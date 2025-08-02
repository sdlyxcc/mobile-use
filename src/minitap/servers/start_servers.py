import signal
import sys
import time
from typing import Optional

import requests
from colorama import Fore, Style, init

from minitap.servers.device_hardware_bridge import DeviceHardwareBridge
from minitap.servers.device_screen_api import start as start_device_screen_api

# Initialize colorama for Windows compatibility
init(autoreset=True)

# Global variables for graceful shutdown
running_processes = []
bridge_instance = None
shutdown_requested = False


# Colored logging functions
def log_info(message: str) -> None:
    """Print info message in blue."""
    print(f"{Fore.BLUE}ℹ {message}{Style.RESET_ALL}")


def log_success(message: str) -> None:
    """Print success message in green."""
    print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")


def log_error(message: str) -> None:
    """Print error message in red."""
    print(f"{Fore.RED}❌ {message}{Style.RESET_ALL}")


def log_warning(message: str) -> None:
    """Print warning message in yellow."""
    print(f"{Fore.YELLOW}⚠ {message}{Style.RESET_ALL}")


def log_header(message: str) -> None:
    """Print header message in cyan with separator."""
    separator = "=" * 60
    print(f"{Fore.CYAN}{separator}")
    print(f"{message}")
    print(f"{separator}{Style.RESET_ALL}")


def check_device_screen_api_health(port=9998, max_retries=30, delay=1):
    health_url = f"http://localhost:{port}/health-check"

    for attempt in range(max_retries):
        try:
            response = requests.get(health_url, timeout=3)
            if response.status_code == 200:
                log_success(f"Device Screen API is healthy on port {port}")
                return True
        except requests.exceptions.RequestException:
            pass

        if attempt == 0:
            log_info(f"Waiting for Device Screen API to become healthy on port {port}...")

        time.sleep(delay)

    log_error(f"Device Screen API failed to become healthy after {max_retries} attempts")
    return False


def start_device_hardware_bridge() -> Optional[DeviceHardwareBridge]:
    log_info("Starting Device Hardware Bridge...")

    try:
        bridge = DeviceHardwareBridge()
        success = bridge.start()

        if success:
            log_success("Device Hardware Bridge started successfully")
            return bridge
        else:
            log_error("Failed to start Device Hardware Bridge")
            return None

    except Exception as e:
        log_error(f"Error starting Device Hardware Bridge: {e}")
        return None


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully using the same stop functions as stop_servers.py."""
    global shutdown_requested
    
    log_warning("\nShutdown signal received. Gracefully stopping servers...")
    shutdown_requested = True
    
    # Use the same unified stop function as stop_servers.py for consistency
    try:
        from minitap.servers.stop_servers import stop_all_servers
        
        # Stop both services using the same reliable functions
        api_stopped, bridge_stopped = stop_all_servers(quiet=True)
        
        if api_stopped and bridge_stopped:
            log_success("All servers stopped gracefully")
        elif api_stopped:
            log_warning("Device Screen API stopped, but Device Hardware Bridge had issues")
        elif bridge_stopped:
            log_warning("Device Hardware Bridge stopped, but Device Screen API had issues")
        else:
            log_error("Failed to stop both servers gracefully")
            
    except ImportError as e:
        log_error(f"Could not import stop_servers module: {e}")
        # Fallback to basic stopping
        if bridge_instance:
            try:
                bridge_instance.stop()
                log_success("Device Hardware Bridge stopped (fallback)")
            except Exception as e:
                log_error(f"Error stopping bridge: {e}")
    except Exception as e:
        log_error(f"Error during graceful shutdown: {e}")
    
    sys.exit(0)


def cleanup_existing_servers():
    """Stop any existing servers to ensure clean startup."""
    log_info("Checking for existing servers...")
    
    # Use the same unified stop function for consistency
    try:
        from minitap.servers.stop_servers import stop_all_servers
        
        # Try to stop existing servers (quietly to avoid duplicate headers)
        api_stopped, bridge_stopped = stop_all_servers(quiet=True)
        
        if api_stopped or bridge_stopped:
            log_success("Cleaned up existing servers")
        else:
            log_info("No existing servers found")
            
    except ImportError as e:
        log_warning(f"Could not import stop_servers module: {e}")
    except Exception as e:
        log_warning(f"Error during cleanup: {e}")


def main():
    global bridge_instance, running_processes
    
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    log_header("Starting Mobile-Use Servers")
    
    # Clean up any existing servers first
    cleanup_existing_servers()

    # Start Device Hardware Bridge
    bridge_instance = start_device_hardware_bridge()
    if not bridge_instance:
        log_warning("Failed to start Device Hardware Bridge. API will continue running.")
        log_info("You can try starting the bridge manually later.")

    # Start Device Screen API
    log_info("Starting Device Screen API...")
    api_process = start_device_screen_api()
    if not api_process:
        log_error("Failed to start Device Screen API. Exiting.")
        sys.exit(1)
    
    running_processes.append(api_process)

    if not check_device_screen_api_health():
        log_error("Device Screen API health check failed. Stopping...")
        api_process.terminate()
        sys.exit(1)

    log_success("Device Screen API listening on port 9998")

    # Display server status
    log_header("Server Status")
    if bridge_instance:
        log_success("Both servers are running successfully:")
        log_info("- Device Screen API: http://localhost:9998")
        log_info("- Maestro Studio: http://localhost:9999")
    else:
        log_warning("Device Screen API is running, but Hardware Bridge failed to start:")
        log_info("- Device Screen API: http://localhost:9998")

    log_info("\nPress Ctrl+C to stop all servers...")

    try:
        while not shutdown_requested:
            time.sleep(1)

            if api_process.poll() is not None:
                log_error("Device Screen API process has stopped unexpectedly")
                break

    except KeyboardInterrupt:
        # This will be handled by the signal handler
        pass


if __name__ == "__main__":
    main()
