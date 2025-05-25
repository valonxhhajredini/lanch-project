"""
Main window and application logic for Project Runner App.
"""

import tkinter as tk
import queue
import threading
import os

from config.settings import UI_CONFIG, PROJECT_TYPES, PROCESS_CONFIG, MESSAGES
from gui.widgets import (
    OutputTextWidget, ProjectTypeSelector, DirectorySelector, 
    CommandEntry, ControlButtons
)
from core.process_manager import ProcessHandler, stream_output_worker, stop_process
from core.port_manager import find_and_kill_process_on_port


class MainWindow:
    """Main application window that coordinates all components."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(UI_CONFIG["window_title"])
        
        # Initialize core components
        self.output_queue = queue.Queue()
        self.process_handler = ProcessHandler()
        
        # Initialize UI components
        self._create_frames()
        self._create_widgets()
        self._setup_window_events()
        
    def _create_frames(self):
        """Create the main layout frames."""
        self.project_type_frame = tk.Frame(self.root, pady=2)
        self.project_type_frame.pack(pady=5, padx=10, fill=tk.X)

        self.dir_frame = tk.Frame(self.root, pady=2)
        self.dir_frame.pack(pady=5, padx=10, fill=tk.X)

        self.command_frame = tk.Frame(self.root, pady=2)
        self.command_frame.pack(pady=5, padx=10, fill=tk.X)

        self.output_frame = tk.Frame(self.root, pady=2)
        self.output_frame.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)

        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(pady=10, padx=10, fill=tk.X, side=tk.BOTTOM)
        
    def _create_widgets(self):
        """Create and configure all UI widgets."""
        # Project type selector
        self.project_selector = ProjectTypeSelector(
            self.project_type_frame, 
            on_change_callback=self._on_project_type_change
        )
        
        # Directory selector
        self.directory_selector = DirectorySelector(self.dir_frame)
        
        # Command entry
        self.command_entry = CommandEntry(self.command_frame)
        
        # Output display
        tk.Label(
            self.output_frame, 
            text="Output:", 
            fg=UI_CONFIG["colors"]["label_fg"], 
            bg=UI_CONFIG["colors"]["label_bg"], 
            padx=5
        ).pack(anchor=tk.NW)
        
        self.output_widget = OutputTextWidget(self.output_frame)
        self.output_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0,5))
        
        # Control buttons
        self.control_buttons = ControlButtons(
            self.button_frame,
            run_callback=self._run_command,
            stop_callback=self._stop_command
        )
        
        # Initialize command entry based on default project type
        self._on_project_type_change(self.project_selector.get())
        
    def _setup_window_events(self):
        """Setup window event handlers."""
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
    def _on_project_type_change(self, project_type):
        """Handle project type selection change."""
        self.command_entry.update_for_project_type(project_type)
        
    def _run_command(self):
        """Start running the selected command."""
        if self.process_handler.is_running():
            self.output_widget.write_message(MESSAGES["command_running"], ("error_tag",))
            return

        command = self.command_entry.get()
        if not command:
            self.output_widget.write_message(MESSAGES["no_command"], ("error_tag",))
            return
            
        cwd = self.directory_selector.get()
        project_type = self.project_selector.get()
        
        # Clear previous output
        self.output_widget.write_message("", ("clear_previous",))
        self.output_widget.write_message(MESSAGES["initial_output"], "init_msg_visible_test")
        
        # Check if we need to clear a port first
        project_config = PROJECT_TYPES.get(project_type)
        port_to_clear = project_config.get("port") if project_config else None
        
        if port_to_clear:
            self._run_with_port_clearing(command, cwd, port_to_clear, project_type)
        else:
            self._start_command_thread(command, cwd)
            
        # Update UI state
        self.control_buttons.set_run_enabled(False)
        self.control_buttons.set_stop_enabled(True)
        self.process_handler.stop_event.clear()
        
    def _run_with_port_clearing(self, command, cwd, port, project_type):
        """Run command after clearing the specified port."""
        self.output_queue.put((f"--- Checking port {port} for {project_type} ---\n", ("info_tag",)))
        self._process_queue()  # Process the port check message immediately
        
        def port_clear_and_start():
            port_cleared = find_and_kill_process_on_port(port, self.output_queue)
            if not port_cleared:
                self.output_queue.put((f"WARNING: Port {port} clear FAILED. Command may not start correctly.\n", ("error_tag",)))
            else:
                self.output_queue.put((f"INFO: Port {port} check/clear complete.\n", ("info_tag",)))
            
            if command:
                self._start_command_thread(command, cwd)
            else:
                self._command_ended_cleanup()
                self.output_queue.put(("No command to run after port clear.", ("info_tag",)))
        
        threading.Thread(target=port_clear_and_start, daemon=True).start()
        
    def _start_command_thread(self, command, cwd):
        """Start the command execution thread."""
        self.process_handler.thread = threading.Thread(
            target=stream_output_worker,
            args=(command, cwd, self.output_queue, self.process_handler.stop_event, self.process_handler),
            daemon=True
        )
        self.process_handler.thread.start()
        self.root.after(PROCESS_CONFIG["queue_check_interval"], self._process_queue)
        
    def _stop_command(self):
        """Stop the currently running command."""
        stop_process(self.process_handler, self.output_queue)
        
    def _process_queue(self):
        """Process messages from the output queue and update the UI."""
        try:
            while True:
                if not self.root.winfo_exists() or not self.output_widget.winfo_exists():
                    return
                    
                message_item = self.output_queue.get_nowait()
                message, tags = message_item if isinstance(message_item, tuple) else (message_item, None)
                
                if message == "WORKER_THREAD_DONE":
                    self._command_ended_cleanup()
                    break
                else:
                    self.output_widget.write_message(message, tags)
                    
        except queue.Empty:
            pass
        except tk.TclError:
            self._command_ended_cleanup()
            return
        
        # Update stop button state based on actual process status
        if (self.process_handler.process and 
            self.process_handler.process.poll() is None and
            self.control_buttons.winfo_exists()):
            self.control_buttons.set_stop_enabled(True)
        
        # Continue processing if thread is still alive
        if (self.process_handler.thread and self.process_handler.thread.is_alive() and
            self.root.winfo_exists()):
            self.root.after(PROCESS_CONFIG["queue_check_interval"], self._process_queue)
        elif (not self.output_queue.empty() and self.root.winfo_exists()):
            self.root.after(PROCESS_CONFIG["queue_check_interval"], self._process_queue)
        elif (self.control_buttons.winfo_exists() and 
              not self.control_buttons.run_button.winfo_exists() or 
              self.control_buttons.run_button['state'] == tk.DISABLED):
            self._command_ended_cleanup()
            
    def _command_ended_cleanup(self):
        """Clean up after command execution ends."""
        if self.control_buttons.winfo_exists():
            self.control_buttons.set_run_enabled(True)
            self.control_buttons.set_stop_enabled(False)
            
        self.process_handler.reset()
        
        if self.output_widget.winfo_exists():
            self.output_widget.write_message(MESSAGES["process_ended"], ("info_tag",))
            
    def _on_closing(self):
        """Handle window closing event."""
        if self.process_handler.is_running():
            stop_process(self.process_handler, self.output_queue)
            
            # Give a brief moment for graceful shutdown
            if self.process_handler.thread and self.process_handler.thread.is_alive():
                self.process_handler.thread.join(timeout=PROCESS_CONFIG["graceful_shutdown_timeout"])
                
        if self.root.winfo_exists():
            self.root.destroy()
            
    def run(self):
        """Start the main application loop."""
        if self.root.winfo_exists():
            self.root.mainloop() 