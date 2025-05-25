"""
Custom widgets and UI components for Project Runner App.
"""

import tkinter as tk
from tkinter import scrolledtext
from config.settings import UI_CONFIG, OUTPUT_TAGS


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