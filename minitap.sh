#!/bin/bash

set -eu

# Find devices connected via TCP/IP
tcp_devices=($(adb devices | grep -E -o '([0-9]{1,3}(\.[0-9]{1,3}){3}:[0-9]+)' | sort -u))

if [ ${#tcp_devices[@]} -gt 0 ]; then
    if [ ${#tcp_devices[@]} -eq 1 ]; then
        # If one TCP/IP device is found, use it
        device_ip=${tcp_devices[0]}
        echo "Device already in TCP/IP mode: $device_ip"
    else
        # If multiple TCP/IP devices are found, prompt user to select one
        echo "Multiple devices found. Please select one:"
        for i in "${!tcp_devices[@]}"; do
            echo "[$((i+1))] ${tcp_devices[$i]}"
        done

        read -p "Enter number: " selection
        # Validate that the selection is a number and within the valid range
        if [[ "$selection" =~ ^[0-9]+$ ]] && [ "$selection" -gt 0 ] && [ "$selection" -le "${#tcp_devices[@]}" ]; then
            index=$((selection-1))
            device_ip=${tcp_devices[$index]}
        else
            echo "Invalid selection." >&2
            exit 1
        fi
    fi
else
    # If no TCP/IP devices found, get IP and connect
    echo "No device in TCP/IP mode, enabling..."
    ADB_COMMAND="ip addr show wlan0 | grep 'inet ' | awk '{print \$2}' | cut -d/ -f1"
    device_ip_only=$(adb shell "$ADB_COMMAND" | tr -d '\r\n')
    if [ -z "$device_ip_only" ]; then
        echo "Error: Could not get device IP. Is a device connected via USB and on the same Wi-Fi network?" >&2
        exit 1
    fi
    adb tcpip 5555
    device_ip="${device_ip_only}:5555"
fi

echo "Device IP is: $device_ip"
export ADB_CONNECT_ADDR="$device_ip"

docker compose run --build --rm --remove-orphans -it mobile-use-full-ip "$@"
