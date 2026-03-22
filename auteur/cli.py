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
def browser_auth(
    platform: str = typer.Argument(help="Platform to authenticate (e.g. grok_imagine)"),
    account: str = typer.Option("default", "--account", "-a", help="Account key"),
    chrome: Optional[str] = typer.Option(None, "--chrome", help="Chrome executable path"),
):
    """Bootstrap browser auth for a platform — opens headed browser for manual login."""
    import asyncio
    from auteur.browser_ops.auth import make_account, bootstrap_auth
    from auteur.browser_ops.platforms import PLATFORM_SPECS

    # Find spec by platform name
    spec = None
    for s in PLATFORM_SPECS.values():
        if s.platform == platform:
            spec = s
            break

    if not spec:
        console.print(f"[red]Unknown platform: {platform}[/]")
        console.print(f"Available: {[s.platform for s in PLATFORM_SPECS.values()]}")
        raise typer.Exit(1)

    acct = make_account(platform, account)
    console.print(f"[bold cyan]Bootstrapping auth[/] for {acct.label}")
    console.print(f"Storage state: {acct.storage_state_path}")

    success = asyncio.run(bootstrap_auth(acct, spec, executable_path=chrome))
    if success:
        console.print("[green]✓ Auth bootstrapped successfully[/]")
    else:
        console.print("[red]✗ Auth bootstrap failed[/]")


@app.command()
def browser_cookies(
    platform: str = typer.Argument(help="Platform to import cookies for (e.g. grok_imagine)"),
    cookie_file: str = typer.Argument(help="Path to cookie JSON file"),
    account: str = typer.Option("default", "--account", "-a", help="Account key"),
    domain: Optional[str] = typer.Option(None, "--domain", "-d", help="Only import cookies matching this domain"),
):
    """Import cookies from a JSON file (gstack-style auth fallback).

    Accepts both Playwright storage_state format and flat cookie arrays
    (browser-use CLI export, Chrome extension exports, etc.).
    """
    from auteur.browser_ops.auth import make_account, import_cookies

    acct = make_account(platform, account)
    console.print(f"[bold cyan]Importing cookies[/] for {acct.label}")
    console.print(f"Source: {cookie_file}")

    try:
        success = import_cookies(acct, cookie_file, domain_filter=domain)
        if success:
            console.print("[green]✓ Cookies imported successfully[/]")
        else:
            console.print("[yellow]No matching cookies found[/]")
    except (FileNotFoundError, ValueError) as e:
        console.print(f"[red]✗ {e}[/]")
        raise typer.Exit(1)


@app.command()
def browser_grab(
    platform: str = typer.Argument(help="Platform to grab cookies for (e.g. grok_imagine)"),
    account: str = typer.Option("default", "--account", "-a", help="Account key"),
    chrome_profile: str = typer.Option("Default", "--profile", "-p", help="Chrome profile name"),
):
    """Grab cookies from a real Chrome profile (gstack shortcut).

    Opens a browser-use CLI session with your real Chrome profile's
    cookies, navigates to the platform, exports cookies, and saves
    them as AUTEUR storage_state. No manual login needed if you're
    already logged in to Chrome.
    """
    from auteur.browser_ops.auth import make_account, bootstrap_via_cli_profile
    from auteur.browser_ops.platforms import PLATFORM_SPECS

    spec = None
    for s in PLATFORM_SPECS.values():
        if s.platform == platform:
            spec = s
            break

    if not spec:
        console.print(f"[red]Unknown platform: {platform}[/]")
        console.print(f"Available: {[s.platform for s in PLATFORM_SPECS.values()]}")
        raise typer.Exit(1)

    acct = make_account(platform, account)
    console.print(f"[bold cyan]Grabbing cookies[/] from Chrome profile '{chrome_profile}'")
    console.print(f"Platform: {spec.start_url}")

    success = bootstrap_via_cli_profile(acct, spec, chrome_profile=chrome_profile)
    if success:
        console.print("[green]✓ Cookies grabbed and saved[/]")
    else:
        console.print("[red]✗ Cookie grab failed[/]")


@app.command()
def browser_status():
    """Show browser automation status and authenticated platforms."""
    from auteur.browser_ops.auth import get_storage_state_dir
    from auteur.browser_ops.platforms import PLATFORM_SPECS

    settings = get_settings()
    table = Table(title="Browser Automation Status")
    table.add_column("Setting", style="cyan")
    table.add_column("Value")

    table.add_row("Enabled", "✓" if settings.browser_use_enabled else "✗")
    table.add_row("Controller LLM", "✓" if (settings.browser_use_api_key or settings.gemini_api_key) else "✗ no key")
    table.add_row("Storage Dir", str(settings.browser_storage_state_dir))

    console.print(table)

    # Show platform auth state
    state_dir = get_storage_state_dir()
    ptable = Table(title="Platform Auth")
    ptable.add_column("Platform", style="cyan")
    ptable.add_column("Model ID")
    ptable.add_column("Auth State")

    for model_id, spec in PLATFORM_SPECS.items():
        state_file = state_dir / f"{spec.platform}_default.json"
        auth_status = "✓ saved" if state_file.exists() else "✗ not bootstrapped"
        ptable.add_row(spec.platform, model_id, auth_status)

    console.print(ptable)


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
