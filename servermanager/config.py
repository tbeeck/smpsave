import os

from attr import dataclass

CONFIG_NAMESPACE = "linode"


@dataclass
class LinodeProvisionerConfig():
    access_token: str
    linode_type: str
    linode_image: str
    linode_label: str
    linode_region: str

    def update_from_env(self):
        if os.getenv("LINODE_TOKEN") != None:
            self.access_token = os.getenv("LINODE_TOKEN")

    def __str__(self):
        return self.__repr__().replace(self.access_token, "******")
