from abc import ABC, abstractmethod
from typing import Callable, Optional


class Provisioner(ABC):
    """ Abstract class for provisioner implementations. """

    @abstractmethod
    def start(self):
        """ Start the server. This method should:
                - Block until the instance is provisioned.
                - Run post-start lifecycle hooks (post-start)
        """
        pass

    @abstractmethod
    def stop(self, force: bool = False):
        """ Stop and deprovision the server, such that billing is not accrued.
                force: if True, skips running lifecycle hooks and deprovisions the server.
        """
        pass

    @abstractmethod
    def get_host(self) -> Optional[str]:
        """ Return the IP address of the provisioned host,
                or None if the server has not been provisioned
        """
        pass

    @abstractmethod
    def run_poststart_hooks(self):
        """ Run the post-start lifecycle hooks. """
        pass

    @abstractmethod
    def run_prestop_hooks(self):
        """ Run the pre-stop lifecycle hooks. """
        pass

    @abstractmethod
    def set_poststart_hooks(self, hooks: list[Callable]):
        """ Register post-start hooks. """
        pass

    @abstractmethod
    def set_prestop_hooks(self, hooks: list[Callable]):
        """ Register pre-stop hooks. """
        pass
