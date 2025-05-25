import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk
import subprocess
import os
import traceback
import threading
import queue
import platform
import signal # For process group killing

# To store the currently running process and the queue for thread communication
current_process_handler = {
    "process": None,
    "thread": None,
    "stop_event": threading.Event(),
    "pgid": None # To store process group ID on Unix-like systems
}

# --- Port Clearing Function ---
def find_and_kill_process_on_port(port, output_q):
    os_name = platform.system()
    pid_to_kill = None
    found_process = False
    output_q.put((f"INFO: Checking port {port} (OS: {os_name})...\n", ("info_tag",)))
    try:
        if os_name == "Darwin" or os_name == "Linux":
            find_cmd = f"lsof -t -iTCP:{port} -sTCP:LISTEN"
            result = subprocess.run(find_cmd, shell=True, capture_output=True, text=True, timeout=5)
            if result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                pid_to_kill = pids[0]
                found_process = True
        elif os_name == "Windows":
            find_cmd = f'netstat -ano -p TCP | findstr ":{port}" | findstr "LISTENING"'
            result = subprocess.run(find_cmd, shell=True, capture_output=True, text=True, timeout=10)
            if result.stdout.strip():
                lines = result.stdout.strip().split('\n')
                if lines:
                    parts = lines[0].strip().split()
                    if len(parts) >= 4 and parts[0].upper() == "TCP" and parts[-2].upper() == "LISTENING":
                         pid_to_kill = parts[-1]
                         found_process = True
        
        if not found_process:
            output_q.put((f"INFO: No active process on port {port}.\n", ("info_tag",)))
            return True
        
        output_q.put((f"INFO: Found PID {pid_to_kill} on port {port}. Killing...\n", ("info_tag",)))
        if os_name == "Darwin" or os_name == "Linux":
            kill_cmd = f"kill -9 {pid_to_kill}"
        elif os_name == "Windows":
            kill_cmd = f"taskkill /F /PID {pid_to_kill}"
        else:
            output_q.put((f"ERROR: Unsupported OS for killing: {os_name}\n", ("error_tag",)))
            return False
            
        kill_result = subprocess.run(kill_cmd, shell=True, capture_output=True, text=True, timeout=5)
        if kill_result.returncode == 0:
            output_q.put((f"SUCCESS: Killed PID {pid_to_kill}.\n", ("info_tag",)))
            threading.Event().wait(0.5)
            return True
        else:
            err_msg = kill_result.stderr.strip() or kill_result.stdout.strip()
            output_q.put((f"ERROR killing PID {pid_to_kill}: {err_msg}\n", ("error_tag",)))
            return False
    except subprocess.TimeoutExpired:
        output_q.put((f"ERROR: Timeout during port check/kill for port {port}.\n", ("error_tag",)))
        return False
    except Exception as e:
        output_q.put((f"ERROR during port clearing ({port}): {str(e)}\n", ("error_tag",)))
        return False
    return True

def main():
    root = tk.Tk()
    root.title("Project Runner App V5 - Output Test")
    output_queue = queue.Queue()

    # --- Color Scheme --- (Reverting to Black on White for Output)
    label_fg = "black"
    label_bg = "#F0F0F0"
    entry_fg = "black"
    entry_bg = "white"
    # Explicit Black on White for output_text
    output_text_fg = "black"
    output_text_bg = "white"
    output_cursor_bg = "black" # Black cursor on white background

    # --- UI Frames ---
    project_type_frame = tk.Frame(root, pady=2)
    project_type_frame.pack(pady=5, padx=10, fill=tk.X)

    dir_frame = tk.Frame(root, pady=2)
    dir_frame.pack(pady=5, padx=10, fill=tk.X)

    command_frame = tk.Frame(root, pady=2)
    command_frame.pack(pady=5, padx=10, fill=tk.X)

    output_frame = tk.Frame(root, pady=2)
    output_frame.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)

    # --- Project Type Selection ---
    tk.Label(project_type_frame, text="Project Type:", fg=label_fg, bg=label_bg, padx=5).pack(side=tk.LEFT)
    project_type = tk.StringVar(value="Custom")

    def update_command_entry(*args):
        pt = project_type.get()
        command_entry.configure(state='normal', fg=entry_fg, bg=entry_bg)
        command_entry.delete(0, tk.END)
        read_only_bg = "#E0E0E0"
        if pt == "Angular":
            command_entry.insert(0, "ng serve")
            command_entry.configure(state='readonly', fg=entry_fg, readonlybackground=read_only_bg, bg=read_only_bg)
        elif pt == "Laravel":
            command_entry.insert(0, "php artisan serve")
            command_entry.configure(state='readonly', fg=entry_fg, readonlybackground=read_only_bg, bg=read_only_bg)
        else: # Custom
            command_entry.configure(state='normal', fg=entry_fg, bg=entry_bg)

    project_type.trace_add("write", update_command_entry)
    # Using tk.Radiobutton for more control over appearance if ttk is problematic
    tk.Radiobutton(project_type_frame, text="Angular", variable=project_type, value="Angular", indicatoron=0, padx=10, fg=label_fg, selectcolor="#D0D0D0", bg="white").pack(side=tk.RIGHT, padx=2)
    tk.Radiobutton(project_type_frame, text="Laravel", variable=project_type, value="Laravel", indicatoron=0, padx=10, fg=label_fg, selectcolor="#D0D0D0", bg="white").pack(side=tk.RIGHT, padx=2)
    tk.Radiobutton(project_type_frame, text="Custom", variable=project_type, value="Custom", indicatoron=0, padx=10, fg=label_fg, selectcolor="#D0D0D0", bg="white").pack(side=tk.RIGHT, padx=2)
    
    # --- Directory Selection ---
    tk.Label(dir_frame, text="Working Directory:", fg=label_fg, bg=label_bg, padx=5).pack(side=tk.LEFT)
    selected_directory = tk.StringVar(value=os.getcwd())
    dir_label = tk.Label(dir_frame, textvariable=selected_directory, relief=tk.SUNKEN, fg=entry_fg, bg=entry_bg, padx=10, anchor=tk.W)
    dir_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
    browse_button = tk.Button(dir_frame, text="Browse", command=lambda: selected_directory.set(filedialog.askdirectory(initialdir=selected_directory.get()) or selected_directory.get()))
    browse_button.pack(side=tk.RIGHT, padx=5)

    # --- Command Input ---
    tk.Label(command_frame, text="Command:", fg=label_fg, bg=label_bg, padx=5).pack(side=tk.LEFT)
    command_entry = tk.Entry(command_frame, width=60, fg=entry_fg, bg=entry_bg, relief=tk.SUNKEN)
    command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
    update_command_entry() # Initialize based on default project type

    # --- Output Display ---
    tk.Label(output_frame, text="Output:", fg=label_fg, bg=label_bg, padx=5).pack(anchor=tk.NW)
    output_text = scrolledtext.ScrolledText(
        output_frame, height=15, width=70, wrap=tk.WORD, relief=tk.SUNKEN, 
        # Explicitly set fg, bg for the ScrolledText widget itself
        fg=output_text_fg, bg=output_text_bg, insertbackground=output_cursor_bg
    )
    # Attempt to configure the internal Text widget directly if ScrolledText doesn't propagate all
    # This is usually not needed if ScrolledText is well-behaved, but good for testing
    try:
        # The internal Text widget is often named 'text' or is the first child of type Text
        # A more robust way might be to find it by class if direct access fails
        internal_text_widget = output_text.component('text') # This is a common way for ttk.Notebook's tabs, might work for ScrolledText's component
        if internal_text_widget:
             internal_text_widget.config(fg=output_text_fg, bg=output_text_bg, insertbackground=output_cursor_bg)
    except (AttributeError, tk.TclError):
        # Fallback if .component('text') isn't available or fails
        # Most simple ScrolledText wrappers set fg/bg on the main Text widget directly.
        # The ScrolledText constructor itself should handle fg, bg, insertbackground.
        pass 

    output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0,5))
    output_text.configure(state='normal')
    # Using a very simple tag for the initial message
    output_text.tag_config("init_msg_visible_test", foreground=output_text_fg, background=output_text_bg)
    output_text.insert(tk.END, "OUTPUT VISIBILITY TEST (Black on White). Waiting for command...\n-------------------------------------\n", "init_msg_visible_test")
    output_text.configure(state='disabled')

    # --- Tags for Output Text Styling (Simplified to black on white for now) ---
    # All tags will use the default output_text_fg and output_text_bg for now.
    output_text.tag_config("error_tag", foreground=output_text_fg) 
    output_text.tag_config("info_tag", foreground=output_text_fg, font=("Helvetica", "9", "bold"))
    output_text.tag_config("stdout_tag", foreground=output_text_fg)
    output_text.tag_config("stderr_tag", foreground=output_text_fg) # Will make stderr red later if base is visible

    def _write_to_output(message, tags=None):
        if not output_text.winfo_exists(): return
        output_text.configure(state='normal')
        if tags == ("clear_previous",):
            output_text.delete(1.0, tk.END)
        else:
            # Ensure a default tag if none, or use provided
            effective_tags = tags if tags else ("stdout_tag",)
            output_text.insert(tk.END, message, effective_tags)
        output_text.configure(state='disabled')
        output_text.see(tk.END)

    def command_ended_cleanup():
        if run_button.winfo_exists(): run_button.config(state=tk.NORMAL)
        if stop_button.winfo_exists(): stop_button.config(state=tk.DISABLED)
        current_process_handler["process"] = None
        current_process_handler["thread"] = None
        current_process_handler["pgid"] = None
        current_process_handler["stop_event"].clear()
        if output_text.winfo_exists(): _write_to_output("\n--- Process Ended/Stopped ---\n", ("info_tag",))

    def stream_output_worker(command_str, cwd_str, q, stop_event_ref):
        process = None
        current_process_handler["pgid"] = None # Reset pgid for new process
        try:
            q.put((f"Attempting: {command_str} in {cwd_str}\n\n", ("info_tag",)))
            preexec_fn_to_use = None
            start_new_session_flag = False
            if platform.system() != "Windows":
                # preexec_fn=os.setsid or start_new_session=True for non-Windows
                # start_new_session is simpler and preferred for Python 3.2+
                start_new_session_flag = True 
            
            process = subprocess.Popen(
                command_str, shell=True, cwd=cwd_str,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, bufsize=1, universal_newlines=True, errors='replace',
                start_new_session=start_new_session_flag # Important for process group killing
            )
            current_process_handler["process"] = process
            if platform.system() != "Windows":
                try:
                    current_process_handler["pgid"] = os.getpgid(process.pid)
                except OSError: # Process might have died quickly
                    current_process_handler["pgid"] = None

            pgid_info = f' (PGID: {current_process_handler["pgid"]})' if current_process_handler["pgid"] else ''
            q.put((f"PID: {process.pid}{pgid_info}. Streaming output...\n--------------------------\n", ("info_tag",)))

            def enqueue_output(stream, stream_type, q_ref, stop_ev_ref):
                tag = "stderr_tag" if stream_type == "stderr" else "stdout_tag"
                try:
                    for line in iter(stream.readline, ''):
                        if stop_ev_ref.is_set(): break
                        q_ref.put((line, (tag,)))
                except Exception: pass
                finally: stream.close()

            stdout_thread = threading.Thread(target=enqueue_output, args=(process.stdout, "stdout", q, stop_event_ref), daemon=True)
            stderr_thread = threading.Thread(target=enqueue_output, args=(process.stderr, "stderr", q, stop_event_ref), daemon=True)
            stdout_thread.start()
            stderr_thread.start()

            while not stop_event_ref.is_set():
                if process.poll() is not None: break
                if not stdout_thread.is_alive() and not stderr_thread.is_alive(): break
                stop_event_ref.wait(0.1)
            
            # Stop handling is now in stop_running_command or on_closing
            # This worker just waits or exits if stop_event is set.

            stdout_thread.join(timeout=1)
            stderr_thread.join(timeout=1)
            if process.poll() is None: 
                # If not stopped by stop_event, wait for natural completion
                if not stop_event_ref.is_set():
                    process.wait()
            q.put((f"\n--- Return code: {process.returncode if process.poll() is not None else 'N/A (killed)'} ---\n", ("info_tag",)))
        except FileNotFoundError:
            q.put((f"ERROR: Command '{command_str.split()[0]}' not found.\n", ("error_tag",)))
        except Exception as e:
            q.put((f"WORKER ERROR: {str(e)}\n{traceback.format_exc()}\n", ("error_tag",)))
        finally:
            # Ensure the process is cleaned up if it's still running and wasn't externally killed
            if process and process.poll() is None and not stop_event_ref.is_set():
                try:
                    process.kill() # Final attempt to kill if not stopped
                    process.wait(timeout=1) # Give it a moment
                except Exception: pass # Ignore errors during this final cleanup
            q.put(("WORKER_THREAD_DONE", None))

    def process_queue():
        try:
            while True:
                if not root.winfo_exists() or not output_text.winfo_exists(): return
                message_item = output_queue.get_nowait()
                message, tags = message_item if isinstance(message_item, tuple) else (message_item, None)
                if message == "WORKER_THREAD_DONE":
                    command_ended_cleanup()
                    break
                else:
                    _write_to_output(message, tags)
        except queue.Empty: pass
        except tk.TclError: command_ended_cleanup(); return
        
        # Ensure Stop button state reflects actual process status
        if current_process_handler["process"] and current_process_handler["process"].poll() is None:
            # Process is still running, ensure Stop button is enabled
            if stop_button.winfo_exists() and stop_button['state'] != tk.NORMAL:
                stop_button.config(state=tk.NORMAL)
        
        if current_process_handler["thread"] and current_process_handler["thread"].is_alive():
            if root.winfo_exists(): root.after(100, process_queue)
        elif not (current_process_handler["thread"] and current_process_handler["thread"].is_alive()):
             if not output_queue.empty() and root.winfo_exists(): root.after(100, process_queue)
             elif run_button.winfo_exists() and run_button['state'] == tk.DISABLED: command_ended_cleanup()

    def run_command_async():
        if current_process_handler["process"] and current_process_handler["process"].poll() is None:
            _write_to_output("Command already running.\n", ("error_tag",))
            return

        command = command_entry.get()
        cwd = selected_directory.get()
        _write_to_output("", ("clear_previous",)) 
        _write_to_output("OUTPUT VISIBILITY TEST (Black on White). Waiting for command...\n-------------------------------------\n", "init_msg_visible_test") 

        pt = project_type.get()
        port_to_clear = None
        if pt == "Angular": port_to_clear = 4200
        elif pt == "Laravel": port_to_clear = 8000

        def start_main_command_thread():
            current_process_handler["thread"] = threading.Thread(
                target=stream_output_worker, 
                args=(command, cwd, output_queue, current_process_handler["stop_event"]),
                daemon=True
            )
            current_process_handler["thread"].start()
            if root.winfo_exists(): root.after(100, process_queue)

        if port_to_clear:
            output_queue.put((f"--- Checking port {port_to_clear} for {pt} ---\n", ("info_tag",)))
            if root.winfo_exists(): root.after(10, process_queue)
            
            def port_clear_worker_and_start():
                port_cleared_successfully = find_and_kill_process_on_port(port_to_clear, output_queue)
                if not port_cleared_successfully:
                    output_queue.put((f"WARNING: Port {port_to_clear} clear FAILED. Command may not start correctly.\n", ("error_tag",)))
                else:
                    output_queue.put((f"INFO: Port {port_to_clear} check/clear complete.\n", ("info_tag",)))
                if command:
                     start_main_command_thread()
                else:
                    command_ended_cleanup() 
                    output_queue.put(("No command to run after port clear.", ("info_tag",)))
            
            threading.Thread(target=port_clear_worker_and_start, daemon=True).start()
        elif command: 
            start_main_command_thread()
        else:
            _write_to_output("No command entered.\n", ("error_tag",))
            return 

        if command: 
            run_button.config(state=tk.DISABLED)
            stop_button.config(state=tk.NORMAL)
            current_process_handler["stop_event"].clear()

    def stop_running_command():
        proc = current_process_handler["process"]
        pgid = current_process_handler["pgid"]
        stop_event = current_process_handler["stop_event"]

        if not proc and not (current_process_handler["thread"] and current_process_handler["thread"].is_alive()):
            if output_text.winfo_exists(): _write_to_output("--- No command to stop. ---\n", ("info_tag",))
            command_ended_cleanup() 
            return

        if output_text.winfo_exists(): _write_to_output(f"--- Sending stop signal to PID: {proc.pid if proc else 'N/A'}, PGID: {pgid if pgid else 'N/A'} ---\n", ("info_tag",))
        stop_event.set() 

        if proc and proc.poll() is None: 
            output_queue.put((f"ATTEMPTING TO STOP PROCESS: PID={proc.pid}, PGID={pgid}\n", ("info_tag",)))
            try:
                if platform.system() != "Windows" and pgid is not None:
                    output_queue.put((f"Using killpg({pgid}, SIGTERM) on Unix-like system.\n", ("info_tag",)))
                    os.killpg(pgid, signal.SIGTERM) 
                    try:
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
                        os.killpg(pgid, signal.SIGKILL) 
                        try:
                            proc.wait(timeout=1)
                            if proc.poll() is not None:
                                output_queue.put((f"Process group {pgid} terminated successfully after SIGKILL (post-timeout).\n", ("info_tag",)))
                            else:
                                output_queue.put((f"Process group {pgid} FAILED to terminate after SIGKILL (post-timeout).\n", ("error_tag",)))
                        except Exception as e_kill_wait:
                             output_queue.put((f"Exception waiting after SIGKILL for PGID {pgid}: {str(e_kill_wait)}\n", ("error_tag",)))
                elif platform.system() == "Windows" or pgid is None: 
                    if pgid is None and platform.system() != "Windows":
                        output_queue.put((f"No PGID, attempting to terminate PID {proc.pid} directly (Unix).\n", ("info_tag",)))
                    else:
                        output_queue.put((f"Attempting to terminate PID {proc.pid} directly (Windows).\n", ("info_tag",)))
                    proc.terminate()
                    try:
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
                        proc.kill()
                        try:
                            proc.wait(timeout=1)
                            if proc.poll() is not None:
                                output_queue.put((f"Process {proc.pid} terminated successfully after Popen.kill() (post-timeout).\n", ("info_tag",)))
                            else:
                                output_queue.put((f"Process {proc.pid} FAILED to terminate after Popen.kill() (post-timeout).\n", ("error_tag",)))
                        except Exception as e_kill_wait:
                            output_queue.put((f"Exception waiting after Popen.kill() for PID {proc.pid}: {str(e_kill_wait)}\n", ("error_tag",)))
                output_queue.put((f"--- Process termination sequence for PID {proc.pid} initiated. Check worker thread for final status. ---\n", ("info_tag",)))
            except ProcessLookupError as ple:
                 output_queue.put((f"--- ProcessLookupError during stop sequence for PGID {pgid} / PID {proc.pid} (already gone?): {str(ple)} ---\n", ("info_tag",)))
            except Exception as e:
                output_queue.put((f"--- Error during stop sequence for PGID {pgid} / PID {proc.pid}: {str(e)} ---\n", ("error_tag",)))
        else: 
            output_queue.put((f"--- Stop called, but process (PID: {proc.pid if proc else 'N/A'}) already ended or not running. ---\n", ("info_tag",)))
        
        # Don't disable the stop button here - let process_queue manage it based on actual process status

    # --- Buttons ---
    button_frame = tk.Frame(root)
    button_frame.pack(pady=10, padx=10, fill=tk.X, side=tk.BOTTOM) # Ensure buttons are at the very bottom
    run_button = tk.Button(button_frame, text="Run Command", command=run_command_async)
    run_button.pack(side=tk.LEFT, padx=5)
    stop_button = tk.Button(button_frame, text="Stop Command", command=stop_running_command, state=tk.DISABLED)
    stop_button.pack(side=tk.LEFT, padx=5)
    
    def on_closing():
        if current_process_handler["process"] and current_process_handler["process"].poll() is None or \
           (current_process_handler["thread"] and current_process_handler["thread"].is_alive()):
            stop_running_command() # Attempt graceful shutdown
            # Give a very brief moment for threads/processes to react before destroying window
            if current_process_handler["thread"] and current_process_handler["thread"].is_alive():
                current_process_handler["thread"].join(timeout=0.5)
        if root.winfo_exists(): root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    if root.winfo_exists(): root.mainloop()

if __name__ == "__main__":
    main() 