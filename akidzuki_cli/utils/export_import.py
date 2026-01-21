import json
from pathlib import Path
from typing import List, Optional, Tuple
from datetime import datetime

from ..models.connection import SSHConnection
from ..config.manager import ConfigManager


def export_to_json(config_manager: ConfigManager, output_file: str) -> bool:
    try:
        connections = config_manager.get_all_connections()
        data = []
        
        for conn in connections:
            conn_dict = {
                "name": conn.name,
                "host": conn.host,
                "hostname": conn.hostname,
                "port": conn.port,
                "user": conn.user,
                "identity_file": conn.identity_file,
                "group": conn.group,
                "favorite": conn.favorite,
                "last_used": conn.last_used.isoformat() if conn.last_used else None,
                "created_at": conn.created_at.isoformat() if conn.created_at else None
            }
            data.append(conn_dict)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception:
        return False


def import_from_json(config_manager: ConfigManager, input_file: str) -> Tuple[int, int]:
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        imported = 0
        skipped = 0
        
        for item in data:
            try:
                conn = SSHConnection(
                    name=item["name"],
                    host=item["host"],
                    hostname=item.get("hostname", item["host"]),
                    port=item.get("port", 22),
                    user=item.get("user", "root"),
                    identity_file=item.get("identity_file"),
                    group=item.get("group"),
                    favorite=item.get("favorite", False),
                    last_used=datetime.fromisoformat(item["last_used"]) if item.get("last_used") else None,
                    created_at=datetime.fromisoformat(item["created_at"]) if item.get("created_at") else None
                )
                
                existing = config_manager.get_connection_by_name(conn.name)
                if existing:
                    skipped += 1
                    continue
                
                if config_manager.add_connection(conn):
                    imported += 1
            except Exception:
                skipped += 1
        
        return imported, skipped
    except Exception:
        return 0, 0


def export_to_ssh_config(config_manager: ConfigManager, output_file: str) -> bool:
    try:
        connections = config_manager.get_all_connections()
        content = "\n\n".join([conn.to_ssh_config_format().strip() for conn in connections])
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content + "\n")
        
        return True
    except Exception:
        return False


def import_from_ssh_config(config_manager: ConfigManager, input_file: str) -> Tuple[int, int]:
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
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
        
        imported = 0
        skipped = 0
        
        for block in blocks:
            conn = SSHConnection.from_ssh_config_block(block)
            if conn:
                existing = config_manager.get_connection_by_name(conn.name)
                if existing:
                    skipped += 1
                    continue
                
                if config_manager.add_connection(conn):
                    imported += 1
        
        return imported, skipped
    except Exception:
        return 0, 0
