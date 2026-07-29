from dataclasses import dataclass

from smpsave.configuration import BaseConfig

CORE_CONFIG_NAMESPACE = "core"


@dataclass
class CoreConfig(BaseConfig):
    """
    CoreConfig contains central configuration values for the application.
    """

    provisioner: str
    """ User's choice of provisioner backend. """

    local_server_dir: str
    """
    Path to the local directory containing the game server files.
    This must also be the root directory for the server lifecycle scripts.
    """

    remote_server_dir: str
    """
    The directory in the game server's filesystem that the local server files
    should be synced to. Include a trailing slash.
    """

    remote_server_user: str = "root"
    """
    Username to use when connecting to the game server.
    """

    server_bootstrap: str = "bootstrap.sh"
    """
    Path to the 'bootstrap' server lifecycle script.
    Must be relative to local_server_dir.
    """

    server_entry_point: str = "start.sh"
    """
    Path to the 'start' server lifecycle script.
    Must be relative to local_server_dir.
    """

    server_graceful_stop: str = "stop.sh"
    """
    Path to the 'stop' server lifecycle script.
    Must be relative to local_server_dir.
    """

    ssh_private_key_path: str = "~/.ssh/id_ed25519"
    """
    Path to the private key used to authenticate SSH sessions with the game
    server, passed explicitly via 'ssh -i'. Point this at wherever the key is
    mounted so it need not live at the default '~/.ssh/id_*' location.
    """

    ssh_known_hosts_path: str = "/dev/null"
    """
    Path used for SSH's UserKnownHostsFile. Defaults to '/dev/null' so the
    ephemeral game server's host key is never persisted and the app never needs
    a writable '~/.ssh'. Point this at a real, writable file if you want
    trust-on-first-use pinning across connections.
    """

    ssh_strict_host_key_checking: str = "accept-new"
    """
    Value for SSH's StrictHostKeyChecking option. 'accept-new' accepts the host
    key on first contact without prompting, which suits a freshly provisioned
    server that gets a new host key each time.
    """
