import logging
import time
from typing import Optional

from linode_api4 import Instance, IPAddress, LinodeClient  # type: ignore

from servermanager.config import LinodeProvisionerConfig

log = logging.getLogger(__name__)


# Set up / tear down the linode

# Standup steps:
# 1. Call linode API to provision linode
# 2. Wait for linode to be ready
# 3. Rsync server files
# 4. Run entry point
# 5. Check server started healthily?

# Shutdown steps:
# 1. Run shutoff script (graceful shutdown of server)
# 2. Rsync files back to local directory
# 3. Linode API to delete linode

POLL_TIMEOUT_SECONDS = 100
POLL_INTERVAL_SECONDS = 5


class LinodeProvisioner():

    config: LinodeProvisionerConfig
    client: LinodeClient

    def __init__(self, config: LinodeProvisionerConfig):
        self.config = config
        self.config.update_from_env()
        self.client = LinodeClient(self.config.access_token)

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
        return instance

    def _poll_until_instance_ready(self, instance: Instance) -> bool:
        log.debug(f"Polling until instance ready: {instance.status}")
        timeout_time = time.time() + POLL_TIMEOUT_SECONDS
        while instance.status != "running":
            if time.time() > timeout_time:
                raise Exception("Timeout waiting for instance to be ready")
            time.sleep(POLL_INTERVAL_SECONDS)
        return True

    def stop(self):
        """ Stop the gameserver linode """
        instance = self.get_instance()
        if not instance:
            log.info("No instance found, skipping stop step.")
            return
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
        return True

    def get_instance(self) -> Optional[Instance]:
        instances = self.client.linode.instances(
            Instance.label == self.config.linode_label
        )
        for instance in instances:
            if instance.label == self.config.linode_label:
                return instance
        return None
