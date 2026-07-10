import abc

import dependency
import review_types


class AgentBase(abc.ABC):
    @abc.abstractmethod
    def perform_review(
        self, review_request: review_types.ReviewRequest
    ) -> review_types.ReviewResponse:
        """Performs the review."""
        pass

    @abc.abstractmethod
    def should_run(self, review_request: review_types.ReviewRequest) -> bool:
        """Whether or not to run the agent based on the review request."""
        pass

    def get_dependencies(self) -> list[dependency.Dependency]:
        """The dependencies that this agent needs."""
        return []
