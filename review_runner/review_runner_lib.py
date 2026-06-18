import concurrent.futures

import agents.agent_registry
import review_types

def perform_review(review_request: review_types.ReviewRequest) -> list[review_types.ReviewResponse]:
  agents_to_run = agents.agent_registry.get_agents_for_request(review_request)
  review_futures = []
  with concurrent.futures.ThreadPoolExecutor() as executor:
    for agent_to_run in agents_to_run:
      review_futures.append(executor.submit(agent_to_run.perform_review, review_request))
  return [review_future.result() for review_future in review_futures]
