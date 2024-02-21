#!/usr/bin/env bash

HOST="$1"
rsync -av \
		--exclude '.mypy-cache/' \
		--exclude 'venv/' \
		--exclude '.git/' \
		--exclude 'sync/' \
		./ root@$HOST:~/minecraft/
