import concurrent.futures
import unittest

import agent_base
import dependency
import dependency_manager
import review_types


class DummyAgent(agent_base.AgentBase):
    def __init__(
        self,
        events_list: list[str],
        name: str,
        dependencies: list[dependency.Dependency] = [],
    ):
        self._events_list = events_list
        self._name = name
        self._dependencies = dependencies

    def perform_review(
        self, review_request: review_types.ReviewRequest
    ) -> review_types.ReviewResponse:
        self._events_list.append(f"ran review for {self._name}")
        return review_types.ReviewResponse([], [])

    def should_run(self, review_request: review_types.ReviewRequest) -> bool:
        return True

    def get_dependencies(self):
        return self._dependencies


class DummyDependency(dependency.Dependency):
    def __init__(
        self,
        events_list: list[str],
        name: str,
        dependencies: list[dependency.Dependency] = [],
    ):
        self._events_list = events_list
        self._name = name
        self._dependencies = dependencies

    def execute(self):
        self._events_list.append(f"executed dependency for {self._name}")

    def get_dependencies(self):
        return self._dependencies

    def merge_from(self, other):
        pass


class DummyDependencyFoo(DummyDependency):
    pass


class DummyAgentFoo(DummyAgent):
    pass


class DependencyManagerTest(unittest.TestCase):
    def test_single_agent_no_deps(self):
        events_list = []
        agents_to_run = [DummyAgent(events_list, "DummyAgent")]
        with concurrent.futures.ThreadPoolExecutor() as executor:
            deps_manager = dependency_manager.DependencyManager(agents_to_run, executor)
            for agent_to_run in deps_manager.get_agents_to_run():
                agent_to_run.perform_review(review_types.ReviewRequest("", "", ""))
        self.assertEqual(events_list, ["ran review for DummyAgent"])

    def test_single_agent_single_dep(self):
        events_list = []
        agents_to_run = [
            DummyAgent(
                events_list, "DummyAgent", [DummyDependency(events_list, "DummyDep")]
            )
        ]
        with concurrent.futures.ThreadPoolExecutor() as executor:
            deps_manager = dependency_manager.DependencyManager(agents_to_run, executor)
            for agent_to_run in deps_manager.get_agents_to_run():
                agent_to_run.perform_review(review_types.ReviewRequest("", "", ""))
        self.assertEqual(
            events_list,
            ["executed dependency for DummyDep", "ran review for DummyAgent"],
        )

    def test_single_agent_multiple_deps(self):
        events_list = []
        agents_to_run = [
            DummyAgent(
                events_list,
                "DummyAgent",
                [
                    DummyDependency(events_list, "DummyDepA"),
                    DummyDependencyFoo(events_list, "DummyDepB"),
                ],
            )
        ]
        with concurrent.futures.ThreadPoolExecutor() as executor:
            deps_manager = dependency_manager.DependencyManager(agents_to_run, executor)
            for agent_to_run in deps_manager.get_agents_to_run():
                agent_to_run.perform_review(review_types.ReviewRequest("", "", ""))
        self.assertCountEqual(
            events_list[:2],
            ["executed dependency for DummyDepA", "executed dependency for DummyDepB"],
        )
        self.assertEqual(events_list[2:], ["ran review for DummyAgent"])

    def test_multiple_agents_one_dep(self):
        events_list = []
        agents_to_run = [
            DummyAgent(
                events_list, "DummyAgent", [DummyDependency(events_list, "DummyDep")]
            ),
            DummyAgentFoo(
                events_list, "DummyAgentFoo", [DummyDependency(events_list, "DummyDep")]
            ),
        ]
        with concurrent.futures.ThreadPoolExecutor() as executor:
            deps_manager = dependency_manager.DependencyManager(agents_to_run, executor)
            for agent_to_run in deps_manager.get_agents_to_run():
                agent_to_run.perform_review(review_types.ReviewRequest("", "", ""))
        self.assertEqual(events_list[0], "executed dependency for DummyDep")
        self.assertCountEqual(
            events_list[1:],
            ["ran review for DummyAgent", "ran review for DummyAgentFoo"],
        )

    def test_multiple_agents_multiple_distinct_deps(self):
        events_list = []
        agents_to_run = [
            DummyAgent(
                events_list, "DummyAgent", [DummyDependency(events_list, "DummyDep")]
            ),
            DummyAgentFoo(
                events_list,
                "DummyAgentFoo",
                [DummyDependencyFoo(events_list, "DummyDepFoo")],
            ),
        ]
        with concurrent.futures.ThreadPoolExecutor() as executor:
            deps_manager = dependency_manager.DependencyManager(agents_to_run, executor)
            for agent_to_run in deps_manager.get_agents_to_run():
                agent_to_run.perform_review(review_types.ReviewRequest("", "", ""))
        self.assertEqual(len(events_list), 4)
        print(events_list)
        self.assertLess(
            events_list.index("executed dependency for DummyDep"),
            events_list.index("ran review for DummyAgent"),
        )
        self.assertLess(
            events_list.index("executed dependency for DummyDepFoo"),
            events_list.index("ran review for DummyAgentFoo"),
        )

    def test_single_agent_two_layer_dep(self):
        events_list = []
        agents_to_run = [
            DummyAgent(
                events_list,
                "DummyAgent",
                [
                    DummyDependency(
                        events_list,
                        "DummyDep",
                        [DummyDependencyFoo(events_list, "DummyDepFoo")],
                    )
                ],
            )
        ]
        with concurrent.futures.ThreadPoolExecutor() as executor:
            deps_manager = dependency_manager.DependencyManager(agents_to_run, executor)
            for agent_to_run in deps_manager.get_agents_to_run():
                agent_to_run.perform_review(review_types.ReviewRequest("", "", ""))
        self.assertEqual(
            events_list,
            [
                "executed dependency for DummyDepFoo",
                "executed dependency for DummyDep",
                "ran review for DummyAgent",
            ],
        )
