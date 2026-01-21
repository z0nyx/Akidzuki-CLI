import logging
from typing import List, Optional
from datetime import datetime

from ..models.connection import SSHConnection
from ..config.manager import ConfigManager
from ..ssh.client import SSHClient


logger = logging.getLogger(__name__)


class ConnectionService:
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.ssh_client = SSHClient(config_manager)
        self._connection_cache = {}
        self._test_cache = {}
    
    def list_connections(self, filter_text: Optional[str] = None, group: Optional[str] = None, 
                        favorite_only: bool = False, sort_by: str = "name") -> List[SSHConnection]:
        connections = self.config_manager.get_all_connections()
        
        if filter_text:
            filter_lower = filter_text.lower()
            connections = [
                c for c in connections
                if filter_lower in c.name.lower() or filter_lower in c.hostname.lower()
            ]
        
        if group:
            connections = [c for c in connections if c.group == group]
        
        if favorite_only:
            connections = [c for c in connections if c.favorite]
        
        if sort_by == "name":
            connections.sort(key=lambda x: x.name.lower())
        elif sort_by == "host":
            connections.sort(key=lambda x: x.hostname.lower())
        elif sort_by == "last_used":
            connections.sort(key=lambda x: x.last_used or datetime.min, reverse=True)
        elif sort_by == "group":
            connections.sort(key=lambda x: (x.group or "", x.name.lower()))
        
        return connections
    
    def get_connection(self, name: str) -> Optional[SSHConnection]:
        return self.config_manager.get_connection_by_name(name)
    
    def add_connection(self, connection: SSHConnection) -> bool:
        result = self.config_manager.add_connection(connection)
        if result:
            logger.info(f"Connection added: {connection.name}")
        else:
            logger.warning(f"Failed to add connection: {connection.name} (already exists)")
        return result
    
    def update_connection(self, old_name: str, connection: SSHConnection) -> bool:
        result = self.config_manager.update_connection(old_name, connection)
        if result:
            logger.info(f"Connection updated: {old_name} -> {connection.name}")
        else:
            logger.warning(f"Failed to update connection: {old_name}")
        return result
    
    def delete_connection(self, name: str) -> bool:
        result = self.config_manager.delete_connection(name)
        if result:
            logger.info(f"Connection deleted: {name}")
        else:
            logger.warning(f"Failed to delete connection: {name}")
        return result
    
    def test_connection(self, connection: SSHConnection, use_cache: bool = True) -> tuple[bool, str]:
        cache_key = f"{connection.name}@{connection.hostname}:{connection.port}"
        
        if use_cache and cache_key in self._test_cache:
            cached_result, cached_time = self._test_cache[cache_key]
            if (datetime.now() - cached_time).seconds < 5:
                return cached_result
        
        logger.info(f"Testing connection: {connection.name}")
        success, message = self.ssh_client.test_connection(connection)
        
        if use_cache:
            self._test_cache[cache_key] = ((success, message), datetime.now())
        
        return success, message
    
    def mark_as_used(self, connection: SSHConnection):
        connection.last_used = datetime.now()
        self.config_manager.update_connection(connection.name, connection)
        logger.debug(f"Marked connection as used: {connection.name}")
    
    def toggle_favorite(self, connection: SSHConnection) -> bool:
        connection.favorite = not connection.favorite
        result = self.config_manager.update_connection(connection.name, connection)
        if result:
            logger.info(f"Toggled favorite for connection: {connection.name} -> {connection.favorite}")
        return result
    
    def get_groups(self) -> List[str]:
        connections = self.config_manager.get_all_connections()
        groups = set()
        for conn in connections:
            if conn.group:
                groups.add(conn.group)
        return sorted(list(groups))
    
    def get_recent_connections(self, limit: int = 5) -> List[SSHConnection]:
        connections = self.config_manager.get_all_connections()
        connections_with_date = [c for c in connections if c.last_used]
        connections_with_date.sort(key=lambda x: x.last_used, reverse=True)
        return connections_with_date[:limit]
