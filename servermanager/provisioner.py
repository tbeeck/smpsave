import logging
import time
from typing import Callable, Optional

from linode_api4 import Instance, LinodeClient  # type: ignore

from servermanager.config import LinodeProvisionerConfig

log = logging.getLogger(__name__)

POLL_TIMEOUT_SECONDS = 100
POLL_INTERVAL_SECONDS = 5


class LinodeProvisioner():

    config: LinodeProvisionerConfig
    client: LinodeClient
    poststart_hooks: list[Callable]
    prestop_hooks: list[Callable]

    def __init__(self, config: LinodeProvisionerConfig):
        self.config = config
        self.config.update_from_env()
        self.client = LinodeClient(self.config.access_token)
        self.poststart_hooks = []
        self.prestop_hooks = []

    def start(self) -> Instance:
        """ Start the gameserver linode.
            Return the IPv4 address of the new linode.
        """
        if self.get_instance():
            log.info(
                "Instance already exists, skipping provision step")
            return
        instance, _ = self.client.linode.instance_create(
            ltype=self.config.linode_type,
            region=self.config.linode_region,
            image=self.config.linode_image,
            label=self.config.linode_label,
        )
        self._poll_until_instance_ready(instance)
        self._run_poststart_hooks()
        return instance

    def _poll_until_instance_ready(self, instance: Instance) -> bool:
        log.debug(f"Polling until instance ready: {instance.status}")
        timeout_time = time.time() + POLL_TIMEOUT_SECONDS
        while instance.status != "running":
            if time.time() > timeout_time:
                raise Exception("Timeout waiting for instance to be ready")
            time.sleep(POLL_INTERVAL_SECONDS)
        log.info(f"Instance ready, id '{instance.id}'")
        return True

    def stop(self):
        """ Stop the gameserver linode """
        instance = self.get_instance()
        if not instance:
            log.info("No instance found, skipping stop step.")
            return
        self._run_prestop_hooks()
        result = instance.delete()
        if not result:
            raise Exception(
                f"Failed to delete linode instance {instance.label}")
        self._poll_until_instance_stopped()

    def _poll_until_instance_stopped(self) -> bool:
        log.debug(f"Polling until instance is deleted.")
        timeout_time = time.time() + POLL_TIMEOUT_SECONDS
        while self.get_instance():
            if time.time() > timeout_time:
                raise Exception("Timeout waiting for instance to be deleted")
            time.sleep(POLL_INTERVAL_SECONDS)
        log.info(f"Instance shutdown successfully.")
        return True

    def _run_poststart_hooks(self):
        try:
            for hook in self.poststart_hooks:
                hook()
        except Exception as e:
            log.error(f"Post-start hook {hook.__name__} failed: ", e)
            raise Exception("Post start hook failed", e)

    def _run_prestop_hooks(self):
        try:
            for hook in self.prestop_hooks:
                hook()
        except Exception as e:
            log.error(f"Pre-stop hook {hook.__name__} failed: ", e)
            raise Exception("Pre-stop hook failed", e)

    def get_instance(self) -> Optional[Instance]:
        instances = self.client.linode.instances(
            Instance.label == self.config.linode_label
        )
        for instance in instances:
            if instance.label == self.config.linode_label:
                return instance
        return None
