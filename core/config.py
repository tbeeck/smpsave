from attr import dataclass

CORE_CONFIG_NAMESPACE = "core"


@dataclass
class CoreConfig():
    local_server_dir: str
    remote_server_dir: str
    remote_server_user: str
