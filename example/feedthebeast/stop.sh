#!/bin/bash

pid="$(ps aux | grep "forge-1.12.2-14.23.5.2858.jar" | head -1 | tr -s ' ' | cut -d ' ' -f 2)"
echo "Killing process with PID $pid"
kill $pid
sleep 5
