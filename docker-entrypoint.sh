#!/bin/bash

set -eu

# Trap SIGTERM and SIGINT to kill background processes
trap 'kill $(jobs -p)' SIGTERM SIGINT

if [ ! -z "${ADB_CONNECT_ADDR:-}" ]; then
    while true; do
        output="$(adb connect "$ADB_CONNECT_ADDR" 2>&1)"
        exit_code=$?
        echo $output

        if [[ $exit_code -ne 0 ]]; then
            echo "ADB connect failed with exit code $exit_code"
        elif echo "$output" | grep -qi "unable to connect\|connection refused"; then
            echo "Connection refused or unable to connect detected in ADB output"
        else
            echo "ADB connect successful"
            break
        fi

        echo "ADB connect failed, retrying in 2s..."
        sleep 2
    done
fi

sleep 2

uv run minitap "$@"
