import paramiko
import sys
import time
import os
import socket
import threading
import queue

from typing import Optional, Callable

if sys.platform == 'win32':
    import msvcrt


class SSHSession:
    def __init__(self, ssh_client: paramiko.SSHClient, connection_name: str):
        self.ssh_client = ssh_client
        self.connection_name = connection_name
        self.channel: Optional[paramiko.Channel] = None
        self.is_active = False
        self.on_exit: Optional[Callable] = None
        self.returned_to_menu = False
    
    def start_interactive_shell(self, on_exit: Optional[Callable] = None):
        self.on_exit = on_exit
        self.channel = self.ssh_client.invoke_shell(term='xterm-256color')
        self.channel.setblocking(0)
        self.is_active = True
        
        time.sleep(0.1)
        
        if sys.platform == 'win32':
            self._start_interactive_shell_windows()
        else:
            self._start_interactive_shell_unix()
    
    def _start_interactive_shell_unix(self):
        import termios
        import tty
        import select
        
        self.old_settings = termios.tcgetattr(sys.stdin)
        
        try:
            tty.setraw(sys.stdin.fileno())
            
            while self.is_active:
                if self.channel.exit_status_ready():
                    break
                
                if self.channel.closed:
                    break
                
                ready_channels = select.select([self.channel], [], [], 0.1)[0]
                if ready_channels:
                    try:
                        data = self.channel.recv(4096)
                        if data:
                            os.write(sys.stdout.fileno(), data)
                            sys.stdout.flush()
                        else:
                            if self.channel.closed:
                                break
                    except EOFError:
                        break
                    except Exception:
                        if self.channel.closed:
                            break
                
                ready_stdin = select.select([sys.stdin], [], [], 0.1)[0]
                if ready_stdin:
                    try:
                        data = os.read(sys.stdin.fileno(), 4096)
                        if not data:
                            break
                        
                        if data == b'\x02':  # Ctrl+B
                            self._handle_menu_return()
                            continue
                        
                        if not self.channel.closed:
                            self.channel.send(data)
                    except Exception:
                        if self.channel.closed:
                            break
        
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()
    
    def _start_interactive_shell_windows(self):        
        input_queue = queue.Queue()
        output_queue = queue.Queue()
        stop_event = threading.Event()
        
        def input_thread():
            while self.is_active and not stop_event.is_set():
                try:
                    if msvcrt.kbhit():
                        ch = msvcrt.getch()
                        if ch == b'\x02':
                            self._handle_menu_return()
                            break
                        input_queue.put(ch)
                    else:
                        time.sleep(0.01)
                except Exception:
                    break
        
        def output_thread():
            while self.is_active and not stop_event.is_set():
                try:
                    data = output_queue.get(timeout=0.1)
                    sys.stdout.buffer.write(data)
                    sys.stdout.flush()
                except queue.Empty:
                    continue
                except Exception:
                    break
        
        in_thread = threading.Thread(target=input_thread, daemon=True)
        out_thread = threading.Thread(target=output_thread, daemon=True)
        in_thread.start()
        out_thread.start()
        
        try:
            while self.is_active:
                if self.channel.exit_status_ready():
                    break
                
                if self.channel.closed:
                    break
                
                try:
                    data = self.channel.recv(4096)
                    if data:
                        output_queue.put(data)
                except (socket.timeout, OSError, IOError) as e:
                    errno = getattr(e, 'errno', None)
                    if errno in (10035, 11):
                        pass
                    elif self.channel.closed or self.channel.exit_status_ready():
                        break
                    else:
                        pass
                except EOFError:
                    break
                except Exception as e:
                    if self.channel.closed or self.channel.exit_status_ready():
                        break
                    error_str = str(e).lower()
                    if 'timeout' in error_str or 'would block' in error_str or 'resource temporarily unavailable' in error_str:
                        pass
                    else:
                        if self.channel.closed:
                            break
            
                try:
                    if not input_queue.empty():
                        ch = input_queue.get_nowait()
                        if self.channel.closed:
                            break
                        self.channel.send(ch)
                except queue.Empty:
                    pass
                except Exception:
                    if self.channel.closed:
                        break
                
                time.sleep(0.01)
        
        except KeyboardInterrupt:
            pass
        finally:
            stop_event.set()
            self.stop()
    
    def _handle_menu_return(self):
        if sys.platform != 'win32' and hasattr(self, 'old_settings'):
            try:
                import termios
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)
            except Exception:
                pass
        
        self.returned_to_menu = True
        self.is_active = False
        
        if self.on_exit:
            self.on_exit()
    
    def stop(self):
        self.is_active = False
        
        if sys.platform != 'win32' and hasattr(self, 'old_settings'):
            try:
                import termios
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)
            except Exception:
                pass
        
        if self.channel:
            try:
                self.channel.close()
            except Exception:
                pass
            
    def close(self):
        self.stop()
        if self.ssh_client:
            try:
                self.ssh_client.close()
            except Exception:
                pass
