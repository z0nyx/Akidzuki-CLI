import paramiko
from typing import Optional
import socket
import time

from ..models.connection import SSHConnection
from ..config.manager import ConfigManager


class SSHClient:
    
    def __init__(self, config_manager: ConfigManager, timeout: int = 10):
        self.config_manager = config_manager
        self.timeout = timeout
    
    def connect(self, connection: SSHConnection) -> tuple[bool, Optional[str], Optional[paramiko.SSHClient]]:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            password = connection.password
            if not password:
                password = self.config_manager.get_password(connection)
            
            kwargs = {
                'hostname': connection.hostname,
                'port': connection.port,
                'username': connection.user,
                'timeout': self.timeout
            }
            
            if connection.key_file or connection.identity_file:
                key_file = connection.key_file or connection.identity_file
                try:
                    client.connect(**kwargs, key_filename=key_file)
                except Exception as e:
                    if password:
                        kwargs['password'] = password
                        client.connect(**kwargs)
                    else:
                        raise
            elif password:
                kwargs['password'] = password
                client.connect(**kwargs)
            else:
                client.connect(**kwargs)
            
            return True, None, client
        
        except paramiko.AuthenticationException:
            return False, "Authentication failed. Check username and password.", None
        except paramiko.SSHException as e:
            return False, f"SSH connection error: {str(e)}", None
        except socket.error as e:
            return False, f"Network error: {str(e)}", None
        except Exception as e:
            return False, f"Unexpected error: {str(e)}", None
    
    def test_connection(self, connection: SSHConnection) -> tuple[bool, str]:
        success, error, client = self.connect(connection)
        if success and client:
            client.close()
            return True, "Connection successful"
        return False, error or "Connection failed"
