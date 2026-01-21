import os
from pathlib import Path
from typing import List, Optional
import keyring

from ..models.connection import SSHConnection


class ConfigManager:
    
    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            self.config_path = Path(".ssh_config")
        else:
            self.config_path = Path(config_path)
        
        if not self.config_path.exists():
            self.config_path.touch()
    
    def _read_config_file(self) -> str:
        try:
            return self.config_path.read_text(encoding='utf-8')
        except Exception:
            return ""
    
    def _write_config_file(self, content: str):
        self.config_path.write_text(content, encoding='utf-8')
    
    def _parse_blocks(self, content: str) -> List[str]:
        blocks = []
        current_block = []
        
        for line in content.split('\n'):
            stripped = line.strip()
            if not stripped:
                if current_block:
                    blocks.append('\n'.join(current_block))
                    current_block = []
                continue
            
            if stripped.lower().startswith('host ') and current_block:
                blocks.append('\n'.join(current_block))
                current_block = [line]
            else:
                current_block.append(line)
        
        if current_block:
            blocks.append('\n'.join(current_block))
        
        return blocks
    
    def get_all_connections(self) -> List[SSHConnection]:
        content = self._read_config_file()
        blocks = self._parse_blocks(content)
        
        connections = []
        for block in blocks:
            conn = SSHConnection.from_ssh_config_block(block)
            if conn:
                connections.append(conn)
        
        return connections
    
    def get_connection_by_name(self, name: str) -> Optional[SSHConnection]:
        connections = self.get_all_connections()
        for conn in connections:
            if conn.name == name:
                return conn
        return None
    
    def add_connection(self, connection: SSHConnection) -> bool:
        existing = self.get_connection_by_name(connection.name)
        if existing:
            return False
        
        if connection.password:
            keyring.set_password(
                "ssh-cli",
                f"{connection.name}@{connection.host}",
                connection.password
            )
        
        config_content = self._read_config_file()
        new_block = connection.to_ssh_config_format()
        
        if config_content and not config_content.endswith('\n'):
            config_content += '\n'
        
        config_content += new_block + '\n'
        self._write_config_file(config_content)
        
        return True
    
    def update_connection(self, old_name: str, connection: SSHConnection) -> bool:
        connections = self.get_all_connections()
        
        found = False
        updated_connections = []
        
        for conn in connections:
            if conn.name == old_name:
                found = True
                if connection.password:
                    keyring.set_password(
                        "ssh-cli",
                        f"{connection.name}@{connection.host}",
                        connection.password
                    )
                updated_connections.append(connection)
            else:
                updated_connections.append(conn)
        
        if not found:
            return False
        
        content = '\n\n'.join([
            conn.to_ssh_config_format().strip() 
            for conn in updated_connections
        ])
        
        if content:
            content += '\n'
        
        self._write_config_file(content)
        return True
    
    def delete_connection(self, name: str) -> bool:
        connections = self.get_all_connections()
        
        found = False
        remaining_connections = []
        
        for conn in connections:
            if conn.name == name:
                found = True
                try:
                    keyring.delete_password("ssh-cli", f"{name}@{conn.host}")
                except Exception:
                    pass
            else:
                remaining_connections.append(conn)
        
        if not found:
            return False
        
        content = '\n\n'.join([
            conn.to_ssh_config_format().strip() 
            for conn in remaining_connections
        ])
        
        if content:
            content += '\n'
        
        self._write_config_file(content)
        return True
    
    def get_password(self, connection: SSHConnection) -> Optional[str]:
        try:
            return keyring.get_password(
                "ssh-cli",
                f"{connection.name}@{connection.host}"
            )
        except Exception:
            return None
