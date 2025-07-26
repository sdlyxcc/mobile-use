import sys

import typer
from rich.console import Console

from minitap.client.adb import adb
from minitap.constants import AVAILABLE_MODELS


def validate_model_for_provider(provider: str, model: str) -> None:
    """Validate that the model is available for the given provider."""
    if provider not in AVAILABLE_MODELS:
        typer.echo(
            f"Error: Invalid provider '{provider}'.\n"
            f"Available providers: {', '.join(AVAILABLE_MODELS)}"
        )
        raise typer.Exit(code=1)

    if model not in AVAILABLE_MODELS[provider]:
        typer.echo(f"Error: Model '{model}' not available for provider '{provider}'.")
        typer.echo(f"Available models for {provider}: {', '.join(AVAILABLE_MODELS[provider])}")
        raise typer.Exit(code=1)


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


def show_available_models():
    """Display all available models organized by provider."""
    typer.echo("Available models by provider:")
    for provider, models in AVAILABLE_MODELS.items():
        typer.echo(f"\n{provider}:")
        for model in models:
            typer.echo(f"  - {model}")
