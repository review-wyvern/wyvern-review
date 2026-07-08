import agents.agent_base
import agents.hello_world_agent
import agents.classifier_agent
import review_types

AGENT_REGISTRY = [
    agents.hello_world_agent.HelloWorldAgent,
    agents.classifier_agent.ClassifierAgent,
]


def get_agents_for_request(
    review_request: review_types.ReviewRequest,
) -> list[agents.agent_base.AgentBase]:
    agents_to_run = []
    for registered_agent in AGENT_REGISTRY:
        agent_instance = registered_agent()
        if agent_instance.should_run(review_request):
            agents_to_run.append(agent_instance)
    return agents_to_run
