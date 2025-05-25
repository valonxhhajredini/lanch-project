"""
Custom widgets and UI components for Project Runner App.
"""

import tkinter as tk
from tkinter import scrolledtext, ttk
from config.settings import UI_CONFIG, OUTPUT_TAGS, MESSAGES, PROJECT_CONFIG, STATUS_CONFIG, get_current_theme


class ThemedWidget:
    """Base class for theme-aware widgets."""
    
    def __init__(self):
        self.theme = get_current_theme()
        
    def refresh_theme(self):
        """Refresh the theme and update widget appearance."""
        self.theme = get_current_theme()
        self.apply_theme()
        
    def apply_theme(self):
        """Apply theme to widget. Override in subclasses."""
        pass


class OutputTextWidget(ThemedWidget):
    """Custom output text widget with proper styling and tag configuration."""
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.dimensions = UI_CONFIG["dimensions"]
        
        # Create the scrolled text widget
        self.widget = scrolledtext.ScrolledText(
            parent, 
            height=self.dimensions["output_height"], 
            width=self.dimensions["output_width"], 
            wrap=tk.WORD, 
            relief=tk.FLAT,
            borderwidth=1,
            font=("Consolas", 10),
            selectbackground=self.theme["colors"]["primary"]
        )
        
        self.apply_theme()
        self._configure_tags()
        self._initialize_content()
        
    def apply_theme(self):
        """Apply current theme to the output widget."""
        self.widget.configure(
            fg=self.theme["content"]["output_fg"],
            bg=self.theme["content"]["output_bg"],
            insertbackground=self.theme["content"]["fg"],
            highlightbackground=self.theme["content"]["input_border"],
            highlightcolor=self.theme["colors"]["primary"]
        )
        
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
            fg="#333333", 
            bg="#ffffff", 
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
                fg="#333333", 
                selectcolor="#007bff", 
                bg="#f8f9fa"
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
        
        # Initialize directory variable
        import os
        self.selected_directory = tk.StringVar(value=initial_dir or os.getcwd())
        
        self._create_widgets()
        
    def _create_widgets(self):
        """Create the directory selection widgets."""
        tk.Label(
            self.parent, 
            text="Working Directory:", 
            fg="#333333", 
            bg="#ffffff", 
            padx=5
        ).pack(side=tk.LEFT)
        
        self.dir_label = tk.Label(
            self.parent, 
            textvariable=self.selected_directory, 
            relief=tk.SUNKEN, 
            fg="#495057", 
            bg="#ffffff", 
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
        self.dimensions = UI_CONFIG["dimensions"]
        
        self._create_widgets()
        
    def _create_widgets(self):
        """Create the command entry widgets."""
        tk.Label(
            self.parent, 
            text="Command:", 
            fg="#333333", 
            bg="#ffffff", 
            padx=5
        ).pack(side=tk.LEFT)
        
        self.entry = tk.Entry(
            self.parent, 
            width=self.dimensions["command_entry_width"], 
            fg="#495057", 
            bg="#ffffff", 
            relief=tk.SUNKEN
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
    def update_for_project_type(self, project_type):
        """Update the command entry based on project type."""
        from config.settings import PROJECT_TYPES
        
        project_config = PROJECT_TYPES.get(project_type, PROJECT_TYPES["Custom"])
        
        self.entry.configure(state='normal', fg="#495057", bg="#ffffff")
        self.entry.delete(0, tk.END)
        
        if project_config["readonly"]:
            self.entry.insert(0, project_config["command"])
            self.entry.configure(
                state='readonly', 
                fg="#495057", 
                readonlybackground="#e9ecef", 
                bg="#e9ecef"
            )
        else:
            self.entry.configure(state='normal', fg="#495057", bg="#ffffff")
            
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
        
        self._create_widgets()
        
    def _create_widgets(self):
        """Create the create instance interface."""
        # Main container
        main_frame = tk.Frame(self.parent, bg="#ffffff")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Welcome message
        welcome_frame = tk.Frame(main_frame, bg="#ffffff")
        welcome_frame.pack(fill=tk.X, pady=(0, 30))
        
        welcome_label = tk.Label(
            welcome_frame,
            text=MESSAGES["welcome_message"],
            font=("Helvetica", 12),
            fg="#333333",
            bg="#ffffff",
            justify=tk.LEFT,
            wraplength=500
        )
        welcome_label.pack()
        
        # Project type selection
        selection_frame = tk.Frame(main_frame, bg="#ffffff")
        selection_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            selection_frame,
            text="Select Project Type:",
            font=("Helvetica", 14, "bold"),
            fg="#333333",
            bg="#ffffff"
        ).pack(pady=(0, 15))
        
        # Project type buttons
        self.selected_type = tk.StringVar(value="Laravel")
        
        button_frame = tk.Frame(selection_frame, bg="#ffffff")
        button_frame.pack()
        
        for project_type in ["Angular", "Laravel", "Custom"]:
            btn = tk.Radiobutton(
                button_frame,
                text=f"{project_type} Project",
                variable=self.selected_type,
                value=project_type,
                font=("Helvetica", 11),
                fg="#333333",
                bg="#f8f9fa",
                selectcolor="#007bff",
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


class ProjectInstanceTab(ThemedWidget):
    """Complete project instance tab with all controls."""
    
    def __init__(self, parent, project_type, instance_number=1):
        super().__init__()
        self.parent = parent
        self.project_type = project_type
        self.instance_number = instance_number
        
        # Create main container
        self.main_frame = tk.Frame(parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self._create_widgets()
        self.apply_theme()
        
    def _create_widgets(self):
        """Create all widgets for the project instance."""
        # Create frames
        self._create_frames()
        
        # Project type selector (read-only, shows current type)
        self.type_label = tk.Label(
            self.project_type_frame,
            text=f"Project Type: {self.project_type}",
            font=("SF Pro Display", 12, "bold")
        )
        self.type_label.pack(side=tk.LEFT, padx=10)
        
        # Directory selector
        self.directory_selector = DirectorySelector(self.dir_frame)
        
        # Command entry
        self.command_entry = CommandEntry(self.command_frame)
        self.command_entry.update_for_project_type(self.project_type)
        
        # Output display
        self.output_label = tk.Label(
            self.output_frame,
            text="Output:",
            font=("SF Pro Display", 12, "bold"),
            padx=5
        )
        self.output_label.pack(anchor=tk.NW)
        
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
        self.project_type_frame = tk.Frame(self.main_frame)
        self.project_type_frame.pack(pady=5, padx=10, fill=tk.X)

        self.dir_frame = tk.Frame(self.main_frame)
        self.dir_frame.pack(pady=5, padx=10, fill=tk.X)

        self.command_frame = tk.Frame(self.main_frame)
        self.command_frame.pack(pady=5, padx=10, fill=tk.X)

        self.output_frame = tk.Frame(self.main_frame)
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
        
    def apply_theme(self):
        """Apply current theme to the project instance tab."""
        # Main frame
        self.main_frame.configure(bg=self.theme["content"]["bg"])
        
        # All sub-frames
        frames = ['project_type_frame', 'dir_frame', 'command_frame', 'output_frame', 'button_frame']
        for frame_name in frames:
            if hasattr(self, frame_name):
                frame = getattr(self, frame_name)
                if frame.winfo_exists():
                    frame.configure(bg=self.theme["content"]["bg"])
        
        # Labels
        if hasattr(self, 'type_label') and self.type_label.winfo_exists():
            self.type_label.configure(
                fg=self.theme["content"]["fg"],
                bg=self.theme["content"]["bg"]
            )
            
        if hasattr(self, 'output_label') and self.output_label.winfo_exists():
            self.output_label.configure(
                fg=self.theme["content"]["fg"],
                bg=self.theme["content"]["bg"]
            )
            
        # Refresh themed widgets
        if hasattr(self, 'output_widget'):
            self.output_widget.refresh_theme()


class ProjectListItem(ThemedWidget):
    """Individual project item in the sidebar."""
    
    def __init__(self, parent, project_id, project_name, project_type, click_callback=None, delete_callback=None):
        super().__init__()
        self.parent = parent
        self.project_id = project_id
        self.project_name = project_name
        self.project_type = project_type
        self.click_callback = click_callback
        self.delete_callback = delete_callback
        self.status = "created"
        self.selected = False
        
        self._create_widget()
        
    def _create_widget(self):
        """Create the project list item widget."""
        self.frame = tk.Frame(
            self.parent,
            relief=tk.FLAT,
            borderwidth=0,
            height=UI_CONFIG["dimensions"]["sidebar_item_height"]
        )
        self.frame.pack(fill=tk.X, padx=10, pady=3)
        self.frame.pack_propagate(False)  # Maintain fixed height
        
        # Bind click events
        self.frame.bind("<Button-1>", self._on_click)
        self.frame.bind("<Enter>", self._on_enter)
        self.frame.bind("<Leave>", self._on_leave)
        
        # Delete button (pack first on the right to ensure it's always visible)
        self.delete_button = tk.Button(
            self.frame,
            text="×",
            font=("SF Pro Display", 14, "bold"),
            relief=tk.FLAT,
            width=2,
            command=self._on_delete,
            cursor="hand2"
        )
        self.delete_button.pack(side=tk.RIGHT, padx=(5, 15), pady=15)
        
        # Status indicator
        self.status_label = tk.Label(
            self.frame,
            text=STATUS_CONFIG["indicators"]["created"],
            font=("SF Pro Display", 18),
            width=2
        )
        self.status_label.pack(side=tk.LEFT, padx=(15, 10), pady=15)
        self.status_label.bind("<Button-1>", self._on_click)
        
        # Project info frame (fills remaining space between status and delete button)
        self.info_frame = tk.Frame(self.frame)
        self.info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 5), pady=10)
        self.info_frame.bind("<Button-1>", self._on_click)
        
        # Project name (truncate if too long)
        display_name = self.project_name
        if len(display_name) > 18:  # Truncate long names
            display_name = display_name[:15] + "..."
            
        self.name_label = tk.Label(
            self.info_frame,
            text=display_name,
            font=("SF Pro Display", 12, "bold"),
            anchor=tk.W
        )
        self.name_label.pack(fill=tk.X)
        self.name_label.bind("<Button-1>", self._on_click)
        
        # Project type and status
        self.status_text_label = tk.Label(
            self.info_frame,
            text=f"{self.project_type} • {STATUS_CONFIG['text']['created']}",
            font=("SF Pro Display", 10),
            anchor=tk.W
        )
        self.status_text_label.pack(fill=tk.X)
        self.status_text_label.bind("<Button-1>", self._on_click)
        
        self.apply_theme()
        
    def apply_theme(self):
        """Apply current theme to the project item."""
        # Main frame
        self.frame.configure(bg=self.theme["sidebar"]["bg"])
        
        # Delete button
        self.delete_button.configure(
            fg=self.theme["colors"]["danger"],
            bg=self.theme["sidebar"]["bg"],
            activebackground=self.theme["sidebar"]["hover_bg"]
        )
        
        # Status indicator
        self.status_label.configure(
            fg=STATUS_CONFIG["colors"][self.status],
            bg=self.theme["sidebar"]["bg"]
        )
        
        # Info frame
        self.info_frame.configure(bg=self.theme["sidebar"]["bg"])
        
        # Name label
        self.name_label.configure(
            fg=self.theme["sidebar"]["fg"],
            bg=self.theme["sidebar"]["bg"]
        )
        
        # Status text label
        self.status_text_label.configure(
            fg=self.theme["sidebar"]["fg"],
            bg=self.theme["sidebar"]["bg"]
        )
        
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
            self._update_background(self.theme["sidebar"]["hover_bg"])
            
    def _on_leave(self, event):
        """Handle mouse leave."""
        if not self.selected:
            self._update_background(self.theme["sidebar"]["bg"])
            
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
            self._update_background(self.theme["sidebar"]["selected_bg"])
        else:
            self._update_background(self.theme["sidebar"]["bg"])
            
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


class ProjectSidebar(ThemedWidget):
    """Sidebar containing project list and controls."""
    
    def __init__(self, parent, create_callback=None, select_callback=None, delete_callback=None, theme_callback=None):
        super().__init__()
        self.parent = parent
        self.create_callback = create_callback
        self.select_callback = select_callback
        self.delete_callback = delete_callback
        self.theme_callback = theme_callback
        self.project_items = {}
        self.selected_project_id = None
        
        self._create_widgets()
        
    def _create_widgets(self):
        """Create the sidebar widgets."""
        # Main sidebar frame
        self.sidebar_frame = tk.Frame(
            self.parent,
            width=UI_CONFIG["dimensions"]["sidebar_width"],
            relief=tk.FLAT,
            borderwidth=0
        )
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar_frame.pack_propagate(False)  # Maintain fixed width
        
        # Header with theme toggle
        header_frame = tk.Frame(self.sidebar_frame)
        header_frame.pack(fill=tk.X, padx=15, pady=(15, 10))
        
        # Projects title
        self.title_label = tk.Label(
            header_frame,
            text="Projects",
            font=("SF Pro Display", 16, "bold"),
            anchor=tk.W
        )
        self.title_label.pack(side=tk.LEFT)
        
        # Theme toggle button
        self.theme_button = tk.Button(
            header_frame,
            text="🌙",
            font=("SF Pro Display", 14),
            command=self._on_theme_toggle,
            relief=tk.FLAT,
            width=3,
            height=1,
            cursor="hand2"
        )
        self.theme_button.pack(side=tk.RIGHT)
        
        # Create new project button
        self.create_button = tk.Button(
            self.sidebar_frame,
            text="+ Create New Project",
            command=self._on_create_new,
            font=("SF Pro Display", 11, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=12,
            cursor="hand2"
        )
        self.create_button.pack(fill=tk.X, padx=15, pady=(5, 20))
        
        # Scrollable project list
        self.list_frame = tk.Frame(self.sidebar_frame)
        self.list_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Status legend
        self.legend_frame = tk.Frame(self.sidebar_frame)
        self.legend_frame.pack(fill=tk.X, padx=15, pady=15, side=tk.BOTTOM)
        
        self.legend_title = tk.Label(
            self.legend_frame,
            text="Status:",
            font=("SF Pro Display", 10, "bold")
        )
        self.legend_title.pack(anchor=tk.W)
        
        self.legend_labels = []
        for status, color in [("running", "🟢 Running"), ("stopped", "🔴 Stopped"), 
                             ("starting", "🟡 Starting"), ("created", "⚪ Ready")]:
            label = tk.Label(
                self.legend_frame,
                text=color,
                font=("SF Pro Display", 9)
            )
            label.pack(anchor=tk.W)
            self.legend_labels.append(label)
            
        self.apply_theme()
            
    def apply_theme(self):
        """Apply current theme to sidebar."""
        # Main sidebar frame
        self.sidebar_frame.configure(bg=self.theme["sidebar"]["bg"])
        
        # Header elements
        self.title_label.configure(
            fg=self.theme["sidebar"]["header_fg"],
            bg=self.theme["sidebar"]["header_bg"]
        )
        
        # Theme toggle button
        from config.settings import THEMES
        theme_icon = "☀️" if get_current_theme() == THEMES["dark"] else "🌙"
        self.theme_button.configure(
            bg=self.theme["buttons"]["light_bg"],
            fg=self.theme["buttons"]["light_fg"],
            activebackground=self.theme["sidebar"]["hover_bg"],
            text=theme_icon
        )
        
        # Create button
        self.create_button.configure(
            bg=self.theme["buttons"]["success_bg"],
            fg=self.theme["buttons"]["success_fg"],
            activebackground=self.theme["colors"]["success"]
        )
        
        # Frames
        for frame in [self.sidebar_frame, self.list_frame, self.legend_frame]:
            if hasattr(frame, 'configure'):
                frame.configure(bg=self.theme["sidebar"]["bg"])
        
        # Legend
        self.legend_title.configure(
            fg=self.theme["sidebar"]["fg"],
            bg=self.theme["sidebar"]["bg"]
        )
        
        for label in self.legend_labels:
            label.configure(
                fg=self.theme["sidebar"]["fg"],
                bg=self.theme["sidebar"]["bg"]
            )
            
        # Update all project items
        for item in self.project_items.values():
            if hasattr(item, 'refresh_theme'):
                item.refresh_theme()
                
    def _on_theme_toggle(self):
        """Handle theme toggle button click."""
        from config.settings import toggle_theme
        new_theme = toggle_theme()
        self.refresh_theme()
        
        if self.theme_callback:
            self.theme_callback(new_theme)
             
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