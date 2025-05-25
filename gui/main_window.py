"""
Multi-instance tabbed main window for Project Runner App.
"""

import tkinter as tk
from tkinter import ttk
import queue
import threading

from config.settings import UI_CONFIG, PROJECT_TYPES, PROCESS_CONFIG, MESSAGES, TAB_CONFIG
from gui.widgets import CreateInstanceTab, ProjectInstanceTab
from core.process_manager import ProcessHandler, stream_output_worker, stop_process
from core.port_manager import find_and_kill_process_on_port


class MainWindow:
    """Multi-instance tabbed main window."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(UI_CONFIG["window_title"])
        self.root.geometry("900x700")
        
        # Instance management
        self.instances = {}  # tab_id -> instance data
        self.instance_counters = {"Angular": 0, "Laravel": 0, "Custom": 0}
        self.next_tab_id = 1
        
        # Create tabbed interface
        self._create_notebook()
        self._create_initial_tab()
        self._setup_window_events()
        
    def _create_notebook(self):
        """Create the main notebook widget for tabs."""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Bind tab selection event
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
        
    def _create_initial_tab(self):
        """Create the initial 'Create New Instance' tab."""
        create_frame = tk.Frame(self.notebook)
        self.create_tab = CreateInstanceTab(create_frame, self._create_new_instance)
        
        self.notebook.add(create_frame, text=TAB_CONFIG["create_tab_title"])
        
    def _create_new_instance(self, project_type):
        """Create a new project instance tab."""
        # Increment counter for this project type
        self.instance_counters[project_type] += 1
        instance_number = self.instance_counters[project_type]
        
        # Create new tab frame
        tab_frame = tk.Frame(self.notebook)
        
        # Create project instance
        instance_tab = ProjectInstanceTab(tab_frame, project_type, instance_number)
        
        # Create process handler and output queue for this instance
        process_handler = ProcessHandler()
        output_queue = queue.Queue()
        
        # Store instance data
        tab_id = self.next_tab_id
        self.next_tab_id += 1
        
        self.instances[tab_id] = {
            'tab_frame': tab_frame,
            'instance_tab': instance_tab,
            'process_handler': process_handler,
            'output_queue': output_queue,
            'project_type': project_type,
            'instance_number': instance_number
        }
        
        # Set up callbacks for this instance
        instance_tab.set_callbacks(
            lambda: self._run_command(tab_id),
            lambda: self._stop_command(tab_id)
        )
        
        # Add tab to notebook
        tab_title = instance_tab.get_tab_title()
        self.notebook.add(tab_frame, text=tab_title)
        
        # Switch to the new tab
        self.notebook.select(tab_frame)
        
        # Show success message in output
        instance_tab.output_widget.write_message("", ("clear_previous",))
        instance_tab.output_widget.write_message(MESSAGES["instance_created"] + "\n\n", ("info_tag",))
        instance_tab.output_widget.write_message(MESSAGES["initial_output"], "init_msg_visible_test")
        
    def _run_command(self, tab_id):
        """Run command for specific instance."""
        if tab_id not in self.instances:
            return
            
        instance = self.instances[tab_id]
        instance_tab = instance['instance_tab']
        process_handler = instance['process_handler']
        output_queue = instance['output_queue']
        
        if process_handler.is_running():
            instance_tab.output_widget.write_message(MESSAGES["command_running"], ("error_tag",))
            return

        command = instance_tab.command_entry.get()
        if not command:
            instance_tab.output_widget.write_message(MESSAGES["no_command"], ("error_tag",))
            return
            
        cwd = instance_tab.directory_selector.get()
        project_type = instance['project_type']
        
        # Clear previous output
        instance_tab.output_widget.write_message("", ("clear_previous",))
        instance_tab.output_widget.write_message(MESSAGES["initial_output"], "init_msg_visible_test")
        
        # Check if we need to clear a port first
        project_config = PROJECT_TYPES.get(project_type)
        port_to_clear = project_config.get("port") if project_config else None
        
        if port_to_clear:
            self._run_with_port_clearing(tab_id, command, cwd, port_to_clear, project_type)
        else:
            self._start_command_thread(tab_id, command, cwd)
            
        # Update UI state
        instance_tab.control_buttons.set_run_enabled(False)
        instance_tab.control_buttons.set_stop_enabled(True)
        process_handler.stop_event.clear()
        
    def _run_with_port_clearing(self, tab_id, command, cwd, port, project_type):
        """Run command after clearing the specified port."""
        instance = self.instances[tab_id]
        output_queue = instance['output_queue']
        
        output_queue.put((f"--- Checking port {port} for {project_type} ---\n", ("info_tag",)))
        self._process_queue(tab_id)  # Process the port check message immediately
        
        def port_clear_and_start():
            port_cleared = find_and_kill_process_on_port(port, output_queue)
            if not port_cleared:
                output_queue.put((f"WARNING: Port {port} clear FAILED. Command may not start correctly.\n", ("error_tag",)))
            else:
                output_queue.put((f"INFO: Port {port} check/clear complete.\n", ("info_tag",)))
            
            if command:
                self._start_command_thread(tab_id, command, cwd)
            else:
                self._command_ended_cleanup(tab_id)
                output_queue.put(("No command to run after port clear.", ("info_tag",)))
        
        threading.Thread(target=port_clear_and_start, daemon=True).start()
        
    def _start_command_thread(self, tab_id, command, cwd):
        """Start the command execution thread for specific instance."""
        instance = self.instances[tab_id]
        process_handler = instance['process_handler']
        output_queue = instance['output_queue']
        
        process_handler.thread = threading.Thread(
            target=stream_output_worker,
            args=(command, cwd, output_queue, process_handler.stop_event, process_handler),
            daemon=True
        )
        process_handler.thread.start()
        self.root.after(PROCESS_CONFIG["queue_check_interval"], lambda: self._process_queue(tab_id))
        
    def _stop_command(self, tab_id):
        """Stop the currently running command for specific instance."""
        if tab_id not in self.instances:
            return
            
        instance = self.instances[tab_id]
        process_handler = instance['process_handler']
        output_queue = instance['output_queue']
        
        stop_process(process_handler, output_queue)
        
    def _process_queue(self, tab_id):
        """Process messages from the output queue for specific instance."""
        if tab_id not in self.instances:
            return
            
        instance = self.instances[tab_id]
        instance_tab = instance['instance_tab']
        process_handler = instance['process_handler']
        output_queue = instance['output_queue']
        
        try:
            while True:
                if not self.root.winfo_exists() or not instance_tab.output_widget.winfo_exists():
                    return
                    
                message_item = output_queue.get_nowait()
                message, tags = message_item if isinstance(message_item, tuple) else (message_item, None)
                
                if message == "WORKER_THREAD_DONE":
                    self._command_ended_cleanup(tab_id)
                    break
                else:
                    instance_tab.output_widget.write_message(message, tags)
                    
        except queue.Empty:
            pass
        except tk.TclError:
            self._command_ended_cleanup(tab_id)
            return
        
        # Update stop button state based on actual process status
        if (process_handler.process and 
            process_handler.process.poll() is None and
            instance_tab.control_buttons.winfo_exists()):
            instance_tab.control_buttons.set_stop_enabled(True)
        
        # Continue processing if thread is still alive
        if (process_handler.thread and process_handler.thread.is_alive() and
            self.root.winfo_exists()):
            self.root.after(PROCESS_CONFIG["queue_check_interval"], lambda: self._process_queue(tab_id))
        elif (not output_queue.empty() and self.root.winfo_exists()):
            self.root.after(PROCESS_CONFIG["queue_check_interval"], lambda: self._process_queue(tab_id))
        elif (instance_tab.control_buttons.winfo_exists() and 
              instance_tab.control_buttons.run_button['state'] == tk.DISABLED):
            self._command_ended_cleanup(tab_id)
            
    def _command_ended_cleanup(self, tab_id):
        """Clean up after command execution ends for specific instance."""
        if tab_id not in self.instances:
            return
            
        instance = self.instances[tab_id]
        instance_tab = instance['instance_tab']
        process_handler = instance['process_handler']
        
        if instance_tab.control_buttons.winfo_exists():
            instance_tab.control_buttons.set_run_enabled(True)
            instance_tab.control_buttons.set_stop_enabled(False)
            
        process_handler.reset()
        
        if instance_tab.output_widget.winfo_exists():
            instance_tab.output_widget.write_message(MESSAGES["process_ended"], ("info_tag",))
            
    def _on_tab_changed(self, event):
        """Handle tab selection change."""
        # Could be used for future features like updating window title
        pass
        
    def _setup_window_events(self):
        """Setup window event handlers."""
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
    def _on_closing(self):
        """Handle window closing event."""
        # Stop all running processes
        for tab_id, instance in self.instances.items():
            process_handler = instance['process_handler']
            if process_handler.is_running():
                output_queue = instance['output_queue']
                stop_process(process_handler, output_queue)
                
                # Give a brief moment for graceful shutdown
                if process_handler.thread and process_handler.thread.is_alive():
                    process_handler.thread.join(timeout=PROCESS_CONFIG["graceful_shutdown_timeout"])
                    
        if self.root.winfo_exists():
            self.root.destroy()
            
    def run(self):
        """Start the main application loop."""
        if self.root.winfo_exists():
            self.root.mainloop() 