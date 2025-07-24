import typer
from minitap.services.llm import AVAILABLE_MODELS, AVAILABLE_PROVIDERS


def validate_model_for_provider(provider: str, model: str) -> None:
    """Validate that the model is available for the given provider."""
    if provider not in AVAILABLE_PROVIDERS:
        typer.echo(f"Error: Invalid provider '{provider}'. Available providers: {', '.join(AVAILABLE_PROVIDERS)}")
        raise typer.Exit(code=1)
    
    if model not in AVAILABLE_MODELS[provider]:
        typer.echo(f"Error: Model '{model}' not available for provider '{provider}'.")
        typer.echo(f"Available models for {provider}: {', '.join(AVAILABLE_MODELS[provider])}")
        raise typer.Exit(code=1)


def show_available_models():
    """Display all available models organized by provider."""
    typer.echo("Available models by provider:")
    for provider, models in AVAILABLE_MODELS.items():
        typer.echo(f"\n{provider}:")
        for model in models:
            typer.echo(f"  - {model}")
