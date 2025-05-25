"""
Custom widgets and UI components for Project Runner App.
"""

import tkinter as tk
from tkinter import scrolledtext, ttk
from config.settings import UI_CONFIG, OUTPUT_TAGS, MESSAGES, PROJECT_CONFIG, STATUS_CONFIG


class OutputTextWidget:
    """Custom output text widget with proper styling and tag configuration."""
    
    def __init__(self, parent):
        self.colors = UI_CONFIG["colors"]
        self.dimensions = UI_CONFIG["dimensions"]
        
        # Create the scrolled text widget
        self.widget = scrolledtext.ScrolledText(
            parent, 
            height=self.dimensions["output_height"], 
            width=self.dimensions["output_width"], 
            wrap=tk.WORD, 
            relief=tk.SUNKEN,
            fg=self.colors["output_text_fg"], 
            bg=self.colors["output_text_bg"], 
            insertbackground=self.colors["output_cursor_bg"]
        )
        
        self._configure_tags()
        self._initialize_content()
        
    def _configure_tags(self):
        """Configure text tags for different types of output."""
        for tag_name, tag_config in OUTPUT_TAGS.items():
            self.widget.tag_config(tag_name, **tag_config)
            
    def _initialize_content(self):
        """Set initial content in the output widget."""
        from config.settings import MESSAGES
        self.widget.configure(state='normal')
        self.widget.insert(tk.END, MESSAGES["initial_output"], "init_msg_visible_test")
        self.widget.configure(state='disabled')
        
    def write_message(self, message, tags=None):
        """Write a message to the output widget."""
        if not self.widget.winfo_exists():
            return
            
        self.widget.configure(state='normal')
        
        if tags == ("clear_previous",):
            self.widget.delete(1.0, tk.END)
        else:
            effective_tags = tags if tags else ("stdout_tag",)
            self.widget.insert(tk.END, message, effective_tags)
            
        self.widget.configure(state='disabled')
        self.widget.see(tk.END)
        
    def pack(self, **kwargs):
        """Pack the widget."""
        self.widget.pack(**kwargs)
        
    def winfo_exists(self):
        """Check if widget exists."""
        return self.widget.winfo_exists()


class ProjectTypeSelector:
    """Widget for selecting project type with radio buttons."""
    
    def __init__(self, parent, on_change_callback=None):
        self.parent = parent
        self.on_change_callback = on_change_callback
        self.colors = UI_CONFIG["colors"]
        
        # Create the variable and trace changes
        self.project_type = tk.StringVar(value="Custom")
        if on_change_callback:
            self.project_type.trace_add("write", self._on_change)
            
        self._create_widgets()
        
    def _create_widgets(self):
        """Create the radio button widgets."""
        tk.Label(
            self.parent, 
            text="Project Type:", 
            fg=self.colors["label_fg"], 
            bg=self.colors["label_bg"], 
            padx=5
        ).pack(side=tk.LEFT)
        
        # Create radio buttons for each project type
        for project_type in ["Custom", "Laravel", "Angular"]:
            tk.Radiobutton(
                self.parent, 
                text=project_type, 
                variable=self.project_type, 
                value=project_type, 
                indicatoron=0, 
                padx=10, 
                fg=self.colors["label_fg"], 
                selectcolor=self.colors["button_select_color"], 
                bg=self.colors["button_bg"]
            ).pack(side=tk.RIGHT, padx=2)
            
    def _on_change(self, *args):
        """Handle project type change."""
        if self.on_change_callback:
            self.on_change_callback(self.project_type.get())
            
    def get(self):
        """Get the current project type."""
        return self.project_type.get()


class DirectorySelector:
    """Widget for selecting working directory."""
    
    def __init__(self, parent, initial_dir=None):
        self.parent = parent
        self.colors = UI_CONFIG["colors"]
        
        # Initialize directory variable
        import os
        self.selected_directory = tk.StringVar(value=initial_dir or os.getcwd())
        
        self._create_widgets()
        
    def _create_widgets(self):
        """Create the directory selection widgets."""
        tk.Label(
            self.parent, 
            text="Working Directory:", 
            fg=self.colors["label_fg"], 
            bg=self.colors["label_bg"], 
            padx=5
        ).pack(side=tk.LEFT)
        
        self.dir_label = tk.Label(
            self.parent, 
            textvariable=self.selected_directory, 
            relief=tk.SUNKEN, 
            fg=self.colors["entry_fg"], 
            bg=self.colors["entry_bg"], 
            padx=10, 
            anchor=tk.W
        )
        self.dir_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.browse_button = tk.Button(
            self.parent, 
            text="Browse", 
            command=self._browse_directory
        )
        self.browse_button.pack(side=tk.RIGHT, padx=5)
        
    def _browse_directory(self):
        """Open directory browser dialog."""
        from tkinter import filedialog
        new_dir = filedialog.askdirectory(initialdir=self.selected_directory.get())
        if new_dir:
            self.selected_directory.set(new_dir)
            
    def get(self):
        """Get the current directory."""
        return self.selected_directory.get()


class CommandEntry:
    """Widget for command input with project-specific behavior."""
    
    def __init__(self, parent):
        self.parent = parent
        self.colors = UI_CONFIG["colors"]
        self.dimensions = UI_CONFIG["dimensions"]
        
        self._create_widgets()
        
    def _create_widgets(self):
        """Create the command entry widgets."""
        tk.Label(
            self.parent, 
            text="Command:", 
            fg=self.colors["label_fg"], 
            bg=self.colors["label_bg"], 
            padx=5
        ).pack(side=tk.LEFT)
        
        self.entry = tk.Entry(
            self.parent, 
            width=self.dimensions["command_entry_width"], 
            fg=self.colors["entry_fg"], 
            bg=self.colors["entry_bg"], 
            relief=tk.SUNKEN
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
    def update_for_project_type(self, project_type):
        """Update the command entry based on project type."""
        from config.settings import PROJECT_TYPES
        
        project_config = PROJECT_TYPES.get(project_type, PROJECT_TYPES["Custom"])
        
        self.entry.configure(state='normal', fg=self.colors["entry_fg"], bg=self.colors["entry_bg"])
        self.entry.delete(0, tk.END)
        
        if project_config["readonly"]:
            self.entry.insert(0, project_config["command"])
            self.entry.configure(
                state='readonly', 
                fg=self.colors["entry_fg"], 
                readonlybackground=self.colors["readonly_bg"], 
                bg=self.colors["readonly_bg"]
            )
        else:
            self.entry.configure(state='normal', fg=self.colors["entry_fg"], bg=self.colors["entry_bg"])
            
    def get(self):
        """Get the current command."""
        return self.entry.get()
        
    def winfo_exists(self):
        """Check if widget exists."""
        return self.entry.winfo_exists()


class ControlButtons:
    """Widget for run/stop control buttons."""
    
    def __init__(self, parent, run_callback=None, stop_callback=None):
        self.parent = parent
        self.run_callback = run_callback
        self.stop_callback = stop_callback
        
        self._create_widgets()
        
    def _create_widgets(self):
        """Create the control buttons."""
        self.run_button = tk.Button(
            self.parent, 
            text="Run Command", 
            command=self._on_run
        )
        self.run_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = tk.Button(
            self.parent, 
            text="Stop Command", 
            command=self._on_stop, 
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
    def _on_run(self):
        """Handle run button click."""
        if self.run_callback:
            self.run_callback()
            
    def _on_stop(self):
        """Handle stop button click."""
        if self.stop_callback:
            self.stop_callback()
            
    def set_run_enabled(self, enabled):
        """Enable/disable the run button."""
        state = tk.NORMAL if enabled else tk.DISABLED
        if self.run_button.winfo_exists():
            self.run_button.config(state=state)
            
    def set_stop_enabled(self, enabled):
        """Enable/disable the stop button."""
        state = tk.NORMAL if enabled else tk.DISABLED
        if self.stop_button.winfo_exists():
            self.stop_button.config(state=state)
            
    def winfo_exists(self):
        """Check if widgets exist."""
        return self.run_button.winfo_exists() and self.stop_button.winfo_exists()


class CreateInstanceTab:
    """Widget for creating new project instances."""
    
    def __init__(self, parent, create_callback=None):
        self.parent = parent
        self.create_callback = create_callback
        self.colors = UI_CONFIG["colors"]
        
        self._create_widgets()
        
    def _create_widgets(self):
        """Create the create instance interface."""
        # Main container
        main_frame = tk.Frame(self.parent, bg=self.colors["label_bg"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Welcome message
        welcome_frame = tk.Frame(main_frame, bg=self.colors["label_bg"])
        welcome_frame.pack(fill=tk.X, pady=(0, 30))
        
        welcome_label = tk.Label(
            welcome_frame,
            text=MESSAGES["welcome_message"],
            font=("Helvetica", 12),
            fg=self.colors["label_fg"],
            bg=self.colors["label_bg"],
            justify=tk.LEFT,
            wraplength=500
        )
        welcome_label.pack()
        
        # Project type selection
        selection_frame = tk.Frame(main_frame, bg=self.colors["label_bg"])
        selection_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            selection_frame,
            text="Select Project Type:",
            font=("Helvetica", 14, "bold"),
            fg=self.colors["label_fg"],
            bg=self.colors["label_bg"]
        ).pack(pady=(0, 15))
        
        # Project type buttons
        self.selected_type = tk.StringVar(value="Laravel")
        
        button_frame = tk.Frame(selection_frame, bg=self.colors["label_bg"])
        button_frame.pack()
        
        for project_type in ["Angular", "Laravel", "Custom"]:
            btn = tk.Radiobutton(
                button_frame,
                text=f"{project_type} Project",
                variable=self.selected_type,
                value=project_type,
                font=("Helvetica", 11),
                fg=self.colors["label_fg"],
                bg=self.colors["button_bg"],
                selectcolor=self.colors["button_select_color"],
                indicatoron=0,
                padx=20,
                pady=10,
                relief=tk.RAISED,
                borderwidth=2
            )
            btn.pack(side=tk.LEFT, padx=10)
        
        # Create button
        create_button = tk.Button(
            main_frame,
            text="Create Instance",
            command=self._on_create,
            font=("Helvetica", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            padx=30,
            pady=10,
            relief=tk.RAISED,
            borderwidth=2
        )
        create_button.pack(pady=30)
        
    def _on_create(self):
        """Handle create instance button click."""
        if self.create_callback:
            self.create_callback(self.selected_type.get())


class ProjectInstanceTab:
    """Complete project instance tab with all controls."""
    
    def __init__(self, parent, project_type, instance_number=1):
        self.parent = parent
        self.project_type = project_type
        self.instance_number = instance_number
        self.colors = UI_CONFIG["colors"]
        
        # Create main container
        self.main_frame = tk.Frame(parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self._create_widgets()
        
    def _create_widgets(self):
        """Create all widgets for the project instance."""
        # Create frames
        self._create_frames()
        
        # Project type selector (read-only, shows current type)
        type_label = tk.Label(
            self.project_type_frame,
            text=f"Project Type: {self.project_type}",
            font=("Helvetica", 12, "bold"),
            fg=self.colors["label_fg"],
            bg=self.colors["label_bg"]
        )
        type_label.pack(side=tk.LEFT, padx=10)
        
        # Directory selector
        self.directory_selector = DirectorySelector(self.dir_frame)
        
        # Command entry
        self.command_entry = CommandEntry(self.command_frame)
        self.command_entry.update_for_project_type(self.project_type)
        
        # Output display
        tk.Label(
            self.output_frame,
            text="Output:",
            fg=self.colors["label_fg"],
            bg=self.colors["label_bg"],
            padx=5
        ).pack(anchor=tk.NW)
        
        self.output_widget = OutputTextWidget(self.output_frame)
        self.output_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0,5))
        
        # Control buttons
        self.control_buttons = ControlButtons(
            self.button_frame,
            run_callback=None,  # Will be set by parent
            stop_callback=None  # Will be set by parent
        )
        
    def _create_frames(self):
        """Create the layout frames."""
        self.project_type_frame = tk.Frame(self.main_frame, pady=2)
        self.project_type_frame.pack(pady=5, padx=10, fill=tk.X)

        self.dir_frame = tk.Frame(self.main_frame, pady=2)
        self.dir_frame.pack(pady=5, padx=10, fill=tk.X)

        self.command_frame = tk.Frame(self.main_frame, pady=2)
        self.command_frame.pack(pady=5, padx=10, fill=tk.X)

        self.output_frame = tk.Frame(self.main_frame, pady=2)
        self.output_frame.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)

        self.button_frame = tk.Frame(self.main_frame)
        self.button_frame.pack(pady=10, padx=10, fill=tk.X, side=tk.BOTTOM)
        
    def get_project_name(self):
        """Generate project name for this instance."""
        base_name = PROJECT_CONFIG["default_names"].get(self.project_type, "Project")
        if self.instance_number > 1:
            title = f"{base_name} {self.instance_number}"
        else:
            title = base_name
            
        # Truncate if too long
        max_length = PROJECT_CONFIG["max_name_length"]
        if len(title) > max_length:
            title = title[:max_length-3] + "..."
            
        return title
        
    def set_callbacks(self, run_callback, stop_callback):
        """Set the run and stop callbacks for this instance."""
        self.control_buttons.run_callback = run_callback
        self.control_buttons.stop_callback = stop_callback


class ProjectListItem:
    """Individual project item in the sidebar."""
    
    def __init__(self, parent, project_id, project_name, project_type, click_callback=None, delete_callback=None):
        self.parent = parent
        self.project_id = project_id
        self.project_name = project_name
        self.project_type = project_type
        self.click_callback = click_callback
        self.delete_callback = delete_callback
        self.status = "created"
        self.selected = False
        
        self.colors = UI_CONFIG["colors"]
        self.sidebar_colors = UI_CONFIG["sidebar"]
        
        self._create_widget()
        
    def _create_widget(self):
        """Create the project list item widget."""
        self.frame = tk.Frame(
            self.parent,
            bg=self.sidebar_colors["bg"],
            relief=tk.FLAT,
            borderwidth=1,
            height=UI_CONFIG["dimensions"]["sidebar_item_height"]
        )
        self.frame.pack(fill=tk.X, padx=5, pady=2)
        self.frame.pack_propagate(False)  # Maintain fixed height
        
        # Bind click events
        self.frame.bind("<Button-1>", self._on_click)
        self.frame.bind("<Enter>", self._on_enter)
        self.frame.bind("<Leave>", self._on_leave)
        
        # Status indicator
        self.status_label = tk.Label(
            self.frame,
            text=STATUS_CONFIG["indicators"]["created"],
            font=("Helvetica", 16),
            fg=STATUS_CONFIG["colors"]["created"],
            bg=self.sidebar_colors["bg"],
            width=2
        )
        self.status_label.pack(side=tk.LEFT, padx=(10, 5), pady=10)
        self.status_label.bind("<Button-1>", self._on_click)
        
        # Project info frame
        info_frame = tk.Frame(self.frame, bg=self.sidebar_colors["bg"])
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 10), pady=5)
        info_frame.bind("<Button-1>", self._on_click)
        
        # Project name
        self.name_label = tk.Label(
            info_frame,
            text=self.project_name,
            font=("Helvetica", 11, "bold"),
            fg=self.colors["label_fg"],
            bg=self.sidebar_colors["bg"],
            anchor=tk.W
        )
        self.name_label.pack(fill=tk.X)
        self.name_label.bind("<Button-1>", self._on_click)
        
        # Project type and status
        self.status_text_label = tk.Label(
            info_frame,
            text=f"{self.project_type} • {STATUS_CONFIG['text']['created']}",
            font=("Helvetica", 9),
            fg="#666666",
            bg=self.sidebar_colors["bg"],
            anchor=tk.W
        )
        self.status_text_label.pack(fill=tk.X)
        self.status_text_label.bind("<Button-1>", self._on_click)
        
        # Delete button
        self.delete_button = tk.Button(
            self.frame,
            text="×",
            font=("Helvetica", 12, "bold"),
            fg="#dc3545",
            bg=self.sidebar_colors["bg"],
            relief=tk.FLAT,
            width=2,
            command=self._on_delete
        )
        self.delete_button.pack(side=tk.RIGHT, padx=(5, 10), pady=10)
        
    def _on_click(self, event):
        """Handle click on project item."""
        if self.click_callback:
            self.click_callback(self.project_id)
            
    def _on_delete(self):
        """Handle delete button click."""
        if self.delete_callback:
            self.delete_callback(self.project_id)
            
    def _on_enter(self, event):
        """Handle mouse enter."""
        if not self.selected:
            self._update_background(self.sidebar_colors["hover_bg"])
            
    def _on_leave(self, event):
        """Handle mouse leave."""
        if not self.selected:
            self._update_background(self.sidebar_colors["bg"])
            
    def _update_background(self, color):
        """Update background color of all components."""
        self.frame.config(bg=color)
        self.status_label.config(bg=color)
        self.delete_button.config(bg=color)
        for child in self.frame.winfo_children():
            if isinstance(child, tk.Frame):
                child.config(bg=color)
                for grandchild in child.winfo_children():
                    if isinstance(grandchild, tk.Label):
                        grandchild.config(bg=color)
                        
    def set_selected(self, selected):
        """Set the selection state."""
        self.selected = selected
        if selected:
            self._update_background(self.sidebar_colors["selected_bg"])
        else:
            self._update_background(self.sidebar_colors["bg"])
            
    def update_status(self, status):
        """Update the project status."""
        self.status = status
        
        # Update status indicator
        self.status_label.config(
            text=STATUS_CONFIG["indicators"][status],
            fg=STATUS_CONFIG["colors"][status]
        )
        
        # Update status text
        self.status_text_label.config(
            text=f"{self.project_type} • {STATUS_CONFIG['text'][status]}"
        )


class ProjectSidebar:
    """Sidebar containing project list and controls."""
    
    def __init__(self, parent, create_callback=None, select_callback=None, delete_callback=None):
        self.parent = parent
        self.create_callback = create_callback
        self.select_callback = select_callback
        self.delete_callback = delete_callback
        self.project_items = {}
        self.selected_project_id = None
        
        self.colors = UI_CONFIG["colors"]
        self.sidebar_colors = UI_CONFIG["sidebar"]
        
        self._create_widgets()
        
    def _create_widgets(self):
        """Create the sidebar widgets."""
        # Main sidebar frame
        self.sidebar_frame = tk.Frame(
            self.parent,
            bg=self.sidebar_colors["bg"],
            width=UI_CONFIG["dimensions"]["sidebar_width"],
            relief=tk.RAISED,
            borderwidth=1
        )
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar_frame.pack_propagate(False)  # Maintain fixed width
        
        # Header
        header_frame = tk.Frame(self.sidebar_frame, bg=self.sidebar_colors["bg"])
        header_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        tk.Label(
            header_frame,
            text="Projects",
            font=("Helvetica", 14, "bold"),
            fg=self.colors["label_fg"],
            bg=self.sidebar_colors["bg"]
        ).pack(anchor=tk.W)
        
        # Create new project button
        self.create_button = tk.Button(
            self.sidebar_frame,
            text="+ Create New Project",
            command=self._on_create_new,
            font=("Helvetica", 10, "bold"),
            bg="#28a745",
            fg="white",
            relief=tk.FLAT,
            padx=20,
            pady=8
        )
        self.create_button.pack(fill=tk.X, padx=10, pady=(5, 15))
        
        # Scrollable project list
        self.list_frame = tk.Frame(self.sidebar_frame, bg=self.sidebar_colors["bg"])
        self.list_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Status legend
        legend_frame = tk.Frame(self.sidebar_frame, bg=self.sidebar_colors["bg"])
        legend_frame.pack(fill=tk.X, padx=10, pady=10, side=tk.BOTTOM)
        
        tk.Label(
            legend_frame,
            text="Status:",
            font=("Helvetica", 8, "bold"),
            fg="#666666",
            bg=self.sidebar_colors["bg"]
        ).pack(anchor=tk.W)
        
        for status, color in [("running", "🟢 Running"), ("stopped", "🔴 Stopped"), 
                             ("starting", "🟡 Starting"), ("created", "⚪ Ready")]:
            tk.Label(
                legend_frame,
                text=color,
                font=("Helvetica", 8),
                fg="#666666",
                bg=self.sidebar_colors["bg"]
            ).pack(anchor=tk.W)
            
    def _on_create_new(self):
        """Handle create new project button click."""
        if self.create_callback:
            self.create_callback()
            
    def add_project(self, project_id, project_name, project_type):
        """Add a new project to the sidebar."""
        item = ProjectListItem(
            self.list_frame,
            project_id,
            project_name,
            project_type,
            self._on_project_select,
            self._on_project_delete
        )
        self.project_items[project_id] = item
        
        # Auto-select if it's the first project
        if len(self.project_items) == 1:
            self.select_project(project_id)
            
    def _on_project_select(self, project_id):
        """Handle project selection."""
        self.select_project(project_id)
        if self.select_callback:
            self.select_callback(project_id)
            
    def _on_project_delete(self, project_id):
        """Handle project deletion."""
        if self.delete_callback:
            self.delete_callback(project_id)
            
    def select_project(self, project_id):
        """Select a project in the sidebar."""
        # Deselect current
        if self.selected_project_id and self.selected_project_id in self.project_items:
            self.project_items[self.selected_project_id].set_selected(False)
            
        # Select new
        if project_id in self.project_items:
            self.project_items[project_id].set_selected(True)
            self.selected_project_id = project_id
            
    def update_project_status(self, project_id, status):
        """Update the status of a project."""
        if project_id in self.project_items:
            self.project_items[project_id].update_status(status)
            
    def remove_project(self, project_id):
        """Remove a project from the sidebar."""
        if project_id in self.project_items:
            self.project_items[project_id].frame.destroy()
            del self.project_items[project_id]
            
            # Select another project if this was selected
            if self.selected_project_id == project_id:
                self.selected_project_id = None
                if self.project_items:
                    # Select the first available project
                    first_id = next(iter(self.project_items))
                    self.select_project(first_id)
                    if self.select_callback:
                        self.select_callback(first_id) 