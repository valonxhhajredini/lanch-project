"""
Port management functionality for clearing processes on specific ports.
"""

import subprocess
import platform
import threading
from config.settings import PROCESS_CONFIG


def find_and_kill_process_on_port(port, output_queue):
    """
    Find and kill any process running on the specified port.
    
    Args:
        port (int): The port number to check and clear
        output_queue (queue.Queue): Queue for sending output messages
        
    Returns:
        bool: True if port was successfully cleared or was already free, False otherwise
    """
    os_name = platform.system()
    pid_to_kill = None
    found_process = False
    
    output_queue.put((f"INFO: Checking port {port} (OS: {os_name})...\n", ("info_tag",)))
    
    try:
        # Find process using the port
        if os_name in ["Darwin", "Linux"]:
            find_cmd = f"lsof -t -iTCP:{port} -sTCP:LISTEN"
            result = subprocess.run(
                find_cmd, shell=True, capture_output=True, text=True, 
                timeout=PROCESS_CONFIG["port_check_timeout"]
            )
            if result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                pid_to_kill = pids[0]
                found_process = True
                
        elif os_name == "Windows":
            find_cmd = f'netstat -ano -p TCP | findstr ":{port}" | findstr "LISTENING"'
            result = subprocess.run(
                find_cmd, shell=True, capture_output=True, text=True, 
                timeout=PROCESS_CONFIG["process_kill_timeout"]
            )
            if result.stdout.strip():
                lines = result.stdout.strip().split('\n')
                if lines:
                    parts = lines[0].strip().split()
                    if (len(parts) >= 4 and parts[0].upper() == "TCP" and 
                        parts[-2].upper() == "LISTENING"):
                        pid_to_kill = parts[-1]
                        found_process = True
        
        if not found_process:
            output_queue.put((f"INFO: No active process on port {port}.\n", ("info_tag",)))
            return True
        
        # Kill the process
        output_queue.put((f"INFO: Found PID {pid_to_kill} on port {port}. Killing...\n", ("info_tag",)))
        
        if os_name in ["Darwin", "Linux"]:
            kill_cmd = f"kill -9 {pid_to_kill}"
        elif os_name == "Windows":
            kill_cmd = f"taskkill /F /PID {pid_to_kill}"
        else:
            output_queue.put((f"ERROR: Unsupported OS for killing: {os_name}\n", ("error_tag",)))
            return False
            
        kill_result = subprocess.run(
            kill_cmd, shell=True, capture_output=True, text=True, 
            timeout=PROCESS_CONFIG["port_check_timeout"]
        )
        
        if kill_result.returncode == 0:
            output_queue.put((f"SUCCESS: Killed PID {pid_to_kill}.\n", ("info_tag",)))
            threading.Event().wait(0.5)  # Brief pause after killing
            return True
        else:
            err_msg = kill_result.stderr.strip() or kill_result.stdout.strip()
            output_queue.put((f"ERROR killing PID {pid_to_kill}: {err_msg}\n", ("error_tag",)))
            return False
            
    except subprocess.TimeoutExpired:
        output_queue.put((f"ERROR: Timeout during port check/kill for port {port}.\n", ("error_tag",)))
        return False
    except Exception as e:
        output_queue.put((f"ERROR during port clearing ({port}): {str(e)}\n", ("error_tag",)))
        return False
        
    return True 