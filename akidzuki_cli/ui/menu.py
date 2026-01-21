from typing import List, Optional, Callable
import sys
import time
from rich.console import Console
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.layout import Layout
from rich.align import Align

from ..ui.connection_view import ConnectionEditor
from ..models.connection import SSHConnection
from ..config.manager import ConfigManager
from ..services.connection_service import ConnectionService
from ..utils.keyboard_handler import get_key


class MainMenu:
    
    def __init__(self, connection_service: ConnectionService):
        self.connection_service = connection_service
        self.console = Console()
        self.selected_index = 0
        self.connections: List[SSHConnection] = []
        self.filtered_connections: List[SSHConnection] = []
        self.running = True
        self.filter_text = ""
        self.filter_mode = False
        self.sort_by = "name"
        self.show_favorites_only = False
        self.selected_group: Optional[str] = None
        self._refresh_connections()
    
    def _refresh_connections(self):
        self.connections = self.connection_service.list_connections(
            filter_text=self.filter_text if self.filter_text else None,
            group=self.selected_group,
            favorite_only=self.show_favorites_only,
            sort_by=self.sort_by
        )
        self.filtered_connections = self.connections
        if self.selected_index >= len(self.filtered_connections):
            self.selected_index = max(0, len(self.filtered_connections) - 1)
    
    def _display_menu(self):
        self.console.clear()
        
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
        self.console.print(centered)
        self.console.print()
        
        if self.filter_mode:
            self.console.print(f"[yellow]Search: {self.filter_text}_[/yellow]")
            self.console.print()
        
        if self.show_favorites_only:
            self.console.print("[yellow]⭐ Showing favorites only[/yellow]")
        
        if self.selected_group:
            self.console.print(f"[cyan]📁 Group: {self.selected_group}[/cyan]")
        
        if not self.filtered_connections:
            if self.filter_text or self.show_favorites_only or self.selected_group:
                self.console.print("[yellow]No connections match the current filters.[/yellow]")
            else:
                self.console.print("[yellow]No connections found. Add a new connection to get started.[/yellow]")
            self.console.print()
        else:
            self.console.print(f"[bold]Connections ({len(self.filtered_connections)}/{len(self.connection_service.list_connections())}):[/bold]")
            self.console.print()
            
            recent_connections = self.connection_service.get_recent_connections(limit=3)
            recent_names = {c.name for c in recent_connections}
            
            for i, conn in enumerate(self.filtered_connections):
                if i == self.selected_index:
                    prefix = "▶ "
                    style = "bold green"
                else:
                    prefix = "  "
                    style = "white"
                
                favorite_icon = "⭐ " if conn.favorite else "  "
                group_text = f" [{conn.group}]" if conn.group else ""
                recent_icon = "🕐 " if conn.name in recent_names else "  "
                
                info = f"{favorite_icon}{recent_icon}{conn.name}{group_text} - {conn.user}@{conn.hostname}:{conn.port}"
                
                if conn.identity_file:
                    info += " 🔑"
                
                self.console.print(f"{prefix}[{style}]{info}[/{style}]")
            
            self.console.print()
        
        self._display_status_bar()
    
    def _display_status_bar(self):
        status_parts = []
        
        if self.filter_mode:
            status_parts.append("[dim]ESC[/dim] Cancel search")
        else:
            status_parts.append("[dim]↑↓[/dim] Navigate")
            status_parts.append("[dim]Enter[/dim] Connect")
            status_parts.append("[dim]A[/dim] Add")
            status_parts.append("[dim]E[/dim] Edit")
            status_parts.append("[dim]D[/dim] Delete")
            status_parts.append("[dim]T[/dim] Test")
            status_parts.append("[dim]F[/dim] Search")
            status_parts.append("[dim]S[/dim] Sort")
            status_parts.append("[dim]G[/dim] Group")
            status_parts.append("[dim]*/V[/dim] Favorite")
            status_parts.append("[dim]I[/dim] Info")
            status_parts.append("[dim]?[/dim] Help")
            status_parts.append("[dim]Q[/dim] Quit")
        
        status_line = " | ".join(status_parts)
        self.console.print(f"[dim]{'─' * 80}[/dim]")
        self.console.print(status_line)
    
    def _handle_navigation(self, key: str) -> bool:
        if key == 'up' and self.selected_index > 0:
            self.selected_index -= 1
            return True
        elif key == 'down' and self.selected_index < len(self.filtered_connections) - 1:
            self.selected_index += 1
            return True
        return False
    
    def _handle_filter_input(self, char: str):
        if char == 'backspace':
            self.filter_text = self.filter_text[:-1]
        elif char == 'escape':
            self.filter_mode = False
            self.filter_text = ""
        elif char == 'enter':
            self.filter_mode = False
        elif len(char) == 1 and char.isprintable():
            self.filter_text += char
        self._refresh_connections()
    
    def _add_connection(self):
        self.console.clear()
        self.console.print("[bold cyan]Add New SSH Connection[/bold cyan]")
        self.console.print()
        
        editor = ConnectionEditor(self.connection_service.config_manager)
        connection = editor.create_new()
        
        if connection:
            success = self.connection_service.add_connection(connection)
            if success:
                self.console.print("\n[green]✓ Connection added successfully![/green]")
                self._refresh_connections()
            else:
                self.console.print("\n[red]✗ Connection with this name already exists![/red]")
        else:
            self.console.print("\n[yellow]Cancelled.[/yellow]")
        
        self.console.print("\nPress Enter to continue...")
        input()
    
    def _edit_connection(self):
        if not self.filtered_connections:
            return
        
        conn = self.filtered_connections[self.selected_index]
        
        self.console.clear()
        self.console.print(f"[bold cyan]Edit Connection: {conn.name}[/bold cyan]")
        self.console.print()
        
        editor = ConnectionEditor(self.connection_service.config_manager)
        updated = editor.edit(conn)
        
        if updated:
            success = self.connection_service.update_connection(conn.name, updated)
            if success:
                self.console.print("\n[green]✓ Connection updated successfully![/green]")
                self._refresh_connections()
            else:
                self.console.print("\n[red]✗ Failed to update connection![/red]")
        else:
            self.console.print("\n[yellow]No changes made.[/yellow]")
        
        self.console.print("\nPress Enter to continue...")
        input()
    
    def _delete_connection(self):
        if not self.filtered_connections:
            return
        
        conn = self.filtered_connections[self.selected_index]
        
        if Confirm.ask(f"\n[red]Delete connection '{conn.name}'?[/red]"):
            success = self.connection_service.delete_connection(conn.name)
            if success:
                self.console.print("[green]✓ Connection deleted![/green]")
                self._refresh_connections()
            else:
                self.console.print("[red]✗ Failed to delete connection![/red]")
            self.console.print("\nPress Enter to continue...")
            input()
    
    def _test_connection(self):
        if not self.filtered_connections:
            return
        
        conn = self.filtered_connections[self.selected_index]
        
        self.console.clear()
        self.console.print(f"[cyan]Testing connection: {conn.name}[/cyan]")
        self.console.print(f"Host: {conn.hostname}:{conn.port}")
        self.console.print()
        
        with self.console.status("[bold green]Testing connection..."):
            success, message = self.connection_service.test_connection(conn)
        
        if success:
            self.console.print(f"[green]✓ {message}[/green]")
        else:
            self.console.print(f"[red]✗ {message}[/red]")
        
        self.console.print("\nPress Enter to continue...")
        input()
    
    def _show_connection_info(self):
        if not self.filtered_connections:
            return
        
        conn = self.filtered_connections[self.selected_index]
        
        self.console.clear()
        self.console.print(f"[bold cyan]Connection Info: {conn.name}[/bold cyan]")
        self.console.print()
        
        table = Table(show_header=False, box=None)
        table.add_column(style="cyan", width=20)
        table.add_column(style="white")
        
        table.add_row("Name:", conn.name)
        table.add_row("Host:", conn.hostname)
        table.add_row("Port:", str(conn.port))
        table.add_row("User:", conn.user)
        table.add_row("Group:", conn.group or "None")
        table.add_row("Favorite:", "⭐ Yes" if conn.favorite else "No")
        table.add_row("Identity File:", conn.identity_file or "None")
        table.add_row("Last Used:", conn.last_used.strftime("%Y-%m-%d %H:%M:%S") if conn.last_used else "Never")
        table.add_row("Created:", conn.created_at.strftime("%Y-%m-%d %H:%M:%S") if conn.created_at else "Unknown")
        
        self.console.print(table)
        self.console.print()
        self.console.print("Press Enter to continue...")
        input()
    
    def _toggle_favorite(self):
        if not self.filtered_connections:
            return
        
        conn = self.filtered_connections[self.selected_index]
        self.connection_service.toggle_favorite(conn)
        self._refresh_connections()
    
    def _change_sort(self):
        sort_options = ["name", "host", "last_used", "group"]
        current_idx = sort_options.index(self.sort_by) if self.sort_by in sort_options else 0
        next_idx = (current_idx + 1) % len(sort_options)
        self.sort_by = sort_options[next_idx]
        self._refresh_connections()
    
    def _change_group_filter(self):
        groups = self.connection_service.get_groups()
        if not groups:
            self.console.print("[yellow]No groups available.[/yellow]")
            self.console.print("Press Enter to continue...")
            input()
            return
        
        self.console.clear()
        self.console.print("[bold cyan]Select Group:[/bold cyan]")
        self.console.print()
        self.console.print("[dim]0[/dim] - All groups")
        for i, group in enumerate(groups, 1):
            marker = "▶ " if group == self.selected_group else "  "
            self.console.print(f"{marker}[dim]{i}[/dim] - {group}")
        
        self.console.print()
        choice = Prompt.ask("Select group", default="0")
        
        try:
            idx = int(choice)
            if idx == 0:
                self.selected_group = None
            elif 1 <= idx <= len(groups):
                self.selected_group = groups[idx - 1]
        except:
            pass
        
        self._refresh_connections()
    
    def _toggle_favorites_filter(self):
        self.show_favorites_only = not self.show_favorites_only
        self._refresh_connections()
    
    def _show_help(self):
        self.console.clear()
        self.console.print("[bold cyan]Keyboard Shortcuts[/bold cyan]")
        self.console.print()
        
        help_table = Table(show_header=True, header_style="bold cyan")
        help_table.add_column("Key", style="yellow")
        help_table.add_column("Action")
        
        help_table.add_row("↑ / ↓", "Navigate connections")
        help_table.add_row("Enter", "Connect to selected connection")
        help_table.add_row("A", "Add new connection")
        help_table.add_row("E", "Edit selected connection")
        help_table.add_row("D", "Delete selected connection")
        help_table.add_row("T", "Test connection")
        help_table.add_row("F", "Search / Filter connections")
        help_table.add_row("S", "Change sort order")
        help_table.add_row("G", "Filter by group")
        help_table.add_row("* / V", "Toggle favorite / Show favorites only")
        help_table.add_row("I", "Show connection info")
        help_table.add_row("R", "Refresh list")
        help_table.add_row("?", "Show this help")
        help_table.add_row("Q / ESC", "Quit")
        help_table.add_row("", "")
        help_table.add_row("[bold]During SSH Session:[/bold]", "")
        help_table.add_row("Ctrl+B", "Return to menu (keep connection)")
        help_table.add_row("Ctrl+C", "Disconnect and return")
        
        self.console.print(help_table)
        self.console.print()
        self.console.print("Press Enter to continue...")
        input()
    
    def _connect_to_selected(self) -> Optional[SSHConnection]:
        if not self.filtered_connections:
            return None
        
        conn = self.filtered_connections[self.selected_index]
        self.connection_service.mark_as_used(conn)
        return conn
    
    def run(self) -> Optional[SSHConnection]:
        while self.running:
            self._display_menu()
            
            try:
                key = None
                while key is None and self.running:
                    key = get_key()
                    if key is None:
                        time.sleep(0.05)
                
                if key is None:
                    continue
                
                if self.filter_mode:
                    self._handle_filter_input(key)
                    continue
                
                if key == 'up':
                    if self._handle_navigation('up'):
                        continue
                elif key == 'down':
                    if self._handle_navigation('down'):
                        continue
                elif key == 'enter':
                    if self.filtered_connections:
                        conn = self._connect_to_selected()
                        if conn:
                            return conn
                elif key == 'a':
                    self._add_connection()
                elif key == 'e':
                    if self.filtered_connections:
                        self._edit_connection()
                elif key == 'd':
                    if self.filtered_connections:
                        self._delete_connection()
                elif key == 't':
                    if self.filtered_connections:
                        self._test_connection()
                elif key == 'f':
                    self.filter_mode = True
                    self.filter_text = ""
                elif key == 's':
                    self._change_sort()
                elif key == 'g':
                    self._change_group_filter()
                elif key == '⭐' or key == '*' or key == 'v':
                    if self.filtered_connections:
                        self._toggle_favorite()
                    else:
                        self._toggle_favorites_filter()
                elif key == 'i':
                    if self.filtered_connections:
                        self._show_connection_info()
                elif key == '?':
                    self._show_help()
                elif key == 'c':
                    if self.filtered_connections:
                        conn = self._connect_to_selected()
                        if conn:
                            return conn
                elif key == 'r':
                    self._refresh_connections()
                elif key == 'q' or key == '\x03':
                    self.running = False
                    return None
                elif key == 'escape':
                    if self.filter_mode:
                        self.filter_mode = False
                        self.filter_text = ""
                        self._refresh_connections()
                    else:
                        self.running = False
                        return None
            
            except KeyboardInterrupt:
                self.running = False
                return None
            except Exception as e:
                try:
                    choice = input("\nEnter command: ").lower().strip()
                    if choice == 'a':
                        self._add_connection()
                    elif choice == 'e' and self.filtered_connections:
                        self._edit_connection()
                    elif choice == 'd' and self.filtered_connections:
                        self._delete_connection()
                    elif choice == 't' and self.filtered_connections:
                        self._test_connection()
                    elif choice == 'c' and self.filtered_connections:
                        return self._connect_to_selected()
                    elif choice == 'r':
                        self._refresh_connections()
                    elif choice == 'q':
                        self.running = False
                        return None
                except:
                    return None
        
        return None
