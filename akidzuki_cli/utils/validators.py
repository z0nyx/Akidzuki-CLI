import re
import socket

def validate_host(host: str) -> tuple[bool, str]:
    if not host or not host.strip():
        return False, "Host cannot be empty"
    
    host = host.strip()
    
    try:
        socket.inet_aton(host)
        return True, ""
    except socket.error:
        pass
    
    if len(host) > 255:
        return False, "Hostname too long"
    
    if re.match(r'^[a-zA-Z0-9.-]+$', host):
        return True, ""
    
    return False, "Invalid host format"


def validate_port(port: str) -> tuple[bool, str, int]:
    try:
        port_num = int(port)
        if 1 <= port_num <= 65535:
            return True, "", port_num
        return False, "Port must be between 1 and 65535", 0
    except ValueError:
        return False, "Port must be a number", 0


def validate_user(user: str) -> tuple[bool, str]:
    if not user or not user.strip():
        return False, "Username cannot be empty"
    
    if len(user) > 32:
        return False, "Username too long"
    
    if re.match(r'^[a-zA-Z0-9_.-]+$', user):
        return True, ""
    
    return False, "Invalid username format"
