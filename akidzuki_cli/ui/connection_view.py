from typing import Optional
from rich.console import Console
from rich.prompt import Prompt
from getpass import getpass

from ..models.connection import SSHConnection
from ..config.manager import ConfigManager
from ..utils.validators import validate_host, validate_port, validate_user


class ConnectionEditor:    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.console = Console()
    
    def create_new(self) -> Optional[SSHConnection]:
        self.console.print("[dim]Enter connection details (press Enter to skip optional fields)[/dim]")
        self.console.print()
        
        name = Prompt.ask("Connection name", default="").strip()
        if not name:
            return None
        
        if self.config_manager.get_connection_by_name(name):
            if not Prompt.ask(f"Connection '{name}' already exists. Overwrite?", choices=['y', 'n'], default='n') == 'y':
                return None
        
        while True:
            host = Prompt.ask("Host (IP or hostname)", default="").strip()
            if not host:
                self.console.print("[red]Host is required![/red]")
                continue
            is_valid, error = validate_host(host)
            if is_valid:
                break
            self.console.print(f"[red]{error}[/red]")
        
        hostname = Prompt.ask("HostName", default=host).strip() or host
        
        while True:
            user = Prompt.ask("Username", default="root").strip()
            is_valid, error = validate_user(user)
            if is_valid:
                break
            self.console.print(f"[red]{error}[/red]")
        
        while True:
            port_str = Prompt.ask("Port", default="22").strip()
            is_valid, error, port = validate_port(port_str)
            if is_valid:
                break
            self.console.print(f"[red]{error}[/red]")
        
        password = None
        if Prompt.ask("Enter password?", choices=['y', 'n'], default='n') == 'y':
            password = getpass("Password: ")
            if not password:
                password = None
        
        identity_file = Prompt.ask("Identity file path (SSH key)", default="").strip() or None
        
        group = Prompt.ask("Group (optional)", default="").strip() or None
        
        favorite = False
        if Prompt.ask("Mark as favorite?", choices=['y', 'n'], default='n') == 'y':
            favorite = True
        
        return SSHConnection(
            name=name,
            host=host,
            hostname=hostname,
            user=user,
            port=port,
            password=password,
            identity_file=identity_file,
            group=group,
            favorite=favorite
        )
    
    def edit(self, connection: SSHConnection) -> Optional[SSHConnection]:
        self.console.print("[dim]Edit connection details (press Enter to keep current value)[/dim]")
        self.console.print()
        
        new_name = Prompt.ask("Connection name", default=connection.name).strip()
        if not new_name:
            return None
        
        while True:
            host = Prompt.ask("Host", default=connection.host).strip()
            if not host:
                self.console.print("[red]Host is required![/red]")
                continue
            is_valid, error = validate_host(host)
            if is_valid:
                break
            self.console.print(f"[red]{error}[/red]")
        
        hostname = Prompt.ask("HostName", default=connection.hostname or connection.host).strip() or host
        
        while True:
            user = Prompt.ask("Username", default=connection.user).strip()
            is_valid, error = validate_user(user)
            if is_valid:
                break
            self.console.print(f"[red]{error}[/red]")
        
        while True:
            port_str = Prompt.ask("Port", default=str(connection.port)).strip()
            is_valid, error, port = validate_port(port_str)
            if is_valid:
                break
            self.console.print(f"[red]{error}[/red]")
        
        password = connection.password
        current_password = self.config_manager.get_password(connection)
        if current_password:
            password = current_password
        
        if Prompt.ask("Update password?", choices=['y', 'n'], default='n') == 'y':
            new_password = getpass("New password (leave empty to keep current): ")
            if new_password:
                password = new_password
        
        identity_file = Prompt.ask(
            "Identity file path", 
            default=connection.identity_file or ""
        ).strip() or None
        
        group = Prompt.ask("Group", default=connection.group or "").strip() or None
        
        favorite = connection.favorite
        if Prompt.ask(f"Favorite (current: {'Yes' if favorite else 'No'})?", choices=['y', 'n'], default='n') == 'y':
            favorite = not favorite
        
        return SSHConnection(
            name=new_name,
            host=host,
            hostname=hostname,
            user=user,
            port=port,
            password=password,
            identity_file=identity_file,
            group=group,
            favorite=favorite,
            last_used=connection.last_used,
            created_at=connection.created_at
        )


class ConnectionView:
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.console = Console()
