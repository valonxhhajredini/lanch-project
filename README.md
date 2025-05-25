# Project Runner App

A desktop GUI application for running Angular, Laravel, and custom development projects with real-time output display.

## Features

- **Multi-Instance Support**: Create and manage multiple project instances simultaneously
- **Sidebar Interface**: Clean sidebar with project list and visual status indicators
- **Status Indicators**: Color-coded status (🟢 Running, 🔴 Stopped, 🟡 Starting, ⚪ Ready)
- **Project Type Support**: Angular, Laravel, and Custom projects
- **Real-time Output**: Live streaming of command output with proper threading
- **Port Management**: Automatic clearing of conflicting processes on ports 4200 (Angular) and 8000 (Laravel)
- **Process Control**: Independent start and stop commands for each instance
- **Dashboard Design**: Modern, intuitive interface with welcome screen
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

1. Click "+ Create New Project" in the sidebar or welcome screen
2. Select project type (Angular/Laravel/Custom) in the dialog
3. Click "Create Project" to add it to your sidebar
4. Configure the working directory for your project
5. Enter or use pre-filled command based on project type
6. Click "Run Command" to start the project (status turns 🟢 green)
7. Use "Stop Command" to terminate running processes (status turns 🔴 red)
8. Create multiple instances and switch between them using the sidebar
9. Monitor all project statuses at a glance with color-coded indicators

## Key Achievements

🎯 **Modular Architecture**: Transformed 446-line monolithic file into clean, maintainable modules  
📏 **Size Compliance**: All files under 500-line limit  
🔧 **Multi-Instance Support**: Enhanced with sidebar interface for simultaneous project management  
🎨 **Modern UI Design**: Sidebar with color-coded status indicators and dashboard layout  
📚 **Well Documented**: Comprehensive README and planning documentation  
🧪 **Test Ready**: Isolated functions ready for unit testing  
🚀 **Production Ready**: Clean, professional codebase structure  

## Development

- Keep files under 500 lines
- Add unit tests for new functionality
- Document changes in this README 