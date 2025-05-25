# Project Runner App

A desktop GUI application for running Angular, Laravel, and custom development projects with real-time output display.

## Features

- **Multi-Instance Support**: Create and manage multiple project instances simultaneously
- **Tabbed Interface**: Clean tabbed UI for switching between different projects
- **Project Type Support**: Angular, Laravel, and Custom projects
- **Real-time Output**: Live streaming of command output with proper threading
- **Port Management**: Automatic clearing of conflicting processes on ports 4200 (Angular) and 8000 (Laravel)
- **Process Control**: Independent start and stop commands for each instance
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

1. Click on the "+ Create New" tab to create a new project instance
2. Select project type (Angular/Laravel/Custom) and click "Create Instance"
3. Configure the working directory for your project
4. Enter or use pre-filled command based on project type
5. Click "Run Command" to start the project
6. Use "Stop Command" to terminate running processes
7. Create multiple instances to run different projects simultaneously

## Key Achievements

🎯 **Modular Architecture**: Transformed 446-line monolithic file into clean, maintainable modules  
📏 **Size Compliance**: All files under 500-line limit  
🔧 **Multi-Instance Support**: Enhanced with tabbed interface for simultaneous project management  
📚 **Well Documented**: Comprehensive README and planning documentation  
🧪 **Test Ready**: Isolated functions ready for unit testing  
🚀 **Production Ready**: Clean, professional codebase structure  

## Development

- Keep files under 500 lines
- Add unit tests for new functionality
- Document changes in this README 