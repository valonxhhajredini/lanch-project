# Project Runner App

A desktop GUI application for running Angular, Laravel, and custom development projects with real-time output display.

## Features

- **Project Type Support**: Angular, Laravel, and Custom projects
- **Real-time Output**: Live streaming of command output with proper threading
- **Port Management**: Automatic clearing of conflicting processes on ports 4200 (Angular) and 8000 (Laravel)
- **Process Control**: Start and stop commands with proper process group handling
- **Cross-platform**: Works on macOS, Linux, and Windows

## Project Structure

```
project-runner/
├── README.md
├── main.py              # Entry point
├── gui/
│   ├── __init__.py
│   ├── main_window.py   # Main GUI window and layout
│   └── widgets.py       # Custom UI widgets
├── core/
│   ├── __init__.py
│   ├── process_manager.py  # Process execution and management
│   └── port_manager.py     # Port clearing functionality
└── config/
    ├── __init__.py
    └── settings.py      # Application settings and constants
```

## Installation

1. Ensure Python 3.6+ is installed
2. No additional dependencies required (uses built-in tkinter)

## Usage

```bash
python3 main.py
```

Or test the imports first:
```bash
python3 test_imports.py
```

1. Select project type (Angular/Laravel/Custom)
2. Choose working directory
3. Enter or use pre-filled command
4. Click "Run Command" to start
5. Use "Stop Command" to terminate running processes

## Development

- Keep files under 500 lines
- Add unit tests for new functionality
- Document changes in this README 