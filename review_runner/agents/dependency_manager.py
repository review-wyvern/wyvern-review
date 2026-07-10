import collections
import concurrent.futures
import typing

import agents.agent_base
import dependency


class DependencyManager:
    def __init__(
        self,
        agents_to_run: list[agents.agent_base.AgentBase],
        executor: concurrent.futures.Executor,
    ):
        self._agents_to_run = agents_to_run
        self._dependencies_to_run: dict[
            type, tuple[dependency.Dependency, set[type]]
        ] = {}
        self._agents_to_deps: dict[
            type[agents.agent_base.AgentBase], set[type[dependency.Dependency]]
        ] = {}
        dependencies_to_process = collections.deque()
        for agent_to_run in agents_to_run:
            agent_dependencies = agent_to_run.get_dependencies()
            dependencies_to_process.extend(agent_dependencies)
            self._agents_to_deps[type(agent_to_run)] = [
                type(agent_dependency) for agent_dependency in agent_dependencies
            ]
        while len(dependencies_to_process) > 0:
            dependency_to_process = dependencies_to_process.popleft()
            if type(dependency_to_process) in self._dependencies_to_run:
                canonical_dependency, _ = self._dependencies_to_run[
                    type(dependency_to_process)
                ]
                canonical_dependency.merge_from(dependency_to_process)
            else:
                sub_dependency_types = set(
                    [
                        type(sub_dependency)
                        for sub_dependency in dependency_to_process.get_dependencies()
                    ]
                )
                self._dependencies_to_run[type(dependency_to_process)] = (
                    dependency_to_process,
                    sub_dependency_types,
                )
                dependencies_to_process.extend(dependency_to_process.get_dependencies())
        self._executor = executor

    def get_agents_to_run(
        self,
    ) -> typing.Generator[agents.agent_base.AgentBase, None, None]:
        """Provides all the agents to run.

        This function is a generator that yields the next agent to run when all
        of its dependencies are ready.
        """
        in_progress_dependencies = set()
        while len(self._agents_to_deps) > 0:
            # Execute any dependencies that have no outstanding subdeps.
            newly_running_dependencies = []
            for dependency_type in self._dependencies_to_run:
                dependency_to_run, sub_dependencies = self._dependencies_to_run[
                    dependency_type
                ]
                if len(sub_dependencies) != 0:
                    continue
                in_progress_dependencies.add(
                    self._executor.submit(dependency_to_run.execute_return_type)
                )
                newly_running_dependencies.append(type(dependency_to_run))
            for newly_running_dependency in newly_running_dependencies:
                del self._dependencies_to_run[newly_running_dependency]
            # Yield any agents that do not have any outstanding deps.
            completed_agent_indices = []
            for agent_index, agent_to_run in enumerate(self._agents_to_run):
                agent_deps = self._agents_to_deps[type(agent_to_run)]
                if len(agent_deps) == 0:
                    yield agent_to_run
                    completed_agent_indices.append(agent_index)
                    del self._agents_to_deps[type(agent_to_run)]
            # And then remove them from the list.
            for completed_agent_index in sorted(completed_agent_indices, reverse=True):
                del self._agents_to_run[completed_agent_index]
            # Now we wait for at least one of the dependency futures to complete.
            completed_deps, in_progress_dependencies = concurrent.futures.wait(
                in_progress_dependencies, return_when=concurrent.futures.FIRST_COMPLETED
            )
            # Update the dependencies/agents to note that a dep is now complete.
            for completed_dep in completed_deps:
                completed_dep_type = completed_dep.result()
                for other_dep in self._dependencies_to_run:
                    _, sub_dependencies_set = self._dependencies_to_run[other_dep]
                    if completed_dep_type in sub_dependencies_set:
                        sub_dependencies_set.remove(completed_dep_type)
                for agent_type in self._agents_to_deps:
                    if completed_dep_type in self._agents_to_deps[agent_type]:
                        self._agents_to_deps[agent_type].remove(completed_dep_type)
