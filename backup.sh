#!/usr/bin/env bash

HOST="root@home.timbeck.me"
DIRS=(
    "ftb"
)

for dir in "${DIRS[@]}"; do
    source_dir="$HOST:~/$dir"
    dest_dir="./sync/$dir"
    mkdir -p "$dest_dir"
    echo "Sync from $source_dir to $dest_dir"
    rsync -avz -e ssh "$source_dir" "$dest_dir"
done
