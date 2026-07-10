import concurrent.futures

import agents.agent_registry
import agents.agent_base
import agents.dependency_manager
import review_types


def perform_review(
    review_request: review_types.ReviewRequest,
    agents_to_run: list[agents.agent_base.AgentBase] | None = None,
) -> list[review_types.ReviewResponse]:
    if agents_to_run is None:
        agents_to_run = agents.agent_registry.get_agents_for_request(review_request)
    review_futures = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        deps_manager = agents.dependency_manager.DependencyManager(
            agents_to_run, executor
        )
        for agent_to_run in deps_manager.get_agents_to_run():
            review_futures.append(
                executor.submit(agent_to_run.perform_review, review_request)
            )
    return [review_future.result() for review_future in review_futures]
