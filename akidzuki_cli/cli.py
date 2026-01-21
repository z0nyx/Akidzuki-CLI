import argparse
import sys
from rich.console import Console
from rich.table import Table

from .config.manager import ConfigManager
from .services.connection_service import ConnectionService
from .services.session_service import SessionService
from .ssh.session import SSHSession
from .utils.logger import setup_logging
from .settings import Settings


def cmd_list(args, connection_service: ConnectionService, console: Console):
    connections = connection_service.list_connections(sort_by=args.sort)
    
    if not connections:
        console.print("[yellow]No connections found.[/yellow]")
        return
    
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Name", style="cyan")
    table.add_column("Host", style="white")
    table.add_column("Port", style="white")
    table.add_column("User", style="white")
    table.add_column("Group", style="dim")
    table.add_column("Favorite", style="yellow")
    
    for conn in connections:
        favorite = "⭐" if conn.favorite else ""
        table.add_row(
            conn.name,
            conn.hostname,
            str(conn.port),
            conn.user,
            conn.group or "",
            favorite
        )
    
    console.print(table)


def cmd_test(args, connection_service: ConnectionService, console: Console):
    conn = connection_service.get_connection(args.name)
    if not conn:
        console.print(f"[red]Connection '{args.name}' not found.[/red]")
        return
    
    console.print(f"[cyan]Testing connection: {conn.name}[/cyan]")
    console.print(f"Host: {conn.hostname}:{conn.port}")
    console.print()
    
    success, message = connection_service.test_connection(conn)
    
    if success:
        console.print(f"[green]✓ {message}[/green]")
    else:
        console.print(f"[red]✗ {message}[/red]")
        sys.exit(1)


def cmd_connect(args, connection_service: ConnectionService, session_service: SessionService, console: Console):
    conn = connection_service.get_connection(args.name)
    if not conn:
        console.print(f"[red]Connection '{args.name}' not found.[/red]")
        sys.exit(1)
    
    console.print(f"[cyan]Connecting to {conn.name}...[/cyan]")
    console.print(f"Host: {conn.hostname}:{conn.port}")
    console.print()
    
    success, error, session = session_service.connect(conn)
    
    if not success:
        console.print(f"[red]Connection failed: {error}[/red]")
        sys.exit(1)
    
    connection_service.mark_as_used(conn)
    
    console.print("[green]Connected![/green]")
    console.print("[dim]Press Ctrl+B to return to menu, Ctrl+C to disconnect[/dim]")
    console.print()
    
    try:
        session.start_interactive_shell()
    except KeyboardInterrupt:
        pass
    finally:
        session.close()


def main_cli():
    parser = argparse.ArgumentParser(description="Akidzuki - SSH Connection Manager CLI")
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    list_parser = subparsers.add_parser('list', help='List all connections')
    list_parser.add_argument('--sort', choices=['name', 'host', 'last_used', 'group'], default='name', help='Sort order')
    
    test_parser = subparsers.add_parser('test', help='Test a connection')
    test_parser.add_argument('name', help='Connection name')
    
    connect_parser = subparsers.add_parser('connect', help='Connect to a server')
    connect_parser.add_argument('name', help='Connection name')
    
    args = parser.parse_args()
    
    settings = Settings()
    log_level = getattr(logging, settings.get_log_level(), logging.INFO)
    setup_logging(settings.get_log_file(), log_level)
    
    config_manager = ConfigManager(settings.get_config_path())
    connection_service = ConnectionService(config_manager)
    session_service = SessionService(config_manager, settings)
    console = Console()
    
    if args.command == 'list':
        cmd_list(args, connection_service, console)
    elif args.command == 'test':
        cmd_test(args, connection_service, console)
    elif args.command == 'connect':
        cmd_connect(args, connection_service, session_service, console)
    else:
        parser.print_help()
