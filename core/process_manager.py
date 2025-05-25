"""
Process management functionality for executing and controlling commands.
"""

import subprocess
import threading
import platform
import signal
import os
import traceback
from config.settings import PROCESS_CONFIG


class ProcessHandler:
    """Manages a single running process and its associated threads."""
    
    def __init__(self):
        self.process = None
        self.thread = None
        self.stop_event = threading.Event()
        self.pgid = None
        
    def reset(self):
        """Reset the handler for a new process."""
        self.process = None
        self.thread = None
        self.pgid = None
        self.stop_event.clear()
        
    def is_running(self):
        """Check if process is currently running."""
        return (self.process and self.process.poll() is None) or \
               (self.thread and self.thread.is_alive())


def stream_output_worker(command_str, cwd_str, output_queue, stop_event_ref, process_handler):
    """
    Worker function that runs in a separate thread to execute commands and stream output.
    
    Args:
        command_str (str): Command to execute
        cwd_str (str): Working directory
        output_queue (queue.Queue): Queue for output messages
        stop_event_ref (threading.Event): Event to signal stopping
        process_handler (ProcessHandler): Handler to store process info
    """
    process = None
    process_handler.pgid = None
    
    try:
        output_queue.put((f"Attempting: {command_str} in {cwd_str}\n\n", ("info_tag",)))
        
        # Configure process creation based on platform
        start_new_session_flag = platform.system() != "Windows"
        
        process = subprocess.Popen(
            command_str, shell=True, cwd=cwd_str,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, bufsize=1, universal_newlines=True, errors='replace',
            start_new_session=start_new_session_flag
        )
        
        process_handler.process = process
        
        # Get process group ID for Unix-like systems
        if platform.system() != "Windows":
            try:
                process_handler.pgid = os.getpgid(process.pid)
            except OSError:
                process_handler.pgid = None

        pgid_info = f' (PGID: {process_handler.pgid})' if process_handler.pgid else ''
        output_queue.put((f"PID: {process.pid}{pgid_info}. Streaming output...\n{'-'*26}\n", ("info_tag",)))

        # Start output streaming threads
        stdout_thread = threading.Thread(
            target=_enqueue_output, 
            args=(process.stdout, "stdout", output_queue, stop_event_ref), 
            daemon=True
        )
        stderr_thread = threading.Thread(
            target=_enqueue_output, 
            args=(process.stderr, "stderr", output_queue, stop_event_ref), 
            daemon=True
        )
        
        stdout_thread.start()
        stderr_thread.start()

        # Wait for process completion or stop signal
        while not stop_event_ref.is_set():
            if process.poll() is not None:
                break
            if not stdout_thread.is_alive() and not stderr_thread.is_alive():
                break
            stop_event_ref.wait(0.1)

        # Clean up threads
        stdout_thread.join(timeout=PROCESS_CONFIG["thread_join_timeout"])
        stderr_thread.join(timeout=PROCESS_CONFIG["thread_join_timeout"])
        
        # Wait for natural completion if not stopped
        if process.poll() is None and not stop_event_ref.is_set():
            process.wait()
            
        return_code = process.returncode if process.poll() is not None else 'N/A (killed)'
        output_queue.put((f"\n--- Return code: {return_code} ---\n", ("info_tag",)))
        
    except FileNotFoundError:
        output_queue.put((f"ERROR: Command '{command_str.split()[0]}' not found.\n", ("error_tag",)))
    except Exception as e:
        output_queue.put((f"WORKER ERROR: {str(e)}\n{traceback.format_exc()}\n", ("error_tag",)))
    finally:
        # Final cleanup
        if process and process.poll() is None and not stop_event_ref.is_set():
            try:
                process.kill()
                process.wait(timeout=PROCESS_CONFIG["thread_join_timeout"])
            except Exception:
                pass
        output_queue.put(("WORKER_THREAD_DONE", None))


def _enqueue_output(stream, stream_type, output_queue, stop_event_ref):
    """
    Read from a stream and put lines into the output queue.
    
    Args:
        stream: The stream to read from (stdout or stderr)
        stream_type (str): Type of stream ("stdout" or "stderr")
        output_queue (queue.Queue): Queue to put output lines
        stop_event_ref (threading.Event): Event to signal stopping
    """
    tag = "stderr_tag" if stream_type == "stderr" else "stdout_tag"
    try:
        for line in iter(stream.readline, ''):
            if stop_event_ref.is_set():
                break
            output_queue.put((line, (tag,)))
    except Exception:
        pass
    finally:
        stream.close()


def stop_process(process_handler, output_queue):
    """
    Stop a running process using appropriate signals/methods for the platform.
    
    Args:
        process_handler (ProcessHandler): Handler containing process info
        output_queue (queue.Queue): Queue for output messages
    """
    proc = process_handler.process
    pgid = process_handler.pgid
    stop_event = process_handler.stop_event

    if not proc and not (process_handler.thread and process_handler.thread.is_alive()):
        output_queue.put(("--- No command to stop. ---\n", ("info_tag",)))
        return

    pid_info = proc.pid if proc else 'N/A'
    pgid_info = pgid if pgid else 'N/A'
    output_queue.put((f"--- Sending stop signal to PID: {pid_info}, PGID: {pgid_info} ---\n", ("info_tag",)))
    
    stop_event.set()

    if proc and proc.poll() is None:
        output_queue.put((f"ATTEMPTING TO STOP PROCESS: PID={proc.pid}, PGID={pgid}\n", ("info_tag",)))
        
        try:
            if platform.system() != "Windows" and pgid is not None:
                _stop_unix_process_group(proc, pgid, output_queue)
            else:
                _stop_windows_or_fallback_process(proc, pgid, output_queue)
                
            output_queue.put((f"--- Process termination sequence for PID {proc.pid} initiated. ---\n", ("info_tag",)))
            
        except ProcessLookupError as ple:
            output_queue.put((f"--- ProcessLookupError (already gone?): {str(ple)} ---\n", ("info_tag",)))
        except Exception as e:
            output_queue.put((f"--- Error during stop sequence: {str(e)} ---\n", ("error_tag",)))
    else:
        output_queue.put((f"--- Stop called, but process already ended or not running. ---\n", ("info_tag",)))


def _stop_unix_process_group(proc, pgid, output_queue):
    """Stop process group on Unix-like systems using SIGTERM then SIGKILL."""
    output_queue.put((f"Using killpg({pgid}, SIGTERM) on Unix-like system.\n", ("info_tag",)))
    
    try:
        os.killpg(pgid, signal.SIGTERM)
        proc.wait(timeout=2)
        
        if proc.poll() is not None:
            output_queue.put((f"Process group {pgid} terminated successfully after SIGTERM.\n", ("info_tag",)))
        else:
            output_queue.put((f"Process group {pgid} did NOT terminate after SIGTERM. Attempting SIGKILL.\n", ("info_tag",)))
            os.killpg(pgid, signal.SIGKILL)
            proc.wait(timeout=1)
            
            if proc.poll() is not None:
                output_queue.put((f"Process group {pgid} terminated successfully after SIGKILL.\n", ("info_tag",)))
            else:
                output_queue.put((f"Process group {pgid} FAILED to terminate after SIGKILL.\n", ("error_tag",)))
                
    except subprocess.TimeoutExpired:
        output_queue.put((f"Timeout waiting for process group {pgid} after SIGTERM. Attempting SIGKILL.\n", ("info_tag",)))
        try:
            os.killpg(pgid, signal.SIGKILL)
            proc.wait(timeout=1)
            
            if proc.poll() is not None:
                output_queue.put((f"Process group {pgid} terminated successfully after SIGKILL (post-timeout).\n", ("info_tag",)))
            else:
                output_queue.put((f"Process group {pgid} FAILED to terminate after SIGKILL (post-timeout).\n", ("error_tag",)))
        except Exception as e_kill_wait:
            output_queue.put((f"Exception waiting after SIGKILL for PGID {pgid}: {str(e_kill_wait)}\n", ("error_tag",)))


def _stop_windows_or_fallback_process(proc, pgid, output_queue):
    """Stop process on Windows or as fallback when no process group available."""
    if pgid is None and platform.system() != "Windows":
        output_queue.put((f"No PGID, attempting to terminate PID {proc.pid} directly (Unix).\n", ("info_tag",)))
    else:
        output_queue.put((f"Attempting to terminate PID {proc.pid} directly (Windows).\n", ("info_tag",)))
    
    try:
        proc.terminate()
        proc.wait(timeout=2)
        
        if proc.poll() is not None:
            output_queue.put((f"Process {proc.pid} terminated successfully after Popen.terminate().\n", ("info_tag",)))
        else:
            output_queue.put((f"Process {proc.pid} did NOT terminate after Popen.terminate(). Attempting Popen.kill().\n", ("info_tag",)))
            proc.kill()
            proc.wait(timeout=1)
            
            if proc.poll() is not None:
                output_queue.put((f"Process {proc.pid} terminated successfully after Popen.kill().\n", ("info_tag",)))
            else:
                output_queue.put((f"Process {proc.pid} FAILED to terminate after Popen.kill().\n", ("error_tag",)))
                
    except subprocess.TimeoutExpired:
        output_queue.put((f"Timeout waiting for process {proc.pid} after Popen.terminate(). Attempting Popen.kill().\n", ("info_tag",)))
        try:
            proc.kill()
            proc.wait(timeout=1)
            
            if proc.poll() is not None:
                output_queue.put((f"Process {proc.pid} terminated successfully after Popen.kill() (post-timeout).\n", ("info_tag",)))
            else:
                output_queue.put((f"Process {proc.pid} FAILED to terminate after Popen.kill() (post-timeout).\n", ("error_tag",)))
        except Exception as e_kill_wait:
            output_queue.put((f"Exception waiting after Popen.kill() for PID {proc.pid}: {str(e_kill_wait)}\n", ("error_tag",))) 