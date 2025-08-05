import multiprocessing
import signal
import sys
import time
from typing import Optional

import requests
import uvicorn

from minitap.servers.device_hardware_bridge import BridgeStatus, DeviceHardwareBridge
from minitap.servers.device_screen_api import DEVICE_SCREEN_API_PORT, app
from minitap.utils.logger import get_server_logger

logger = get_server_logger()

running_processes = []
bridge_instance = None
shutdown_requested = False


def check_device_screen_api_health(port=9998, max_retries=30, delay=1):
    health_url = f"http://localhost:{port}/health-check"

    for attempt in range(max_retries):
        try:
            response = requests.get(health_url, timeout=3)
            if response.status_code == 200:
                logger.success(f"Device Screen API is healthy on port {port}")
                return True
        except requests.exceptions.RequestException:
            pass

        if attempt == 0:
            logger.info(f"Waiting for Device Screen API to become healthy on port {port}...")

        time.sleep(delay)

    logger.error(f"Device Screen API failed to become healthy after {max_retries} attempts")
    return False


def start_device_hardware_bridge() -> Optional[DeviceHardwareBridge]:
    logger.info("Starting Device Hardware Bridge...")

    try:
        bridge = DeviceHardwareBridge()
        success = bridge.start()

        if success:
            logger.success("Device Hardware Bridge started successfully")
            return bridge
        else:
            logger.error("Failed to start Device Hardware Bridge")
            return None

    except Exception as e:
        logger.error(f"Error starting Device Hardware Bridge: {e}")
        return None


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully using the same stop functions as stop_servers.py."""
    global shutdown_requested

    logger.warning("\nShutdown signal received. Gracefully stopping servers...")
    shutdown_requested = True

    try:
        from minitap.servers.stop_servers import stop_all_servers

        api_stopped, bridge_stopped = stop_all_servers(quiet=True)

        if api_stopped and bridge_stopped:
            logger.success("All servers stopped gracefully")
        elif api_stopped:
            logger.warning("Device Screen API stopped, but Device Hardware Bridge had issues")
        elif bridge_stopped:
            logger.warning("Device Hardware Bridge stopped, but Device Screen API had issues")
        else:
            logger.error("Failed to stop both servers gracefully")

    except ImportError as e:
        logger.error(f"Could not import stop_servers module: {e}")
        # Fallback to basic stopping
        if bridge_instance:
            try:
                bridge_instance.stop()
                logger.success("Device Hardware Bridge stopped (fallback)")
            except Exception as e:
                logger.error(f"Error stopping bridge: {e}")
    except Exception as e:
        logger.error(f"Error during graceful shutdown: {e}")

    sys.exit(0)


def cleanup_existing_servers():
    """Stop any existing servers to ensure clean startup."""
    logger.info("Checking for existing servers...")

    try:
        from minitap.servers.stop_servers import stop_all_servers

        api_stopped, bridge_stopped = stop_all_servers(quiet=True)

        if api_stopped or bridge_stopped:
            logger.success("Cleaned up existing servers")
        else:
            logger.info("No existing servers found")

    except ImportError as e:
        logger.warning(f"Could not import stop_servers module: {e}")
    except Exception as e:
        logger.warning(f"Error during cleanup: {e}")


def start_device_screen_api_process():
    """Target function to run uvicorn in a separate process."""
    uvicorn.run(app, host="0.0.0.0", port=DEVICE_SCREEN_API_PORT)


def start_device_screen_api() -> Optional[multiprocessing.Process]:
    """Starts the Device Screen API in a new process."""
    try:
        process = multiprocessing.Process(target=start_device_screen_api_process, daemon=True)
        process.start()
        return process
    except Exception as e:
        logger.error(f"Failed to start Device Screen API process: {e}")
        return None


def start_servers_and_get_device_id() -> Optional[str]:
    """Starts all servers, waits for them to be ready, and returns the device ID."""
    global bridge_instance, running_processes

    cleanup_existing_servers()

    bridge_instance = start_device_hardware_bridge()

    if not bridge_instance:
        logger.warning("Failed to start Device Hardware Bridge. Exiting.")
        logger.info("Note: Device Screen API requires Device Hardware Bridge to function properly.")
        return None

    logger.info("Starting Device Screen API...")
    api_process = start_device_screen_api()
    if not api_process:
        logger.error("Failed to start Device Screen API. Exiting.")
        return None

    running_processes.append(api_process)

    if not check_device_screen_api_health():
        logger.error("Device Screen API health check failed. Stopping...")
        api_process.terminate()
        return None

    logger.success("Device Screen API listening on port 9998")

    logger.info("Waiting for Device Hardware Bridge to connect to a device...")
    while True:
        status_info = bridge_instance.get_status()
        status = status_info.get("status")

        if status == BridgeStatus.RUNNING.value:
            device_id = bridge_instance.get_device_id()
            logger.success(f"Device Hardware Bridge is running. Connected to device: {device_id}")
            return device_id

        failed_statuses = [
            BridgeStatus.NO_DEVICE.value,
            BridgeStatus.FAILED.value,
            BridgeStatus.PORT_IN_USE.value,
        ]
        if status in failed_statuses:
            logger.error(f"Device Hardware Bridge failed to connect. Status: {status}")
            return None

        time.sleep(1)


def main():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    logger.info("\n" + "=" * 50)
    logger.info("Starting mobile-use servers")
    logger.info("=" * 50)

    device_id = start_servers_and_get_device_id()

    if device_id:
        logger.header("Server Status")
        logger.success("Both servers are running successfully:")
        logger.info(f"- Connected Device ID: {device_id}")
        logger.info("- Device Screen API: http://localhost:9998")
        logger.info("- Maestro Studio: http://localhost:9999")
    else:
        logger.warning("Servers did not start correctly or no device was found.")

    logger.info("\nPress Ctrl+C to stop all servers...")

    try:
        while not shutdown_requested:
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except Exception as e:
        logger.error(f"Unexpected error in main loop: {e}")
        pass


if __name__ == "__main__":
    main()
