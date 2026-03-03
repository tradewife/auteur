"""AUTEUR CLI — command-line interface for the film/video agent harness."""

from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from auteur import __version__
from auteur.config import get_settings

app = typer.Typer(
    name="auteur",
    help="AUTEUR — deep cinematography knowledge meets multi-API generation.",
    no_args_is_help=True,
)
console = Console()


@app.command()
def version():
    """Show AUTEUR version."""
    console.print(f"AUTEUR v{__version__}")


@app.command()
def status():
    """Show configured providers and API key status."""
    settings = get_settings()

    table = Table(title="AUTEUR Provider Status")
    table.add_column("Provider", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Models")

    table.add_row(
        "FAL",
        "✓ configured" if settings.has_fal else "✗ no key",
        "Flux 2, Nano Banana 2, Veo 3/3.1, Kling 3.0/O3, Sora 2, Grok, Wan 2.6, 1000+",
    )
    table.add_row(
        "Kie.ai",
        "✓ configured" if settings.has_kie else "✗ no key",
        "Veo 3.1, Kling 3.0, Runway Aleph/Gen4, Seedance 1.5, Wan 2.6, Nano Banana, GPT Image",
    )
    table.add_row(
        "Gemini",
        "✓ configured" if settings.has_gemini else "✗ no key",
        "Imagen 4 (Standard/Ultra/Fast), Nano Banana 2, Veo 3",
    )

    console.print(table)


@app.command()
def shot(
    description: str = typer.Argument(help="Natural language description of the shot"),
    style: Optional[str] = typer.Option(None, "--style", "-s", help="DP style profile"),
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="API provider to use"),
    animate: bool = typer.Option(False, "--animate", "-a", help="Animate the generated image"),
):
    """Generate a single cinematic shot from a description."""
    console.print(f"[bold cyan]Composing shot:[/] {description}")
    if style:
        console.print(f"[dim]Style: {style}[/]")
    if provider:
        console.print(f"[dim]Provider: {provider}[/]")
    # TODO: Wire up prompt composer → provider → output
    console.print("[yellow]Shot generation pipeline coming soon.[/]")


@app.command()
def explore():
    """Interactively explore the cinematography knowledge base."""
    from auteur.knowledge import camera, color, composition, lens, lighting, movement

    table = Table(title="AUTEUR Knowledge Base")
    table.add_column("Domain", style="cyan")
    table.add_column("Entries", style="green", justify="right")
    table.add_column("Examples")

    domains = [
        ("Camera Systems", camera.SENSOR_FORMATS, "sensor formats"),
        ("Lenses", lens.FOCAL_LENGTHS, "focal lengths"),
        ("Lighting", lighting.LIGHTING_SETUPS, "named setups"),
        ("Color", color.COLOR_PALETTES, "palette types"),
        ("Composition", composition.COMPOSITION_RULES, "rule systems"),
        ("Movement", movement.CAMERA_MOVEMENTS, "movement types"),
    ]

    for name, collection, desc in domains:
        examples = ", ".join(list(collection.keys())[:3]) + "..."
        table.add_row(name, str(len(collection)), examples)

    console.print(table)


@app.command()
def serve(
    transport: str = typer.Option("stdio", "--transport", "-t", help="Transport: stdio or sse"),
    host: str = typer.Option("127.0.0.1", "--host", help="Host for SSE transport"),
    port: int = typer.Option(8000, "--port", help="Port for SSE transport"),
):
    """Start the AUTEUR MCP server."""
    from auteur.server import mcp

    console.print(f"[bold cyan]AUTEUR MCP Server[/] — transport: {transport}")
    if transport == "sse":
        console.print(f"[dim]Listening on {host}:{port}[/]")
        mcp.run(transport="sse", host=host, port=port)
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    app()
