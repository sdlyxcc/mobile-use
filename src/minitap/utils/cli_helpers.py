import sys

from rich.console import Console

from minitap.clients.adb_client import adb
from minitap.clients.ios_client import get_ios_devices


def display_device_status(console: Console):
    """Checks for connected devices and displays the status."""
    console.print("\n[bold]📱 Device Status[/bold]")
    devices = adb.device_list()
    if devices:
        console.print("✅ [bold green]Android device(s) connected:[/bold green]")
        for device in devices:
            console.print(f"  - {device.serial}")
    else:
        console.print("❌ [bold red]No Android device found.[/bold red]")
        console.print("Please make sure your emulator is running or a device is connected via USB.")
        command = "emulator -avd <avd_name>"
        if sys.platform not in ["win32", "darwin"]:
            command = f"./{command}"
        console.print(f"You can start an emulator using a command like: [bold]'{command}'[/bold]")
        console.print("[italic]iOS detection coming soon...[/italic]")

    xcrun_available, ios_devices, error_message = get_ios_devices()
    if xcrun_available:
        if ios_devices:
            console.print("✅ [bold green]iOS device(s) connected:[/bold green]")
            for device in ios_devices:
                console.print(f"  - {device}")
        else:
            console.print("❌ [bold red]No iOS device found.[/bold red]")
            console.print(
                "Please make sure your emulator is running or a device is connected via USB."
            )
        return
    console.print(f"❌ [bold red]iOS check failed:[/bold red] {error_message}")
