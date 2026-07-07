import unittest

import agents.hello_world_agent
import review_runner_lib
import review_types


class ReviewRunnerLibTest(unittest.TestCase):
    def test_perform_review(self):
        review_request = review_types.ReviewRequest(
            "test diff", "test title", "test description"
        )
        review_responses = review_runner_lib.perform_review(
            review_request, [agents.hello_world_agent.HelloWorldAgent()]
        )
        self.assertEqual(
            review_responses, [review_types.ReviewResponse(["Hello World!"], [])]
        )
