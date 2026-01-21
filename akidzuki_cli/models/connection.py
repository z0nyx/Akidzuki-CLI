from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class SSHConnection:
    
    name: str
    host: str
    hostname: Optional[str] = None
    port: int = 22
    user: str = "root"
    password: Optional[str] = None
    key_file: Optional[str] = None
    identity_file: Optional[str] = None
    group: Optional[str] = None
    favorite: bool = False
    last_used: Optional[datetime] = None
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.hostname is None:
            self.hostname = self.host
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_ssh_config_format(self) -> str:
        lines = [f"Host {self.name}"]
        lines.append(f"  HostName {self.hostname}")
        lines.append(f"  User {self.user}")
        
        if self.port != 22:
            lines.append(f"  Port {self.port}")
        
        if self.identity_file:
            lines.append(f"  IdentityFile {self.identity_file}")
        
        if self.group:
            lines.append(f"  # Group: {self.group}")
        
        if self.favorite:
            lines.append(f"  # Favorite: true")
        
        if self.last_used:
            lines.append(f"  # LastUsed: {self.last_used.isoformat()}")
        
        if self.created_at:
            lines.append(f"  # CreatedAt: {self.created_at.isoformat()}")
        
        return "\n".join(lines) + "\n"
    
    @classmethod
    def from_ssh_config_block(cls, block: str) -> Optional['SSHConnection']:
        lines = [line.strip() for line in block.strip().split('\n') if line.strip()]
        
        if not lines:
            return None
        
        name = None
        hostname = None
        user = None
        port = 22
        identity_file = None
        group = None
        favorite = False
        last_used = None
        created_at = None
        
        for line in lines:
            if line.startswith('#'):
                comment = line[1:].strip()
                if comment.startswith('Group:'):
                    group = comment.split(':', 1)[1].strip()
                elif comment.startswith('Favorite:'):
                    favorite = comment.split(':', 1)[1].strip().lower() == 'true'
                elif comment.startswith('LastUsed:'):
                    try:
                        last_used = datetime.fromisoformat(comment.split(':', 1)[1].strip())
                    except:
                        pass
                elif comment.startswith('CreatedAt:'):
                    try:
                        created_at = datetime.fromisoformat(comment.split(':', 1)[1].strip())
                    except:
                        pass
                continue
            
            parts = line.split(None, 1)
            if len(parts) < 2:
                continue
            
            key = parts[0].lower()
            value = parts[1]
            
            if key == 'host':
                name = value
            elif key == 'hostname':
                hostname = value
            elif key == 'user':
                user = value
            elif key == 'port':
                try:
                    port = int(value)
                except ValueError:
                    pass
            elif key == 'identityfile':
                identity_file = value
        
        if not name or not hostname:
            return None
        
        return cls(
            name=name,
            host=hostname,
            hostname=hostname,
            user=user or "root",
            port=port,
            identity_file=identity_file,
            group=group,
            favorite=favorite,
            last_used=last_used,
            created_at=created_at
        )
