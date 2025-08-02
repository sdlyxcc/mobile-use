import subprocess
import sys
import time
from pathlib import Path

import requests

from minitap.servers.device_hardware_bridge import DeviceHardwareBridge


def check_device_screen_api_health(port=9998, max_retries=30, delay=1):
    health_url = f"http://localhost:{port}/health-check"

    for attempt in range(max_retries):
        try:
            response = requests.get(health_url, timeout=3)
            if response.status_code == 200:
                print(f"✓ Device Screen API is healthy on port {port}")
                return True
        except requests.exceptions.RequestException:
            pass

        if attempt == 0:
            print(f"Waiting for Device Screen API to become healthy on port {port}...")

        time.sleep(delay)

    return False


def start_device_screen_api():
    print("Starting Device Screen API...")

    try:
        current_dir = Path(__file__).parent
        api_script = current_dir / "device_screen_api.py"

        if not api_script.exists():
            print(f"❌ Error: {api_script} not found")
            return None

        process = subprocess.Popen(
            [sys.executable, str(api_script)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(current_dir),
        )

        time.sleep(2)

        if process.poll() is not None:
            stdout, stderr = process.communicate()
            print("❌ Device Screen API failed to start:")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return None

        return process

    except Exception as e:
        print(f"❌ Error starting Device Screen API: {e}")
        return None


def start_device_hardware_bridge():
    print("Starting Device Hardware Bridge...")

    try:
        bridge = DeviceHardwareBridge()

        if not bridge.start():
            print("❌ Failed to start Device Hardware Bridge")
            return None

        max_wait_time = 30
        start_time = time.time()

        while time.time() - start_time < max_wait_time:
            status = bridge.get_status()
            current_status = status["status"]

            if current_status == "running":
                print("✓ Device Hardware Bridge started successfully")
                # Try to extract device ID from output
                output = status.get("output", [])
                device_id = None

                for line in output:
                    if "Running on" in line:
                        device_id = line.split("Running on")[-1].strip()
                        break

                if device_id:
                    print(f"✓ Connected device ID: {device_id}")
                else:
                    print("✓ Device Hardware Bridge is running")

                return bridge

            elif current_status == "no_device":
                print("❌ No running devices found")
                print("   Please connect a device or start an emulator, then try again")
                bridge.stop()
                return None

            elif current_status == "port_in_use":
                print("❌ Port 9999 is already in use")
                print("   Please close the program using this port and try again")
                bridge.stop()
                return None

            elif current_status == "failed":
                print("❌ Device Hardware Bridge failed to start")
                output = status.get("output", [])
                if output:
                    print("   Last output:")
                    for line in output[-5:]:  # Show last 5 lines
                        print(f"   {line}")
                bridge.stop()
                return None

            time.sleep(1)

        print("❌ Device Hardware Bridge startup timed out")
        bridge.stop()
        return None

    except Exception as e:
        print(f"❌ Error starting Device Hardware Bridge: {e}")
        return None


def main():
    print("=" * 60)
    print("Starting Mobile-Use Servers")
    print("=" * 60)
    api_process = start_device_screen_api()
    if not api_process:
        print("❌ Failed to start Device Screen API. Exiting.")
        sys.exit(1)

    if not check_device_screen_api_health():
        print("❌ Device Screen API health check failed. Stopping...")
        api_process.terminate()
        sys.exit(1)

    print("✓ Device Screen API listening on port 9998")

    bridge = start_device_hardware_bridge()
    if not bridge:
        print("❌ Failed to start Device Hardware Bridge. API will continue running.")
        print("   You can try starting the bridge manually later.")

    print("=" * 60)
    print("Server startup complete!")
    print("=" * 60)

    if bridge:
        print("Both servers are running successfully.")
        print("- Device Screen API: http://localhost:9998")
        print("- Maestro Studio: http://localhost:9999")
    else:
        print("Device Screen API is running, but Hardware Bridge failed to start.")
        print("- Device Screen API: http://localhost:9998")

    print("\nPress Ctrl+C to stop all servers...")

    try:
        while True:
            time.sleep(1)

            if api_process.poll() is not None:
                print("❌ Device Screen API process has stopped unexpectedly")
                break

    except KeyboardInterrupt:
        print("\n\nShutting down servers...")

        if bridge:
            print("Stopping Device Hardware Bridge...")
            bridge.stop()

        print("Stopping Device Screen API...")
        api_process.terminate()

        try:
            api_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            print("Force killing Device Screen API...")
            api_process.kill()

        print("All servers stopped.")


if __name__ == "__main__":
    main()
