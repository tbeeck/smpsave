import os

from attr import dataclass

LINODE_CONFIG_NAMESPACE = "linode"


@dataclass
class LinodeProvisionerConfig():
    access_token: str
    linode_type: str
    linode_image: str
    linode_label: str
    linode_region: str
    public_key_path: str

    def populate_from_env(self):
        token = os.getenv("LINODE_TOKEN")
        if token:
            self.access_token = token

    def __str__(self):
        return self.__repr__().replace(self.access_token, "******")
