# Shell out to rsync to sync game files in either direction

import subprocess


def rsync(src: str, dst: str) -> int:
    command = ['rsync', '-avz', src, dst]

    try:
        process = subprocess.run(command, check=False)
        return process.returncode
    except subprocess.CalledProcessError as e:
        print(f"Error executing rsync command: {e}")
        return e.returncode
