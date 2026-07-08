import asyncio
import json

import agents.agent_base
import review_types

from google.adk.models import base_llm
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import pydantic

INSTRUCTIONS = """
You are an expert code review agent. Classify the following patch as trivial or
not. Your final response should consist solely of a single JSON object of the
following form:

{"trivial": <true/false>}

You should take into account the following criteria when making a decision:
1. Trivial refactorings that are obviously beneficial and obviously do not
change behavior can be classified as trivial. Otherwise, they should be
considered non-trivial.
2. Test updates can be considered trivial when someone is either adding
test cases or simply regenerating check lines. Otherwise, test updates
should be considered non-trivial.
3. Build system updates like portings to one of the non-standard build
systems such as bazel or gn should generally considered trivial. Other small
build system changes like adding library dependencies or disabling
warnings can also be considered trivial. Otherwise, build system changes
should be marked as non-trivial.
"""

DEFAULT_MODEL = "gemini-3.1-pro-preview"


class ClassifierAgentOutput(pydantic.BaseModel):
    trivial: bool = pydantic.Field(
        ..., description="Whether or not the commit is trivial."
    )


class ClassifierAgent(agents.agent_base.AgentBase):
    async def classify_diff(self, diff: str, model: base_llm.BaseLlm | str) -> bool:
        classifier_agent = LlmAgent(
            name="classifier",
            description="Classifies commits",
            model=model,
            instruction=INSTRUCTIONS,
            output_schema=ClassifierAgentOutput,
        )
        session_service = InMemorySessionService()
        runner = Runner(
            app_name="classifier",
            agent=classifier_agent,
            session_service=session_service,
        )
        session = await runner.session_service.create_session(
            app_name="classifier", user_id="default_user"
        )
        content = types.Content(
            role="user", parts=[types.Part(text=f"Please review the patch:\n{diff}")]
        )
        is_trivial = False
        async for event in runner.run_async(
            user_id="default_user", session_id=session.id, new_message=content
        ):
            if event.content and event.content.parts:
                message = "\n\n".join(
                    part.text for part in event.content.parts if part.text
                )
                is_trivial = json.loads(message)["trivial"]
        return is_trivial

    def perform_review(
        self,
        review_request: review_types.ReviewRequest,
        model: base_llm.BaseLlm | str = DEFAULT_MODEL,
    ) -> review_types.ReviewResponse:
        is_trivial = asyncio.run(self.classify_diff(review_request.diff, model))
        return review_types.ReviewResponse(
            summary_comments=[
                "This commit is trivial" if is_trivial else "This commit is non-trivial"
            ],
            line_comments=[],
        )

    def should_run(self, review_request: review_types.ReviewRequest) -> bool:
        return True
