import abc
import typing


class Dependency(abc.ABC):
    """The dependency base class.

    This class allows implementors to implement the gathering of a dependency
    that an agent may need, such as an LLVM checkout, or an LLVM build.
    If two agents have the same dependency, the dependencies will get merged in
    a manner up to the implementation (e.g., two agents need different targets
    built, but a single Dependency class will handle building all of them).

    A single dependency class should never vary the type of its subdependencies.
    """

    def execute_return_type(self) -> type:
        """Executes the dependency and returns its type.

        This mainly aimed at the dependency manager so that it can keep
        track of which dependency just finished inside of a future.
        """
        self.execute()
        return type(self)

    @abc.abstractmethod
    def execute(self):
        pass

    @abc.abstractmethod
    def get_dependencies(self) -> list[typing.Self]:
        pass

    @abc.abstractmethod
    def merge_from(self, other: typing.Self):
        pass
