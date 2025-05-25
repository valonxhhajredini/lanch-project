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
    "window_title": "Project Runner App V6 - Multi-Instance",
    "colors": {
        "label_fg": "black",
        "label_bg": "#F0F0F0",
        "entry_fg": "black",
        "entry_bg": "white",
        "output_text_fg": "black",
        "output_text_bg": "white",
        "output_cursor_bg": "black",
        "readonly_bg": "#E0E0E0",
        "button_select_color": "#D0D0D0",
        "button_bg": "white"
    },
    "dimensions": {
        "output_height": 15,
        "output_width": 70,
        "command_entry_width": 60
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

# Tab management settings
TAB_CONFIG = {
    "create_tab_title": "+ Create New",
    "max_tab_title_length": 20,
    "default_names": {
        "Angular": "Angular Project",
        "Laravel": "Laravel Project", 
        "Custom": "Custom Script"
    }
} 