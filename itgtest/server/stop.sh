#!/usr/bin/env bash
host="localhost:8000"
curl "$host/shutdown"
while true; do
    response=$(curl -s -o /dev/null -w "%{http_code}" $host)
    if [[ $response != "200" ]]; then
        echo "Server is unreachable. Exiting..."
        exit 0
    fi
    sleep 1
done
