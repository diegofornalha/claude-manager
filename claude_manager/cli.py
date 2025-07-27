"""Command line interface for Claude Manager."""

from __future__ import annotations

import logging
import sys

import click
from rich.console import Console
from rich.logging import RichHandler

from claude_manager import __version__
from claude_manager.config import ClaudeConfigManager
from claude_manager.terminal_utils import safe_terminal, check_terminal_compatibility, immediate_terminal_reset
from claude_manager.tui import run_tui
from claude_manager.utils import SignalHandler

console = Console()


def setup_logging(debug: bool = False) -> None:
    """Set up logging configuration.

    Args:
        debug: Whether to enable debug logging
    """
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(message)s",
        handlers=[RichHandler(rich_tracebacks=True)],
    )


@click.command()
@click.option(
    "-c",
    "--config",
    "config_path",
    type=click.Path(exists=False),
    help="Path to claude.json configuration file (default: ~/.claude.json)",
)
@click.option(
    "--no-backup",
    is_flag=True,
    help="Disable automatic backups when making changes",
)
@click.option(
    "--debug",
    is_flag=True,
    help="Enable debug logging",
)
@click.option(
    "--reset-terminal",
    is_flag=True,
    help="Emergency terminal reset (fixes stuck ANSI codes)",
)
@click.version_option(version=__version__, prog_name="claude-manager")
def main(config_path: str | None, no_backup: bool, debug: bool, reset_terminal: bool) -> None:  # noqa: ARG001
    """Claude Manager - Manage your Claude Code projects and configurations.

    This tool provides a terminal UI for managing Claude Code projects stored
    in the .claude.json configuration file. It supports:

    \b
    • Listing and analyzing projects
    • Removing unused or old projects
    • Managing MCP server configurations
    • Clearing project history
    • Creating and restoring backups

    Examples:

    \b
        # Run with default config location (~/.claude.json)
        claude-manager

    \b
        # Use custom config file
        claude-manager -c /path/to/config.json

    \b
        # Enable debug logging
        claude-manager --debug
    """
    setup_logging(debug)
    logging.getLogger(__name__)

    # Emergency terminal reset option
    if reset_terminal:
        console.print("[yellow]Performing emergency terminal reset...[/yellow]")
        immediate_terminal_reset()
        console.print("[green]Terminal reset completed![/green]")
        console.print("[dim]Mouse tracking and ANSI codes should now be disabled.[/dim]")
        return

    # no_backup parameter is reserved for future use
    # Check terminal compatibility first
    if not check_terminal_compatibility():
        console.print("[yellow]Warning: Terminal may not support full TUI features[/yellow]")
        console.print("[dim]Continuing anyway... Use Ctrl+C to exit if problems occur[/dim]")

    # Set up signal handlers and terminal management for clean exit
    with SignalHandler(), safe_terminal() as terminal_manager:
        try:
            # Initialize config manager
            config_manager = ClaudeConfigManager(config_path)

            # Load configuration
            if not config_manager.load_config():
                console.print("[red]Failed to load configuration. Exiting.[/red]")
                sys.exit(1)

            # Run TUI with terminal management
            run_tui(config_manager)

        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted by user[/yellow]")
            # Terminal cleanup happens automatically via context manager
            sys.exit(0)
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]")
            if debug:
                console.print_exception()
            # Terminal cleanup happens automatically via context manager
            sys.exit(1)


if __name__ == "__main__":
    main()
