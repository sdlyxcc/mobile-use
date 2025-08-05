from datetime import date
from typing import Optional

from adbutils import AdbDevice

from minitap.clients.adb_client import adb
from minitap.context import get_device_context
from minitap.utils.cli_helpers import run_shell_command_on_host


def get_adb_device() -> AdbDevice:
    """Get the first available device."""
    devices = adb.device_list()
    if not devices:
        raise ConnectionError("No device found.")
    return devices[0]


def get_first_device_id() -> str:
    """Gets the first available device."""
    android_output = run_shell_command_on_host("adb devices")
    lines = android_output.strip().split("\n")
    for line in lines:
        if "device" in line and not line.startswith("List of devices"):
            return line.split()[0]
    ios_output = run_shell_command_on_host("xcrun simctl list devices booted")
    return ios_output


def get_focused_app_info() -> Optional[str]:
    context = get_device_context()
    if context.mobile_platform == "IOS":
        return None
    device = get_adb_device()
    result: str = device.shell("dumpsys window | grep -E 'mCurrentFocus|mFocusedApp'")  # type: ignore
    return result


def get_screen_size() -> tuple[int, int]:
    context = get_device_context()
    return context.device_width, context.device_height


def get_device_date() -> str:
    context = get_device_context()
    if context.mobile_platform == "IOS":
        return date.today().strftime("%a %b %d %H:%M:%S %Z %Y")
    device = get_adb_device()
    result: str = device.shell("date")  # type: ignore
    return result


def list_packages() -> str:
    context = get_device_context()
    if context.mobile_platform == "IOS":
        cmd = ["xcrun", "simctl", "listapps", "booted", "|", "grep", "CFBundleIdentifier"]
        return run_shell_command_on_host(" ".join(cmd))
    else:
        device = get_adb_device()
        cmd = ["pm", "list", "packages", "-f"]
        return device.shell(" ".join(cmd))  # type: ignore
