import logging
from typing import Optional

from ..models.connection import SSHConnection
from ..ssh.client import SSHClient
from ..ssh.session import SSHSession
from ..config.manager import ConfigManager


logger = logging.getLogger(__name__)


class SessionService:
    
    def __init__(self, config_manager: ConfigManager, settings: Optional[Settings] = None):
        self.config_manager = config_manager
        self.settings = settings or Settings()
        timeout = self.settings.get_ssh_timeout()
        self.ssh_client_wrapper = SSHClient(config_manager, timeout=timeout)
        self.active_session: Optional[SSHSession] = None
        self.active_ssh_client = None
    
    def connect(self, connection: SSHConnection) -> tuple[bool, Optional[str], Optional[SSHSession]]:
        logger.info(f"Connecting to: {connection.name} ({connection.hostname}:{connection.port})")
        
        success, error, ssh_client = self.ssh_client_wrapper.connect(connection)
        
        if not success:
            logger.error(f"Connection failed: {connection.name} - {error}")
            return False, error, None
        
        session = SSHSession(ssh_client, connection.name)
        self.active_session = session
        self.active_ssh_client = ssh_client
        
        if ssh_client.get_transport():
            keepalive = self.settings.get_keepalive_interval()
            ssh_client.get_transport().set_keepalive(keepalive)
        
        logger.info(f"Successfully connected to: {connection.name}")
        return True, None, session
    
    def can_reuse_connection(self, connection: SSHConnection) -> bool:
        if not self.active_ssh_client or not self.active_ssh_client.get_transport():
            return False
        
        transport = self.active_ssh_client.get_transport()
        if not transport.is_active():
            return False
        
        try:
            sockname = transport.sock.getpeername() if transport.sock else None
            if sockname and sockname[0] == connection.hostname and sockname[1] == connection.port:
                return True
        except:
            pass
        
        return False
    
    def get_active_session(self) -> Optional[SSHSession]:
        return self.active_session
    
    def close_session(self, close_connection: bool = False):
        if self.active_session:
            if close_connection:
                self.active_session.close()
                self.active_ssh_client = None
            else:
                self.active_session.stop()
            self.active_session = None
            logger.info("Session closed")
