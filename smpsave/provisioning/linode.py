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
    Linode access token. Must provide read/write access to Linodes.
    May be overridden at runtime by the LINODE_TOKEN environment variable.
    """

    linode_type: str
    """
    String identifying the Linode type to provision. Consult Linode's API
    documentation for a complete list of options.
    """

    linode_image: str
    """
    String identifying the image to use for the provisioned Linode.
    Consult Linode's documentation for a complete list of options.
    """

    linode_label: str
    """
    A *unique* label to identify the Linode provisioned by this application.
    """

    linode_region: str
    """
    The Linode region to deploy the game server to.
    Consult Linode's documentation for a complete list of options.
    """

    public_key_path: str
    """
    Path to the public key on this system which the provisioned Linode should authorize
    for future incoming SSH connections.
    """

    def populate_from_env(self):
        token = os.getenv("LINODE_TOKEN")
        if token:
            self.access_token = token

    def __str__(self):
        return self._redact(self.access_token)


POLL_TIMEOUT_SECONDS = 300
POLL_INTERVAL_SECONDS = 5


class LinodeProvisioner(Provisioner):
    config: LinodeProvisionerConfig
    client: LinodeClient
    poststart_hooks: list[Callable] = []
    prestop_hooks: list[Callable] = []

    def __init__(self, config: LinodeProvisionerConfig):
        self.config = config
        log.debug(f"Initializing LinodeProvisioner with config: {config}")
        if not config.linode_image:
            log.warning(
                "No 'linode_image' configured. Linode will provision an instance "
                "with no image, which cannot be booted or connected to over SSH."
            )
        self.client = LinodeClient(self.config.access_token)

    def start(self):
        existing = self._get_instance()
        if existing:
            log.info("Instance already exists, skipping provision step")
            log.debug(
                f"Existing instance id={existing.id}, "
                f"status={existing.status}, ipv4={existing.ipv4}"
            )
            return
        log.info("Starting instance")
        log.debug(
            f"instance_create ltype={self.config.linode_type}, "
            f"region={self.config.linode_region}, "
            f"image={self.config.linode_image!r}, "
            f"label={self.config.linode_label}, "
            f"authorized_keys={[self.config.public_key_path]}"
        )
        result = self.client.linode.instance_create(
            ltype=self.config.linode_type,
            region=self.config.linode_region,
            image=self.config.linode_image,
            label=self.config.linode_label,
            authorized_keys=[self.config.public_key_path],
        )
        # instance_create returns a bare Instance when no image is requested,
        # and (Instance, root_password) when one is.
        if isinstance(result, tuple):
            instance = result[0]
        else:
            instance = result
            log.warning(
                "Linode returned an instance with no root password, which means "
                "it was created without an image. Check 'linode_image' in your "
                "configuration."
            )
        log.info(f"Instance id: {instance.id}")
        log.debug(
            f"Created instance status={instance.status}, "
            f"ipv4={instance.ipv4}, region={instance.region}"
        )
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
        log.debug(
            f"Deleting instance id={instance.id}, "
            f"label={instance.label}, status={instance.status}"
        )
        result = instance.delete()
        if not result:
            raise Exception(f"Failed to delete linode instance {instance.label}")
        self._poll_until_instance_stopped()
        log.info("Instance stoped successfully")

    def get_host(self) -> Optional[str]:
        instance = self._get_instance()
        if not instance:
            log.debug("get_host: no instance found")
            return None
        log.debug(f"get_host: instance id={instance.id} has ipv4={instance.ipv4}")
        if len(instance.ipv4) < 1:
            raise Exception("No public IP found for instance")
        return instance.ipv4[0]

    def run_poststart_hooks(self):
        self._run_hooks("post-start", self.poststart_hooks)

    def run_prestop_hooks(self):
        self._run_hooks("pre-stop", self.prestop_hooks)

    def _run_hooks(self, stage: str, hooks: list[Callable]):
        log.debug(
            f"Running {len(hooks)} {stage} hook(s): {[hook.__name__ for hook in hooks]}"
        )
        current = "<none>"
        try:
            for hook in hooks:
                current = hook.__name__
                log.info(f"Running {stage} hook {current}")
                start = time.time()
                hook()
                log.debug(
                    f"{stage} hook {current} finished in {time.time() - start:.1f}s"
                )
        except Exception as e:
            log.exception(f"{stage} hook '{current}' failed")
            raise Exception(f"{stage} hook failed", e)

    def set_poststart_hooks(self, hooks: list[Callable]):
        log.debug(f"Registering post-start hooks: {[hook.__name__ for hook in hooks]}")
        self.poststart_hooks = hooks

    def set_prestop_hooks(self, hooks: list[Callable]):
        log.debug(f"Registering pre-stop hooks: {[hook.__name__ for hook in hooks]}")
        self.prestop_hooks = hooks

    def _poll_until_instance_stopped(self) -> bool:
        timeout_time = time.time() + POLL_TIMEOUT_SECONDS
        while self._get_instance():
            remaining = timeout_time - time.time()
            log.debug(
                f"Instance still present, waiting for deletion "
                f"({remaining:.0f}s until timeout)"
            )
            if time.time() > timeout_time:
                raise Exception("Timeout waiting for instance to be deleted")
            time.sleep(POLL_INTERVAL_SECONDS)
        return True

    def _poll_until_instance_ready(self, instance: Instance) -> bool:
        log.debug(f"Polling until instance ready, current status: {instance.status}")
        timeout_time = time.time() + POLL_TIMEOUT_SECONDS
        while instance.status != "running":
            remaining = timeout_time - time.time()
            log.debug(
                f"Instance status is '{instance.status}' "
                f"({remaining:.0f}s until timeout)"
            )
            if time.time() > timeout_time:
                raise Exception("Timeout waiting for instance to be ready")
            time.sleep(POLL_INTERVAL_SECONDS)
        log.debug(f"Instance reported ready, ipv4={instance.ipv4}")
        return True

    def _get_instance(self) -> Optional[Instance]:
        instances = self.client.linode.instances(
            Instance.label == self.config.linode_label
        )
        for instance in instances:
            if instance.label == self.config.linode_label:
                return instance
        log.debug(f"No instance matched label '{self.config.linode_label}'")
        return None
