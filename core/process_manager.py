"""
Process management functionality for executing and controlling commands.
Optimized for better performance and resource management.
"""

import subprocess
import threading
import platform
import signal
import os
import traceback
import time
import weakref
from collections import deque
from config.settings import PROCESS_CONFIG, PERFORMANCE_CONFIG


class OptimizedProcessHandler:
    """
    Optimized process handler with better resource management and performance.
    """
    
    def __init__(self):
        self.process = None
        self.thread = None
        self.stop_event = threading.Event()
        self.pgid = None
        self._output_buffer = deque(maxlen=PERFORMANCE_CONFIG["max_output_lines"])
        self._last_cleanup = time.time()
        
    def reset(self):
        """Reset the handler and clean up resources."""
        self._cleanup_resources()
        self.process = None
        self.thread = None
        self.pgid = None
        self.stop_event.clear()
        self._output_buffer.clear()
        
    def _cleanup_resources(self):
        """Clean up system resources."""
        if self.process:
            try:
                if self.process.poll() is None:
                    self.process.terminate()
                    self.process.wait(timeout=1)
            except (subprocess.TimeoutExpired, ProcessLookupError):
                try:
                    self.process.kill()
                except ProcessLookupError:
                    pass
            finally:
                self.process = None
                
        if self.thread and self.thread.is_alive():
            self.stop_event.set()
            self.thread.join(timeout=PROCESS_CONFIG["thread_join_timeout"])
            
    def is_running(self):
        """Check if process is currently running with optimized checks."""
        # Quick check first
        if not self.process and not self.thread:
            return False
            
        # More expensive checks only if needed
        process_running = self.process and self.process.poll() is None
        thread_running = self.thread and self.thread.is_alive()
        
        return process_running or thread_running
        
    def get_memory_usage(self):
        """Get approximate memory usage of the process."""
        if not self.process:
            return 0
        try:
            import psutil
            proc = psutil.Process(self.process.pid)
            return proc.memory_info().rss
        except (ImportError, psutil.NoSuchProcess):
            return 0
            
    def should_cleanup(self):
        """Check if cleanup is needed based on time interval."""
        current_time = time.time()
        if current_time - self._last_cleanup > PERFORMANCE_CONFIG["memory_cleanup_interval"]:
            self._last_cleanup = current_time
            return True
        return False


# Keep backward compatibility
ProcessHandler = OptimizedProcessHandler


class OutputBuffer:
    """Optimized output buffer with memory management."""
    
    def __init__(self, max_size=PERFORMANCE_CONFIG["max_output_lines"]):
        self._buffer = deque(maxlen=max_size)
        self._lock = threading.Lock()
        
    def add(self, message, tags=None):
        """Add message to buffer thread-safely."""
        with self._lock:
            self._buffer.append((message, tags, time.time()))
            
    def get_recent(self, count=None):
        """Get recent messages from buffer."""
        with self._lock:
            if count is None:
                return list(self._buffer)
            return list(self._buffer)[-count:]
            
    def clear(self):
        """Clear the buffer."""
        with self._lock:
            self._buffer.clear()
            
    def size(self):
        """Get current buffer size."""
        return len(self._buffer)


def stream_output_worker(command_str, cwd_str, output_queue, stop_event_ref, process_handler):
    """
    Optimized worker function with better resource management and performance.
    """
    process = None
    process_handler.pgid = None
    output_buffer = OutputBuffer()
    
    try:
        output_queue.put((f"Attempting: {command_str} in {cwd_str}\n\n", ("info_tag",)))
        
        # Configure process creation with optimizations
        start_new_session_flag = platform.system() != "Windows"
        
        # Use optimized buffer size
        process = subprocess.Popen(
            command_str, shell=True, cwd=cwd_str,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, bufsize=PERFORMANCE_CONFIG["output_buffer_size"], 
            universal_newlines=True, errors='replace',
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

        # Start optimized output streaming threads
        stdout_thread = threading.Thread(
            target=_optimized_enqueue_output, 
            args=(process.stdout, "stdout", output_queue, stop_event_ref, output_buffer), 
            daemon=True
        )
        stderr_thread = threading.Thread(
            target=_optimized_enqueue_output, 
            args=(process.stderr, "stderr", output_queue, stop_event_ref, output_buffer), 
            daemon=True
        )
        
        stdout_thread.start()
        stderr_thread.start()

        # Optimized waiting loop with periodic cleanup
        last_cleanup = time.time()
        while not stop_event_ref.is_set():
            if process.poll() is not None:
                break
            if not stdout_thread.is_alive() and not stderr_thread.is_alive():
                break
                
            # Periodic cleanup to prevent memory leaks
            current_time = time.time()
            if current_time - last_cleanup > PERFORMANCE_CONFIG["memory_cleanup_interval"]:
                _cleanup_dead_threads()
                last_cleanup = current_time
                
            stop_event_ref.wait(0.1)

        # Clean up threads with timeout
        stdout_thread.join(timeout=PROCESS_CONFIG["thread_join_timeout"])
        stderr_thread.join(timeout=PROCESS_CONFIG["thread_join_timeout"])
        
        # Wait for natural completion if not stopped
        if process.poll() is None and not stop_event_ref.is_set():
            try:
                process.wait(timeout=PROCESS_CONFIG["process_kill_timeout"])
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=1)
            
        return_code = process.returncode if process.poll() is not None else 'N/A (killed)'
        output_queue.put((f"\n--- Return code: {return_code} ---\n", ("info_tag",)))
        
    except FileNotFoundError:
        output_queue.put((f"ERROR: Command '{command_str.split()[0]}' not found.\n", ("error_tag",)))
    except Exception as e:
        output_queue.put((f"WORKER ERROR: {str(e)}\n{traceback.format_exc()}\n", ("error_tag",)))
    finally:
        # Optimized cleanup
        _cleanup_process(process, stop_event_ref)
        output_queue.put(("WORKER_THREAD_DONE", None))


def _optimized_enqueue_output(stream, stream_type, output_queue, stop_event_ref, output_buffer):
    """
    Optimized output reading with batching and memory management.
    """
    tag = "stderr_tag" if stream_type == "stderr" else "stdout_tag"
    batch_buffer = []
    batch_size = PERFORMANCE_CONFIG["ui_update_batch_size"]
    
    try:
        for line in iter(stream.readline, ''):
            if stop_event_ref.is_set():
                break
                
            # Add to output buffer for history
            output_buffer.add(line, tag)
            
            # Batch output for better UI performance
            batch_buffer.append((line, (tag,)))
            
            if len(batch_buffer) >= batch_size:
                # Send batch to UI
                for item in batch_buffer:
                    output_queue.put(item)
                batch_buffer.clear()
                
        # Send remaining items in batch
        for item in batch_buffer:
            output_queue.put(item)
            
    except Exception:
        pass
    finally:
        try:
            stream.close()
        except:
            pass


def _cleanup_process(process, stop_event_ref):
    """Optimized process cleanup."""
    if not process:
        return
        
    try:
        if process.poll() is None and not stop_event_ref.is_set():
            process.terminate()
            try:
                process.wait(timeout=PROCESS_CONFIG["thread_join_timeout"])
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=1)
    except (ProcessLookupError, OSError):
        pass


def _cleanup_dead_threads():
    """Clean up dead thread references to prevent memory leaks."""
    import gc
    gc.collect()


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