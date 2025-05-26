"""
Application settings and constants for Project Runner App.
"""

# Project type configurations
PROJECT_TYPES = {
    "Angular": {
        "command": "ng serve",
        "port": 4200,
        "readonly": True
    },
    "Laravel": {
        "command": "php artisan serve",
        "port": 8000,
        "readonly": True
    },
    "Custom": {
        "command": "",
        "port": None,
        "readonly": False
    }
}

# UI Configuration
UI_CONFIG = {
    "window_title": "Project Runner App V8 - Modern Themes",
    "dimensions": {
        "output_height": 15,
        "output_width": 70,
        "command_entry_width": 60,
        "sidebar_width": 280,
        "sidebar_item_height": 90
    }
}

# Theme configurations
THEMES = {
    "light": {
        "name": "Light Theme",
        "colors": {
            "primary": "#007bff",
            "success": "#28a745",
            "success_hover": "#218838",
            "danger": "#dc3545",
            "danger_hover": "#c82333",
            "warning": "#ffc107",
            "info": "#17a2b8",
            "light": "#f8f9fa",
            "dark": "#343a40",
            "white": "#ffffff",
            "black": "#000000"
        },
        "main": {
            "bg": "#ffffff",
            "fg": "#212529",
            "border": "#dee2e6"
        },
        "sidebar": {
            "bg": "#f8f9fa",
            "fg": "#495057",
            "selected_bg": "#e3f2fd",
            "hover_bg": "#e9ecef",
            "border": "#dee2e6",
            "header_bg": "#ffffff",
            "header_fg": "#212529"
        },
        "content": {
            "bg": "#ffffff",
            "fg": "#212529",
            "input_bg": "#ffffff",
            "input_fg": "#495057",
            "input_border": "#ced4da",
            "readonly_bg": "#e9ecef",
            "output_bg": "#ffffff",
            "output_fg": "#212529"
        },
        "buttons": {
            "primary_bg": "#007bff",
            "primary_fg": "#ffffff",
            "success_bg": "#28a745",
            "success_fg": "#ffffff",
            "danger_bg": "#dc3545",
            "danger_fg": "#ffffff",
            "secondary_bg": "#6c757d",
            "secondary_fg": "#ffffff",
            "light_bg": "#f8f9fa",
            "light_fg": "#495057"
        }
    },
    "dark": {
        "name": "Dark Theme",
        "colors": {
            "primary": "#0d6efd",
            "success": "#198754",
            "success_hover": "#157347",
            "danger": "#dc3545",
            "danger_hover": "#bb2d3b",
            "warning": "#fd7e14",
            "info": "#0dcaf0",
            "light": "#f8f9fa",
            "dark": "#212529",
            "white": "#ffffff",
            "black": "#000000"
        },
        "main": {
            "bg": "#1a1a1a",
            "fg": "#e9ecef",
            "border": "#495057"
        },
        "sidebar": {
            "bg": "#2d3748",
            "fg": "#e2e8f0",
            "selected_bg": "#4a5568",
            "hover_bg": "#374151",
            "border": "#4a5568",
            "header_bg": "#1a202c",
            "header_fg": "#f7fafc"
        },
        "content": {
            "bg": "#1a1a1a",
            "fg": "#e9ecef",
            "input_bg": "#2d3748",
            "input_fg": "#e2e8f0",
            "input_border": "#4a5568",
            "readonly_bg": "#374151",
            "output_bg": "#1e1e1e",
            "output_fg": "#e9ecef"
        },
        "buttons": {
            "primary_bg": "#0d6efd",
            "primary_fg": "#ffffff",
            "success_bg": "#198754",
            "success_fg": "#ffffff",
            "danger_bg": "#dc3545",
            "danger_fg": "#ffffff",
            "secondary_bg": "#6c757d",
            "secondary_fg": "#ffffff",
            "light_bg": "#495057",
            "light_fg": "#e9ecef"
        }
    }
}

# Process management settings
PROCESS_CONFIG = {
    "queue_check_interval": 100,  # milliseconds
    "port_check_timeout": 5,      # seconds
    "process_kill_timeout": 10,   # seconds
    "thread_join_timeout": 1,     # seconds
    "graceful_shutdown_timeout": 0.5  # seconds
}

# Output text tags configuration
OUTPUT_TAGS = {
    "error_tag": {"foreground": "black"},
    "info_tag": {"foreground": "black", "font": ("Helvetica", "9", "bold")},
    "stdout_tag": {"foreground": "black"},
    "stderr_tag": {"foreground": "black"},
    "init_msg_visible_test": {"foreground": "black", "background": "white"}
}

# Initial messages
MESSAGES = {
    "initial_output": "OUTPUT VISIBILITY TEST (Black on White). Waiting for command...\n-------------------------------------\n",
    "process_ended": "\n--- Process Ended/Stopped ---\n",
    "no_command": "No command entered.\n",
    "command_running": "Command already running.\n",
    "no_command_to_stop": "--- No command to stop. ---\n",
    "welcome_message": "Welcome to Project Runner!\n\nSelect a project type below and click 'Create Instance' to start managing your projects.\n\nYou can create multiple instances and run them simultaneously in separate tabs.",
    "instance_created": "Instance created successfully! Configure your project settings above."
}

# Project management settings
PROJECT_CONFIG = {
    "max_name_length": 25,
    "default_names": {
        "Angular": "Angular Project",
        "Laravel": "Laravel Project", 
        "Custom": "Custom Script"
    }
}

# Status configuration
STATUS_CONFIG = {
    "colors": {
        "running": "#28a745",     # Green
        "stopped": "#dc3545",     # Red  
        "starting": "#ffc107",    # Yellow
        "stopping": "#fd7e14",    # Orange
        "created": "#6c757d"      # Gray
    },
    "indicators": {
        "running": "●",
        "stopped": "●", 
        "starting": "●",
        "stopping": "●",
        "created": "○"
    },
    "text": {
        "running": "Running",
        "stopped": "Stopped",
        "starting": "Starting...",
        "stopping": "Stopping...",
        "created": "Ready"
    }
}

# Default theme and theme management
DEFAULT_THEME = "light"
CURRENT_THEME = DEFAULT_THEME

def get_current_theme():
    """Get the current theme configuration."""
    return THEMES[CURRENT_THEME]

def set_theme(theme_name):
    """Set the current theme."""
    global CURRENT_THEME
    if theme_name in THEMES:
        CURRENT_THEME = theme_name
        return True
    return False

def toggle_theme():
    """Toggle between light and dark themes."""
    global CURRENT_THEME
    CURRENT_THEME = "dark" if CURRENT_THEME == "light" else "light"
    return THEMES[CURRENT_THEME]

# Performance optimization constants
PERFORMANCE_CONFIG = {
    "max_output_lines": 1000,        # Limit output buffer size
    "ui_update_batch_size": 50,      # Process UI updates in batches
    "memory_cleanup_interval": 30,   # Seconds between memory cleanup
    "max_concurrent_processes": 5,   # Limit concurrent processes
    "output_buffer_size": 8192,      # Buffer size for process output
    "widget_cache_size": 100         # Maximum cached widgets
}

# Database optimization settings
DATABASE_CONFIG = {
    "batch_size": 100,               # Batch database operations
    "connection_timeout": 30,        # Database connection timeout
    "retry_attempts": 3,             # Number of retry attempts
    "cache_ttl": 300,               # Cache time-to-live in seconds
    "vacuum_interval": 86400         # Database vacuum interval (24 hours)
} 