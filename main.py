import configparser
import logging
import sys

from servermanager import LinodeProvisioner, LinodeProvisionerConfig


def main():
    config = configparser.ConfigParser()
    config.read("config.ini")
    server_config = LinodeProvisionerConfig(**config["linode"])

    provisioner = LinodeProvisioner(server_config)

    if len(sys.argv) < 2:
        print("Must provide an action: 'start', 'stop'")

    action = sys.argv[1]
    if action == "start":
        provisioner.start()
    elif action == "stop":
        provisioner.stop()
    elif action == "info":
        print("Instance ready", provisioner.instance_ready())
    else:
        print("unknown action", action)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(module)s  %(message)s')
    main()
