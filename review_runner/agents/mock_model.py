from typing import AsyncGenerator

from google.adk.models import base_llm
from google.adk.models import llm_request
from google.adk.models import llm_response
import pydantic


class MockModel(base_llm.BaseLlm):
    """Mock model for testing."""

    requests: list[llm_request.LlmRequest] = pydantic.Field(default_factory=list)
    responses: list[llm_response.LlmResponse] = pydantic.Field(default_factory=list)
    response_index: int = pydantic.Field(default=0)

    def __init__(self, responses: list[llm_response.LlmResponse]):
        super().__init__(model="mock-model")
        self.responses = responses
        self.response_index = 0

    @classmethod
    def supported_models(cls) -> list[str]:
        return ["mock-model"]

    async def generate_content_async(
        self, request: llm_request.LlmRequest, stream: bool = False
    ) -> AsyncGenerator[llm_response.LlmResponse, None]:
        self.requests.append(request)
        if self.response_index < len(self.responses):
            yield self.responses[self.response_index]
            self.response_index += 1
        else:
            raise ValueError("Ran out of responses.")
