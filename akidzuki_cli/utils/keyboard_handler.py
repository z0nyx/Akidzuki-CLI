import sys
import os

if sys.platform == 'win32':
    import msvcrt
    
    def get_key():
        if msvcrt.kbhit():
            ch = msvcrt.getch()
            if ch == b'\xe0':
                ch = msvcrt.getch()
                if ch == b'H':  # Up arrow
                    return 'up'
                elif ch == b'P':  # Down arrow
                    return 'down'
                elif ch == b'M':  # Right arrow
                    return 'right'
                elif ch == b'K':  # Left arrow
                    return 'left'
            elif ch == b'\r':  # Enter
                return 'enter'
            elif ch == b'\x1b':  # Escape
                return 'escape'
            elif ch == b'\x08':  # Backspace
                return 'backspace'
            else:
                try:
                    decoded = ch.decode('utf-8')
                    if decoded == '*':
                        return '*'
                    return decoded.lower()
                except:
                    return None
        return None
else:
    import termios
    import tty
    import select
    
    def get_key():
        if not select.select([sys.stdin], [], [], 0)[0]:
            return None
        
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
            if ch == '\x1b':
                if select.select([sys.stdin], [], [], 0.05)[0]:
                    ch2 = sys.stdin.read(1)
                    ch3 = sys.stdin.read(1) if ch2 == '[' and select.select([sys.stdin], [], [], 0.05)[0] else ''
                    ch = ch + ch2 + ch3
                    if ch == '\x1b[A':  # Up arrow
                        return 'up'
                    elif ch == '\x1b[B':  # Down arrow
                        return 'down'
                    elif ch == '\x1b[C':  # Right arrow
                        return 'right'
                    elif ch == '\x1b[D':  # Left arrow
                        return 'left'
                    else:
                        return 'escape'
                else:
                    return 'escape'
            elif ch == '\r' or ch == '\n':  # Enter
                return 'enter'
            elif ch == '\x7f':  # Backspace
                return 'backspace'
            else:
                return ch.lower()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return None
