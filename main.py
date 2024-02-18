import configparser
import sys
import servermanager


def main():
    config = configparser.ConfigParser()
    config.read("config.ini")
    server_config = servermanager.LinodeProvisionerConfig(**config["linode"])
    server_config.update_from_env()

    action = sys.argv[1]
    if action == "start":
        pass
    elif action == "stop":
        pass
    else:
        print("unknown action", action)

if __name__ == '__main__':
    main()
