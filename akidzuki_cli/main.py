import sys
import os
import time
import logging
from rich.console import Console
from rich.text import Text
from rich.prompt import Confirm
from rich.align import Align

from .config.manager import ConfigManager
from .services.connection_service import ConnectionService
from .services.session_service import SessionService
from .ssh.session import SSHSession
from .ui.menu import MainMenu
from .settings import Settings
from .utils.logger import setup_logging


def main():
    settings = Settings()
    log_level = getattr(logging, settings.get_log_level(), logging.INFO)
    setup_logging(settings.get_log_file(), log_level)
    
    console = Console()
    
    console.clear()
    
    ascii_logo = r"""           _    _     _           _    _ 
     /\   | |  (_)   | |         | |  (_)
    /  \  | | ___  __| |_____   _| | ___ 
   / /\ \ | |/ / |/ _` |_  / | | | |/ / |
  / ____ \|   <| | (_| |/ /| |_| |   <| |
 /_/    \_\_|\_\_|\__,_/___|\__,_|_|\_\_|"""
    
    logo_text = Text(ascii_logo, style="bold cyan")
    author = Text("github: z0nyx", style="white")
    github = Text("https://github.com/z0nyx/Akidzuki-CLI", style="white")
    
    content = Text()
    content.append(logo_text)
    content.append("\n\n")
    content.append(author)
    content.append("\n")
    content.append(github)
    
    centered = Align.center(content)
    console.print(centered)
    console.print()
    
    config_manager = ConfigManager(settings.get_config_path())
    connection_service = ConnectionService(config_manager)
    session_service = SessionService(config_manager, settings)
    
    active_session: SSHSession = None
    
    try:
        while True:
            menu = MainMenu(connection_service)
            selected_connection = menu.run()
            
            if selected_connection is None:
                if active_session:
                    try:
                        active_session.close()
                    except:
                        pass
                break
            
            reuse_connection = False
            if session_service.can_reuse_connection(selected_connection):
                console.clear()
                console.print(f"[yellow]Connection to {selected_connection.name} is already active.[/yellow]")
                reuse_connection = Confirm.ask("Reconnect to existing session?", default=True)
            
            if not reuse_connection:
                console.clear()
                console.print(f"[cyan]Connecting to {selected_connection.name}...[/cyan]")
                console.print(f"Host: {selected_connection.hostname}:{selected_connection.port}")
                console.print(f"User: {selected_connection.user}")
                console.print()
                
                success, error, session = session_service.connect(selected_connection)
                
                if not success:
                    console.print(f"[red]Connection failed: {error}[/red]")
                    console.print("\nPress Enter to return to menu...")
                    input()
                    continue
                
                active_session = session
            else:
                session = session_service.get_active_session()
                if not session:
                    console.print("[red]No active session found.[/red]")
                    console.print("Press Enter to continue...")
                    input()
                    continue
                console.clear()
                console.print(f"[green]Reconnecting to {selected_connection.name}...[/green]")
                console.print()
            
            def return_to_menu():
                nonlocal active_session
                pass
            
            try:
                console.print("[green]Connected![/green]")
                console.print("[dim]Press Ctrl+B to return to menu without disconnecting[/dim]")
                console.print("[dim]Press Ctrl+C to disconnect and exit[/dim]")
                console.print()
                time.sleep(0.5)
                
                console.clear()
                
                session.start_interactive_shell(on_exit=return_to_menu)
                
                if session.returned_to_menu:
                    session.returned_to_menu = False
                    session.stop()
                    active_session = None
                    continue
                
                session.close()
                active_session = None
                session_service.close_session(close_connection=True)
                
                console.print()
                console.print("[yellow]Disconnected from SSH session.[/yellow]")
                console.print("Press Enter to return to menu...")
                input()
                
            except KeyboardInterrupt:
                if session:
                    session.close()
                active_session = None
                session_service.close_session(close_connection=True)
                console.print("\n[yellow]Disconnected.[/yellow]")
                console.print("Press Enter to return to menu...")
                input()
            
    except KeyboardInterrupt:
        pass
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        console.print_exception()
    finally:
        if active_session:
            try:
                active_session.close()
            except:
                pass
        
        console.clear()
        console.print("[cyan]Goodbye![/cyan]")


if __name__ == "__main__":
    main()
