# Validate configuration

from attr import dataclass

CONFIG_NAMESPACE = "linode"

@dataclass
class LinodeProvisionerConfig():
	access_token: str
	linode_type: str
	linode_image: str
	linode_label: str
	linode_region: str

	def __str__(self):
		return self.__repr__().replace(self.access_token, "******")
	