#!/usr/bin/env bash
cmd="python3 server.py"
exec $cmd &>/dev/null & disown
