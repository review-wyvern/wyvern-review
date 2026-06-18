import agents.agent_base
import review_types

class HelloWorldAgent(agents.agent_base.AgentBase):
  def perform_review(self, review_request: review_types.ReviewRequest) -> review_types.ReviewResponse:
    response = review_types.ReviewResponse([], [])
    response.summary_comments.append("Hello World!")
    return response
  
  def should_run(self, review_request: review_types.ReviewRequest) -> bool:
    return True
