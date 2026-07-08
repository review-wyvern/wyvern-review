import unittest

from google.adk.models import llm_response
from google.genai import types

import classifier_agent
import mock_model
import review_types


class ClassifierAgentTest(unittest.TestCase):
    def test_trivial_commit(self):
        model_mock = mock_model.MockModel(
            responses=[
                llm_response.LlmResponse(
                    content=types.Content(
                        parts=[types.Part(text='{"trivial":true}')],
                        role="model",
                    )
                )
            ]
        )
        agent = classifier_agent.ClassifierAgent()
        review_request = review_types.ReviewRequest(
            diff="test diff", title="test title", description="test description"
        )
        review_response = agent.perform_review(review_request, model_mock)
        self.assertEqual(
            review_response,
            review_types.ReviewResponse(
                summary_comments=["This commit is trivial"], line_comments=[]
            ),
        )

    def test_non_trivial_commit(self):
        model_mock = mock_model.MockModel(
            responses=[
                llm_response.LlmResponse(
                    content=types.Content(
                        parts=[types.Part(text='{"trivial":false}')], role="model"
                    )
                )
            ]
        )
        agent = classifier_agent.ClassifierAgent()
        review_request = review_types.ReviewRequest(
            diff="test diff", title="test title", description="test description"
        )
        review_response = agent.perform_review(review_request, model_mock)
        self.assertEqual(
            review_response,
            review_types.ReviewResponse(
                summary_comments=["This commit is non-trivial"], line_comments=[]
            ),
        )
