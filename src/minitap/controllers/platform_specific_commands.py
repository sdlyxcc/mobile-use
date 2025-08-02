from datetime import date
from typing import Optional

from minitap.clients.adb_client import get_device
from minitap.context import get_device_context
from minitap.utils.cli_helpers import run_shell_command_on_host


def get_focused_app_info() -> Optional[str]:
    context = get_device_context()
    if context.mobile_platform == "IOS":
        return None
    device = get_device()
    result: str = device.shell("dumpsys window | grep -E 'mCurrentFocus|mFocusedApp'")  # type: ignore
    return result


def get_screen_size() -> tuple[int, int]:
    context = get_device_context()
    return context.device_width, context.device_height


def get_date() -> str:
    context = get_device_context()
    if context.mobile_platform == "IOS":
        return date.today().strftime("%a %b %d %H:%M:%S %Z %Y")
    device = get_device()
    result: str = device.shell("date")  # type: ignore
    return result


def list_packages() -> str:
    context = get_device_context()
    if context.mobile_platform == "IOS":
        cmd = ["xcrun", "simctl", "listapps", "booted", "|", "grep", "CFBundleIdentifier"]
        return run_shell_command_on_host(" ".join(cmd))
    else:
        device = get_device()
        cmd = ["pm", "list", "packages", "-f"]
        return device.shell(" ".join(cmd))  # type: ignore
