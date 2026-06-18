import unittest

import review_runner_lib
import review_types

class ReviewRunnerLibTest(unittest.TestCase):
  def test_perform_review(self):
    review_request = review_types.ReviewRequest("test diff", "test title", "test description")
    review_responses = review_runner_lib.perform_review(review_request)
    self.assertEqual(review_responses, [review_types.ReviewResponse(["Hello World!"], [])])
