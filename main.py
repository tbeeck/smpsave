import configparser
import sys

import servermanager


def main():
    config = configparser.ConfigParser()
    config.read("config.ini")
    server_config = servermanager.LinodeProvisionerConfig(**config["linode"])
    print(server_config)


if __name__ == '__main__':
    main()
