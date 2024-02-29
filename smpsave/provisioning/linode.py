import logging
import os
import time
from dataclasses import dataclass
from typing import Callable, Optional

from linode_api4 import Instance, LinodeClient  # type: ignore

from smpsave.configuration import BaseConfig
from smpsave.provisioning.provisioner import Provisioner

log = logging.getLogger(__name__)

LINODE_CONFIG_NAMESPACE = "linode"


@dataclass
class LinodeProvisionerConfig(BaseConfig):
    access_token: str
    """ 
    Linode access token. Must provide read/write access to linodes.
    May be overriden at runtime by the LINODE_TOKEN environment variable.
    """

    linode_type: str
    """
    String identifying the linode type to provision. Consult linode's API
    documentation for a complete list of options.
    """

    linode_image: str
    """
    String identifying the image to use for the provisioned linode.
    Consult linode's documentation for a complete list of options.
    """

    linode_label: str
    """
    A *unique* label to identify the linode provisioned by this application.
    """

    linode_region: str
    """
    The linode region to deploy the game server to.
    Consult Linode's documentation for a complete list of options.
    """

    public_key_path: str
    """
    Path to the public key on this system which the provisioned linode should authorize
    for future incoming SSH connections.
    """

    def populate_from_env(self):
        token = os.getenv("LINODE_TOKEN")
        if token:
            self.access_token = token

    def __str__(self):
        return self.__repr__().replace(self.access_token, "******")


POLL_TIMEOUT_SECONDS = 300
POLL_INTERVAL_SECONDS = 5


class LinodeProvisioner(Provisioner):

    config: LinodeProvisionerConfig
    client: LinodeClient
    poststart_hooks: list[Callable] = []
    prestop_hooks: list[Callable] = []

    def __init__(self, config: LinodeProvisionerConfig):
        self.config = config
        self.client = LinodeClient(self.config.access_token)

    def start(self):
        if self._get_instance():
            log.info(
                "Instance already exists, skipping provision step")
            return
        log.info("Starting instance")
        instance, _ = self.client.linode.instance_create(
            ltype=self.config.linode_type,
            region=self.config.linode_region,
            image=self.config.linode_image,
            label=self.config.linode_label,
            authorized_keys=[self.config.public_key_path]
        )
        log.info(f"Instance id: {instance.id}")
        self._poll_until_instance_ready(instance)
        log.info("Instance started successfully.")
        self.run_poststart_hooks()
        log.info("Post-start hooks completed.")
        return instance

    def stop(self, force=False):
        instance = self._get_instance()
        if not instance:
            log.info("No instance found, skipping stop step.")
            return
        if not force:
            self.run_prestop_hooks()
            log.info("Pre-stop hooks completed.")
        else:
            log.info("Force stop: skipping pre-stop hooks")
        result = instance.delete()
        if not result:
            raise Exception(
                f"Failed to delete linode instance {instance.label}")
        self._poll_until_instance_stopped()
        log.info("Instance stoped successfully")

    def get_host(self) -> Optional[str]:
        instance = self._get_instance()
        if not instance:
            return None
        if len(instance.ipv4) < 1:
            raise Exception("No public IP found for instance")
        return instance.ipv4[0]

    def run_poststart_hooks(self):
        try:
            for hook in self.poststart_hooks:
                log.info(f"Running post-start hook {hook.__name__}")
                hook()
        except Exception as e:
            log.error(f"Post-start hook '{hook.__name__}' failed: ", e)
            raise Exception("Post start hook failed", e)

    def run_prestop_hooks(self):
        try:
            for hook in self.prestop_hooks:
                log.info(f"Running pre-stop hook {hook.__name__}")
                hook()
        except Exception as e:
            log.error(f"Pre-stop hook ;{hook.__name__}; failed: ", e)
            raise Exception("Pre-stop hook failed", e)

    def set_poststart_hooks(self, hooks: list[Callable]):
        self.poststart_hooks = hooks

    def set_prestop_hooks(self, hooks: list[Callable]):
        self.prestop_hooks = hooks

    def _poll_until_instance_stopped(self) -> bool:
        timeout_time = time.time() + POLL_TIMEOUT_SECONDS
        while self._get_instance():
            if time.time() > timeout_time:
                raise Exception("Timeout waiting for instance to be deleted")
            time.sleep(POLL_INTERVAL_SECONDS)
        return True

    def _poll_until_instance_ready(self, instance: Instance) -> bool:
        log.debug(f"Polling until instance ready: {instance.status}")
        timeout_time = time.time() + POLL_TIMEOUT_SECONDS
        while instance.status != "running":
            if time.time() > timeout_time:
                raise Exception("Timeout waiting for instance to be ready")
            time.sleep(POLL_INTERVAL_SECONDS)
        return True

    def _get_instance(self) -> Optional[Instance]:
        instances = self.client.linode.instances(
            Instance.label == self.config.linode_label
        )
        for instance in instances:
            if instance.label == self.config.linode_label:
                return instance
        return None
