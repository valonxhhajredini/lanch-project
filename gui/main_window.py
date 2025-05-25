"""
Sidebar-based main window for Project Runner App.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import queue
import threading
import os

from config.settings import UI_CONFIG, PROJECT_TYPES, PROCESS_CONFIG, MESSAGES, PROJECT_CONFIG, STATUS_CONFIG, get_current_theme, set_theme
from gui.widgets import CreateInstanceTab, ProjectInstanceTab, ProjectSidebar
from core.process_manager import ProcessHandler, stream_output_worker, stop_process
from core.port_manager import find_and_kill_process_on_port
from core.database import get_database


class MainWindow:
    """Sidebar-based main window with project list and status indicators."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(UI_CONFIG["window_title"])
        self.root.geometry("1100x700")
        
        # Database connection
        self.db = get_database()
        
        # Theme management
        self.theme = get_current_theme()
        self._load_saved_theme()
        
        # Instance management
        self.instances = {}  # project_id -> instance data
        self.instance_counters = {"Angular": 0, "Laravel": 0, "Custom": 0}
        self.next_project_id = 1
        self.current_project_id = None
        
        # Create main layout
        self._create_layout()
        self._setup_window_events()
        self._apply_theme()
        
        # Load saved projects
        self._load_saved_projects()
        
    def _create_layout(self):
        """Create the main layout with sidebar and content area."""
        # Create sidebar
        self.sidebar = ProjectSidebar(
            self.root,
            create_callback=self._show_create_dialog,
            select_callback=self._on_project_select,
            delete_callback=self._on_project_delete,
            theme_callback=self._on_theme_change,
            run_callback=self._run_command,
            stop_callback=self._stop_command
        )
        
        # Create main content area
        self.content_frame = tk.Frame(self.root)
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Show welcome screen initially
        self._show_welcome_screen()
        
    def _apply_theme(self):
        """Apply current theme to main window."""
        self.theme = get_current_theme()
        
        # Main window
        self.root.configure(bg=self.theme["main"]["bg"])
        
        # Content frame
        self.content_frame.configure(bg=self.theme["content"]["bg"])
        
    def _load_saved_theme(self):
        """Load saved theme from database."""
        saved_theme = self.db.load_app_setting("current_theme", "light")
        if saved_theme in ["light", "dark"]:
            set_theme(saved_theme)
            self.theme = get_current_theme()
            
    def _save_current_theme(self):
        """Save current theme to database."""
        from config.settings import CURRENT_THEME
        self.db.save_app_setting("current_theme", CURRENT_THEME)
        
    def _on_theme_change(self, new_theme):
        """Handle theme change from sidebar."""
        self._apply_theme()
        self._save_current_theme()
        
        # Refresh all project instance tabs
        for project_id, instance in self.instances.items():
            if instance['instance_tab']:
                instance['instance_tab'].refresh_theme()
        
        # Refresh current content
        if self.current_project_id:
            self._on_project_select(self.current_project_id)
        else:
            self._show_welcome_screen()
        
    def _show_welcome_screen(self):
        """Show welcome screen when no project is selected."""
        self._clear_content()
        
        welcome_frame = tk.Frame(self.content_frame, bg=self.theme["content"]["bg"])
        welcome_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=50)
        
        # Welcome message
        tk.Label(
            welcome_frame,
            text="Welcome to Project Runner!",
            font=("SF Pro Display", 28, "bold"),
            fg=self.theme["content"]["fg"],
            bg=self.theme["content"]["bg"]
        ).pack(pady=(50, 20))
        
        tk.Label(
            welcome_frame,
            text="Create your first project to get started",
            font=("SF Pro Display", 16),
            fg=self.theme["content"]["fg"],
            bg=self.theme["content"]["bg"]
        ).pack(pady=(0, 30))
        
        # Large create button
        create_btn = tk.Button(
            welcome_frame,
            text="+ Create New Project",
            command=self._show_create_dialog,
            font=("SF Pro Display", 16, "bold"),
            bg=self.theme["buttons"]["success_bg"],
            fg=self.theme["buttons"]["success_fg"],
            padx=40,
            pady=15,
            relief=tk.FLAT,
            cursor="hand2"
        )
        create_btn.pack(pady=20)
        
        # Features list
        features_frame = tk.Frame(welcome_frame, bg=self.theme["content"]["bg"])
        features_frame.pack(pady=30)
        
        tk.Label(
            features_frame,
            text="Features:",
            font=("SF Pro Display", 14, "bold"),
            fg=self.theme["content"]["fg"],
            bg=self.theme["content"]["bg"]
        ).pack(anchor=tk.W)
        
        features = [
            "• Run multiple projects simultaneously",
            "• Real-time output streaming", 
            "• Automatic port management",
            "• Support for Angular, Laravel, and Custom projects",
            "• Modern dark and light themes"
        ]
        
        for feature in features:
            tk.Label(
                features_frame,
                text=feature,
                font=("SF Pro Display", 12),
                fg=self.theme["content"]["fg"],
                bg=self.theme["content"]["bg"]
            ).pack(anchor=tk.W, pady=3)
            
    def _show_create_dialog(self):
        """Show create new project dialog."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Create New Project")
        dialog.geometry("450x550")  # Increased height even more
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (dialog.winfo_screenheight() // 2) - (550 // 2)
        dialog.geometry(f"450x550+{x}+{y}")
        
        # Apply theme to dialog
        dialog.configure(bg=self.theme["content"]["bg"])
        
        # Create a container frame that fills the dialog
        container = tk.Frame(dialog, bg=self.theme["content"]["bg"])
        container.pack(fill=tk.BOTH, expand=True)
        
        # Main content frame (scrollable content area)
        main_frame = tk.Frame(container, bg=self.theme["content"]["bg"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=(20, 0))
        
        # Button frame at the bottom (fixed position)
        bottom_frame = tk.Frame(container, bg=self.theme["content"]["bg"])
        bottom_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=30, pady=(10, 20))
        
        tk.Label(
            main_frame,
            text="Create New Project",
            font=("SF Pro Display", 18, "bold"),
            fg=self.theme["content"]["fg"],
            bg=self.theme["content"]["bg"]
        ).pack(pady=(0, 20))
        
        # Project name field
        tk.Label(
            main_frame,
            text="Project Name:",
            font=("SF Pro Display", 13, "bold"),
            fg=self.theme["content"]["fg"],
            bg=self.theme["content"]["bg"]
        ).pack(anchor=tk.W, pady=(0, 8))
        
        project_name_entry = tk.Entry(
            main_frame,
            font=("SF Pro Display", 12),
            fg=self.theme["content"]["input_fg"],
            bg=self.theme["content"]["input_bg"],
            relief=tk.FLAT,
            borderwidth=2,
            highlightthickness=1,
            highlightcolor=self.theme["colors"]["primary"]
        )
        project_name_entry.pack(fill=tk.X, pady=(0, 20))
        project_name_entry.insert(0, "My Awesome Project")
        project_name_entry.select_range(0, tk.END)
        
        # Project description field
        tk.Label(
            main_frame,
            text="Description (optional):",
            font=("SF Pro Display", 13, "bold"),
            fg=self.theme["content"]["fg"],
            bg=self.theme["content"]["bg"]
        ).pack(anchor=tk.W, pady=(0, 8))
        
        project_desc_entry = tk.Entry(
            main_frame,
            font=("SF Pro Display", 12),
            fg=self.theme["content"]["input_fg"],
            bg=self.theme["content"]["input_bg"],
            relief=tk.FLAT,
            borderwidth=2,
            highlightthickness=1,
            highlightcolor=self.theme["colors"]["primary"]
        )
        project_desc_entry.pack(fill=tk.X, pady=(0, 20))
        project_desc_entry.insert(0, "Brief description of your project")
        
        tk.Label(
            main_frame,
            text="Select project type:",
            font=("SF Pro Display", 13, "bold"),
            fg=self.theme["content"]["fg"],
            bg=self.theme["content"]["bg"]
        ).pack(anchor=tk.W, pady=(0, 15))
        
        # Project type selection
        selected_type = tk.StringVar(value="Laravel")
        
        radio_frame = tk.Frame(main_frame, bg=self.theme["content"]["bg"])
        radio_frame.pack(fill=tk.X, pady=(0, 25))
        
        for project_type in ["Angular", "Laravel", "Custom"]:
            rb = tk.Radiobutton(
                radio_frame,
                text=f"{project_type} Project",
                variable=selected_type,
                value=project_type,
                font=("SF Pro Display", 12),
                fg=self.theme["content"]["fg"],
                bg=self.theme["content"]["bg"],
                selectcolor=self.theme["colors"]["primary"],
                activebackground=self.theme["content"]["bg"],
                activeforeground=self.theme["content"]["fg"],
                anchor=tk.W,
                cursor="hand2"
            )
            rb.pack(fill=tk.X, pady=8, padx=10)
        
        # Create buttons in the fixed bottom frame
        # Cancel button
        cancel_btn = tk.Button(
            bottom_frame,
            text="Cancel",
            command=dialog.destroy,
            font=("SF Pro Display", 11),
            bg=self.theme["buttons"]["secondary_bg"],
            fg=self.theme["buttons"]["secondary_fg"],
            relief=tk.FLAT,
            padx=25,
            pady=10,
            cursor="hand2"
        )
        cancel_btn.pack(side=tk.RIGHT, padx=(15, 0))
        
        # Create button
        create_btn = tk.Button(
            bottom_frame,
            text="Create Project",
            command=lambda: self._create_project_from_dialog(
                dialog, 
                selected_type.get(), 
                project_name_entry.get().strip(),
                project_desc_entry.get().strip()
            ),
            font=("SF Pro Display", 11, "bold"),
            bg=self.theme["buttons"]["success_bg"],
            fg=self.theme["buttons"]["success_fg"],
            relief=tk.FLAT,
            padx=25,
            pady=10,
            cursor="hand2"
        )
        create_btn.pack(side=tk.RIGHT)
        
        # Bind Enter key to create button
        dialog.bind('<Return>', lambda e: create_btn.invoke())
        dialog.bind('<Escape>', lambda e: dialog.destroy())
        
        # Focus on project name entry
        project_name_entry.focus_set()
        
    def _create_project_from_dialog(self, dialog, project_type, project_name, project_desc):
        """Create project from dialog and close it."""
        dialog.destroy()
        self._create_new_project(project_type, project_name, project_desc)
        
    def _create_new_project(self, project_type, custom_name="", description=""):
        """Create a new project instance."""
        # Increment counter for this project type
        self.instance_counters[project_type] += 1
        instance_number = self.instance_counters[project_type]
        
        # Generate project ID and name
        project_id = self.next_project_id
        self.next_project_id += 1
        
        # Use custom name if provided, otherwise use default naming
        if custom_name:
            project_name = custom_name
        else:
            base_name = PROJECT_CONFIG["default_names"].get(project_type, "Project")
            if instance_number > 1:
                project_name = f"{base_name} {instance_number}"
            else:
                project_name = base_name
        
        # Create process handler and output queue for this instance
        process_handler = ProcessHandler()
        output_queue = queue.Queue()
        
        # Store instance data
        self.instances[project_id] = {
            'project_name': project_name,
            'project_type': project_type,
            'instance_number': instance_number,
            'description': description,
            'process_handler': process_handler,
            'output_queue': output_queue,
            'status': 'created',
            'instance_tab': None,  # Will be created when selected
            'working_directory': os.getcwd(),
            'custom_command': None
        }
        
        # Save to database
        self._save_project_to_db(project_id)
        
        # Add to sidebar
        self.sidebar.add_project(project_id, project_name, project_type)
        
        # Auto-select the new project
        self._on_project_select(project_id)
        
    def _on_project_select(self, project_id):
        """Handle project selection from sidebar."""
        if project_id not in self.instances:
            return
            
        self.current_project_id = project_id
        instance = self.instances[project_id]
        
        # Clear content and create project interface
        self._clear_content()
        
        # Create project instance tab if not exists
        if instance['instance_tab'] is None:
            instance_tab = ProjectInstanceTab(
                self.content_frame, 
                instance['project_type'], 
                instance['instance_number']
            )
            instance['instance_tab'] = instance_tab
            
            # Restore saved working directory and command
            if 'working_directory' in instance and instance['working_directory']:
                instance_tab.directory_selector.selected_directory.set(instance['working_directory'])
            
            if 'custom_command' in instance and instance['custom_command']:
                instance_tab.command_entry.entry.delete(0, tk.END)
                instance_tab.command_entry.entry.insert(0, instance['custom_command'])
            
            # Set up callbacks for this instance
            instance_tab.set_callbacks(
                lambda: self._run_command(project_id),
                lambda: self._stop_command(project_id)
            )
            
            # Show initial message
            instance_tab.output_widget.write_message(MESSAGES["instance_created"] + "\n\n", ("info_tag",))
            instance_tab.output_widget.write_message(MESSAGES["initial_output"], "init_msg_visible_test")
        else:
            # Re-pack existing instance
            instance['instance_tab'].main_frame.pack(fill=tk.BOTH, expand=True)
            
    def _clear_content(self):
        """Clear the content area."""
        for widget in self.content_frame.winfo_children():
            widget.pack_forget()
            
    def _run_command(self, project_id):
        """Run command for specific project."""
        if project_id not in self.instances:
            return
            
        instance = self.instances[project_id]
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
        
        # Update status to starting
        self._update_project_status(project_id, "starting")
        
        # Clear previous output
        instance_tab.output_widget.write_message("", ("clear_previous",))
        instance_tab.output_widget.write_message(MESSAGES["initial_output"], "init_msg_visible_test")
        
        # Check if we need to clear a port first
        project_config = PROJECT_TYPES.get(project_type)
        port_to_clear = project_config.get("port") if project_config else None
        
        if port_to_clear:
            self._run_with_port_clearing(project_id, command, cwd, port_to_clear, project_type)
        else:
            self._start_command_thread(project_id, command, cwd)
            
        # Update UI state
        instance_tab.control_buttons.set_run_enabled(False)
        instance_tab.control_buttons.set_stop_enabled(True)
        process_handler.stop_event.clear()
        
    def _run_with_port_clearing(self, project_id, command, cwd, port, project_type):
        """Run command after clearing the specified port."""
        instance = self.instances[project_id]
        output_queue = instance['output_queue']
        
        output_queue.put((f"--- Checking port {port} for {project_type} ---\n", ("info_tag",)))
        self._process_queue(project_id)
        
        def port_clear_and_start():
            port_cleared = find_and_kill_process_on_port(port, output_queue)
            if not port_cleared:
                output_queue.put((f"WARNING: Port {port} clear FAILED. Command may not start correctly.\n", ("error_tag",)))
            else:
                output_queue.put((f"INFO: Port {port} check/clear complete.\n", ("info_tag",)))
            
            if command:
                self._start_command_thread(project_id, command, cwd)
            else:
                self._command_ended_cleanup(project_id)
                output_queue.put(("No command to run after port clear.", ("info_tag",)))
        
        threading.Thread(target=port_clear_and_start, daemon=True).start()
        
    def _start_command_thread(self, project_id, command, cwd):
        """Start the command execution thread for specific project."""
        instance = self.instances[project_id]
        process_handler = instance['process_handler']
        output_queue = instance['output_queue']
        
        process_handler.thread = threading.Thread(
            target=stream_output_worker,
            args=(command, cwd, output_queue, process_handler.stop_event, process_handler),
            daemon=True
        )
        process_handler.thread.start()
        
        # Update status to running
        self._update_project_status(project_id, "running")
        
        self.root.after(PROCESS_CONFIG["queue_check_interval"], lambda: self._process_queue(project_id))
        
    def _stop_command(self, project_id):
        """Stop the currently running command for specific project."""
        if project_id not in self.instances:
            return
            
        instance = self.instances[project_id]
        process_handler = instance['process_handler']
        output_queue = instance['output_queue']
        
        # Update status to stopping
        self._update_project_status(project_id, "stopping")
        
        stop_process(process_handler, output_queue)
        
    def _process_queue(self, project_id):
        """Process messages from the output queue for specific project."""
        if project_id not in self.instances:
            return
            
        instance = self.instances[project_id]
        instance_tab = instance['instance_tab']
        process_handler = instance['process_handler']
        output_queue = instance['output_queue']
        
        if not instance_tab:
            return
        
        try:
            while True:
                if not self.root.winfo_exists() or not instance_tab.output_widget.winfo_exists():
                    return
                    
                message_item = output_queue.get_nowait()
                message, tags = message_item if isinstance(message_item, tuple) else (message_item, None)
                
                if message == "WORKER_THREAD_DONE":
                    self._command_ended_cleanup(project_id)
                    break
                else:
                    instance_tab.output_widget.write_message(message, tags)
                    
        except queue.Empty:
            pass
        except tk.TclError:
            self._command_ended_cleanup(project_id)
            return
        
        # Continue processing if thread is still alive
        if (process_handler.thread and process_handler.thread.is_alive() and
            self.root.winfo_exists()):
            self.root.after(PROCESS_CONFIG["queue_check_interval"], lambda: self._process_queue(project_id))
        elif (not output_queue.empty() and self.root.winfo_exists()):
            self.root.after(PROCESS_CONFIG["queue_check_interval"], lambda: self._process_queue(project_id))
        elif (instance_tab.control_buttons.winfo_exists() and 
              instance_tab.control_buttons.run_button['state'] == tk.DISABLED):
            self._command_ended_cleanup(project_id)
            
    def _command_ended_cleanup(self, project_id):
        """Clean up after command execution ends for specific project."""
        if project_id not in self.instances:
            return
            
        instance = self.instances[project_id]
        instance_tab = instance['instance_tab']
        process_handler = instance['process_handler']
        
        if instance_tab and instance_tab.control_buttons.winfo_exists():
            instance_tab.control_buttons.set_run_enabled(True)
            instance_tab.control_buttons.set_stop_enabled(False)
            
        process_handler.reset()
        
        # Update status to stopped
        self._update_project_status(project_id, "stopped")
        
        if instance_tab and instance_tab.output_widget.winfo_exists():
            instance_tab.output_widget.write_message(MESSAGES["process_ended"], ("info_tag",))
            
    def _update_project_status(self, project_id, status):
        """Update project status in sidebar and instance data."""
        if project_id in self.instances:
            self.instances[project_id]['status'] = status
            self.sidebar.update_project_status(project_id, status)
            # Save status to database
            self.db.update_project_status(project_id, status)
            
    def _on_project_delete(self, project_id):
        """Handle project deletion with confirmation."""
        if project_id not in self.instances:
            return
            
        instance = self.instances[project_id]
        project_name = instance['project_name']
        
        # Show confirmation dialog
        from tkinter import messagebox
        result = messagebox.askyesno(
            "Delete Project",
            f"Are you sure you want to delete '{project_name}'?\n\nThis will stop the project if running and remove it from the list.",
            icon="warning"
        )
        
        if result:
            # Stop the process if running
            process_handler = instance['process_handler']
            if process_handler.is_running():
                output_queue = instance['output_queue']
                stop_process(process_handler, output_queue)
                
                # Wait briefly for process to stop
                if process_handler.thread and process_handler.thread.is_alive():
                    process_handler.thread.join(timeout=1.0)
            
            # Remove from database
            self.db.delete_project(project_id)
            
            # Remove from sidebar
            self.sidebar.remove_project(project_id)
            
            # Remove from instances
            del self.instances[project_id]
            
            # If this was the current project, show welcome screen
            if self.current_project_id == project_id:
                self.current_project_id = None
                if not self.instances:
                    self._show_welcome_screen()
            
    def _setup_window_events(self):
        """Setup window event handlers."""
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
    def _on_closing(self):
        """Handle window closing event."""
        # Save current state
        self._save_app_state()
        
        # Stop all running processes
        for project_id, instance in self.instances.items():
            process_handler = instance['process_handler']
            if process_handler.is_running():
                output_queue = instance['output_queue']
                stop_process(process_handler, output_queue)
                
                # Give a brief moment for graceful shutdown
                if process_handler.thread and process_handler.thread.is_alive():
                    process_handler.thread.join(timeout=PROCESS_CONFIG["graceful_shutdown_timeout"])
                    
        if self.root.winfo_exists():
            self.root.destroy()
            
    def _save_project_to_db(self, project_id):
        """Save a project to the database."""
        if project_id not in self.instances:
            return
            
        instance = self.instances[project_id]
        
        # Get working directory and custom command if available
        working_dir = instance.get('working_directory', os.getcwd())
        custom_command = instance.get('custom_command')
        
        # If instance tab exists, get current values
        if instance['instance_tab']:
            try:
                working_dir = instance['instance_tab'].directory_selector.get()
                custom_command = instance['instance_tab'].command_entry.get()
            except:
                pass  # Use defaults if widgets don't exist
        
        self.db.save_project(
            project_id=project_id,
            name=instance['project_name'],
            description=instance['description'],
            project_type=instance['project_type'],
            instance_number=instance['instance_number'],
            working_directory=working_dir,
            custom_command=custom_command,
            status=instance['status']
        )
    
    def _load_saved_projects(self):
        """Load saved projects from database."""
        try:
            # Load project counters
            saved_counters = self.db.load_project_counters()
            if saved_counters:
                self.instance_counters.update(saved_counters)
            
            # Load projects
            saved_projects = self.db.load_projects()
            
            if not saved_projects:
                return  # No saved projects
            
            # Find the highest project ID to set next_project_id
            max_id = max((p['project_id'] for p in saved_projects), default=0)
            self.next_project_id = max_id + 1
            
            # Restore projects
            for project_data in saved_projects:
                project_id = project_data['project_id']
                
                # Create process handler and output queue
                process_handler = ProcessHandler()
                output_queue = queue.Queue()
                
                # Restore instance data
                self.instances[project_id] = {
                    'project_name': project_data['name'],
                    'project_type': project_data['project_type'],
                    'instance_number': project_data['instance_number'],
                    'description': project_data['description'] or '',
                    'process_handler': process_handler,
                    'output_queue': output_queue,
                    'status': 'created',  # Reset status on startup
                    'instance_tab': None,
                    'working_directory': project_data['working_directory'] or os.getcwd(),
                    'custom_command': project_data['custom_command']
                }
                
                # Add to sidebar
                self.sidebar.add_project(
                    project_id, 
                    project_data['name'], 
                    project_data['project_type']
                )
            
            # Load last selected project
            last_selected = self.db.load_app_setting("last_selected_project")
            if last_selected and int(last_selected) in self.instances:
                self._on_project_select(int(last_selected))
            elif self.instances:
                # Select first project if no last selected
                first_id = next(iter(self.instances))
                self._on_project_select(first_id)
                
        except Exception as e:
            print(f"Error loading saved projects: {e}")
            # Continue with empty state if loading fails
    
    def _save_app_state(self):
        """Save current application state."""
        try:
            # Save project counters
            self.db.save_project_counters(self.instance_counters)
            
            # Save all projects
            for project_id in self.instances:
                self._save_project_to_db(project_id)
            
            # Save last selected project
            if self.current_project_id:
                self.db.save_app_setting("last_selected_project", str(self.current_project_id))
                
            # Save window geometry
            geometry = self.root.geometry()
            self.db.save_app_setting("window_geometry", geometry)
            
        except Exception as e:
            print(f"Error saving application state: {e}")
    
    def _restore_window_geometry(self):
        """Restore saved window geometry."""
        try:
            saved_geometry = self.db.load_app_setting("window_geometry")
            if saved_geometry:
                self.root.geometry(saved_geometry)
        except Exception as e:
            print(f"Error restoring window geometry: {e}")

    def run(self):
        """Start the main application loop."""
        # Restore window geometry
        self._restore_window_geometry()
        
        if self.root.winfo_exists():
            self.root.mainloop() 