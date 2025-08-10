#!/bin/bash

set -eu

# Trap SIGTERM and SIGINT to kill background processes
trap 'kill $(jobs -p)' SIGTERM SIGINT

if [ ! -z "${ADB_CONNECT_ADDR:-}" ]; then
    adb connect "$ADB_CONNECT_ADDR"
fi

sleep 2

uv run minitap "$@"
