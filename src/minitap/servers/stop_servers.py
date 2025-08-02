#!/usr/bin/env python3
"""
Stop all Mobile-Use servers gracefully.

This script ensures that both the Device Screen API and Device Hardware Bridge
are properly stopped, even if they were started separately or if the main
start_servers.py process was terminated unexpectedly.
"""

import sys
import time
from typing import List

import psutil
import requests
from colorama import Fore, Style, init

# Initialize colorama for Windows compatibility
init(autoreset=True)


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


def find_processes_by_name(name: str) -> List[psutil.Process]:
    """Find all processes with the given name."""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if name.lower() in proc.info['name'].lower():
                processes.append(proc)
            elif proc.info['cmdline'] and any(name in cmd for cmd in proc.info['cmdline']):
                processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return processes


def find_processes_by_port(port: int) -> List[psutil.Process]:
    """Find all processes listening on the given port."""
    processes = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            # Use net_connections() instead of deprecated connections()
            for conn in proc.net_connections():
                if conn.laddr.port == port and conn.status == psutil.CONN_LISTEN:
                    processes.append(proc)
                    break
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return processes


def stop_process_gracefully(process: psutil.Process, timeout: int = 5) -> bool:
    """Stop a process gracefully with timeout."""
    try:
        # Check if process still exists before attempting to stop it
        if not process.is_running():
            log_success(f"Process {process.pid} ({process.name()}) already terminated")
            return True
            
        log_info(f"Stopping process {process.pid} ({process.name()})")
        
        # Try graceful termination first
        process.terminate()
        
        # Wait for process to terminate
        try:
            process.wait(timeout=timeout)
            log_success(f"Process {process.pid} terminated gracefully")
            return True
        except psutil.TimeoutExpired:
            log_warning(f"Process {process.pid} didn't terminate gracefully, force killing...")
            try:
                process.kill()
                process.wait(timeout=2)
                log_success(f"Process {process.pid} force killed")
                return True
            except psutil.NoSuchProcess:
                log_success(f"Process {process.pid} already terminated during force kill")
                return True
            
    except psutil.NoSuchProcess:
        log_success(f"Process {process.pid} no longer exists (already terminated)")
        return True
    except (psutil.AccessDenied, psutil.ZombieProcess) as e:
        log_warning(f"Cannot stop process {process.pid}: {e}")
        return False
    except Exception as e:
        log_error(f"Unexpected error stopping process {process.pid}: {e}")
        return False


def check_service_health(port: int, service_name: str) -> bool:
    """Check if a service is still running on the given port."""
    try:
        if port == 9998:
            response = requests.get(f"http://localhost:{port}/health-check", timeout=2)
        elif port == 9999:
            response = requests.get(f"http://localhost:{port}/api/banner-message", timeout=2)
        else:
            return False
            
        if response.status_code == 200:
            log_warning(f"{service_name} is still responding on port {port}")
            return True
    except requests.exceptions.RequestException:
        pass
    
    return False


def stop_device_screen_api() -> bool:
    """Stop the Device Screen API (port 9998)."""
    log_info("Stopping Device Screen API...")
    
    # Check if service is running
    if not check_service_health(9998, "Device Screen API"):
        log_success("Device Screen API is not running")
        return True
    
    # Find processes by port
    processes = find_processes_by_port(9998)
    
    # Also find by process name/command
    uvicorn_processes = find_processes_by_name("uvicorn")
    python_processes = find_processes_by_name("device_screen_api.py")
    
    all_processes = list(set(processes + uvicorn_processes + python_processes))
    
    if not all_processes:
        log_warning("No Device Screen API processes found, but service is still responding")
        # Still try to verify if service actually stops
        time.sleep(1)
        if not check_service_health(9998, "Device Screen API"):
            log_success("Device Screen API stopped successfully (was orphaned)")
            return True
        return False
    
    # Stop all processes
    for proc in all_processes:
        stop_process_gracefully(proc)
    
    # Verify service is stopped
    time.sleep(1)
    if check_service_health(9998, "Device Screen API"):
        log_error("Device Screen API is still running after stop attempt")
        return False
    
    log_success("Device Screen API stopped successfully")
    return True


def stop_device_hardware_bridge() -> bool:
    """Stop the Device Hardware Bridge (Maestro Studio on port 9999)."""
    log_info("Stopping Device Hardware Bridge...")
    
    # Check if service is running
    if not check_service_health(9999, "Maestro Studio"):
        log_success("Device Hardware Bridge is not running")
        return True
    
    # Find processes by port
    processes = find_processes_by_port(9999)
    
    # Also find by process name
    maestro_processes = find_processes_by_name("maestro")
    
    all_processes = list(set(processes + maestro_processes))
    
    if not all_processes:
        log_warning("No Device Hardware Bridge processes found, but service is still responding")
        # Still try to verify if service actually stops
        time.sleep(1)
        if not check_service_health(9999, "Maestro Studio"):
            log_success("Device Hardware Bridge stopped successfully (was orphaned)")
            return True
        return False
    
    # Stop all processes
    for proc in all_processes:
        stop_process_gracefully(proc)
    
    # Verify service is stopped
    time.sleep(1)
    if check_service_health(9999, "Maestro Studio"):
        log_error("Device Hardware Bridge is still running after stop attempt")
        return False
    
    log_success("Device Hardware Bridge stopped successfully")
    return True


def stop_all_servers(quiet: bool = False) -> tuple[bool, bool]:
    """Stop all servers and return (api_success, bridge_success).
    
    Args:
        quiet: If True, suppress log output (useful when called from other modules)
    
    Returns:
        Tuple of (api_stopped, bridge_stopped) booleans
    """
    if not quiet:
        log_header("Stopping Mobile-Use Servers")
    
    # Stop both services
    api_success = stop_device_screen_api()
    bridge_success = stop_device_hardware_bridge()
    
    if not quiet:
        # Summary
        log_header("Stop Summary")
        if api_success and bridge_success:
            log_success("All servers stopped successfully")
        elif api_success:
            log_warning("Device Screen API stopped, but Device Hardware Bridge had issues")
        elif bridge_success:
            log_warning("Device Hardware Bridge stopped, but Device Screen API had issues")
        else:
            log_error("Failed to stop both servers")
    
    return api_success, bridge_success


def main():
    """Main function to stop all servers."""
    log_header("Stopping Mobile-Use Servers")
    
    # Stop both services
    api_success = stop_device_screen_api()
    bridge_success = stop_device_hardware_bridge()
    
    # Summary
    log_header("Stop Summary")
    if api_success and bridge_success:
        log_success("All servers stopped successfully")
        return 0
    elif api_success:
        log_warning("Device Screen API stopped, but Device Hardware Bridge had issues")
        return 1
    elif bridge_success:
        log_warning("Device Hardware Bridge stopped, but Device Screen API had issues")
        return 1
    else:
        log_error("Failed to stop both servers")
        return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        log_warning("\nStop operation interrupted by user")
        sys.exit(130)
    except Exception as e:
        log_error(f"Unexpected error: {e}")
        sys.exit(1)
