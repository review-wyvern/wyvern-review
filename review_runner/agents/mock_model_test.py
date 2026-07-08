import asyncio
import unittest

from google.adk.models import llm_request
from google.adk.models import llm_response
from google.genai import types

import mock_model


class MockModelTest(unittest.TestCase):
    async def get_responses(
        self, response_count: int, model_mock: mock_model.MockModel
    ):
        responses = []
        async for response in model_mock.generate_content_async(None):
            responses.append(response)
            if len(responses) == response_count:
                break
        return responses

    def test_single_response(self):
        model_responses = [
            llm_response.LlmResponse(
                content=types.Content(
                    parts=[types.Part(text="this is invalid json")],
                    role="model",
                )
            )
        ]
        model_mock = mock_model.MockModel(responses=model_responses)
        real_model_responses = asyncio.run(self.get_responses(1, model_mock))
        self.assertEqual(real_model_responses, model_responses)

    def test_not_enough_responses(self):
        model_mock = mock_model.MockModel(responses=[])
        with self.assertRaises(ValueError):
            asyncio.run(self.get_responses(1, model_mock))
