# Project Runner App V8 - Modern Themes

A sophisticated desktop GUI application for managing and running multiple development projects simultaneously with modern dark and light theme support.

## ✨ Features

### 🎨 Modern Theming System
- **Light Theme**: Clean, professional light interface
- **Dark Theme**: Modern dark mode for comfortable coding sessions
- **Real-time Theme Switching**: Toggle between themes with a single click
- **Theme-aware Components**: All UI elements automatically adapt to the selected theme

### 🚀 Project Management
- **Multi-Instance Support**: Run multiple projects simultaneously
- **Project Types**: Built-in support for Angular, Laravel, and Custom projects
- **Custom Naming**: Give your projects meaningful names and descriptions
- **Status Indicators**: Real-time visual status with color-coded indicators:
  - 🟢 **Running**: Project is actively running
  - 🔴 **Stopped**: Project has been stopped
  - 🟡 **Starting**: Project is starting up
  - ⚪ **Ready**: Project created but not yet run

### 🖥️ User Interface
- **Sidebar Navigation**: Clean project list with status indicators
- **Modern Typography**: SF Pro Display font for a professional look
- **Responsive Design**: Adapts to different window sizes
- **Intuitive Controls**: Easy-to-use buttons and forms

### ⚙️ Technical Features
- **Real-time Output Streaming**: See command output as it happens
- **Automatic Port Management**: Handles port conflicts automatically
- **Process Management**: Safe process starting and stopping
- **Thread-safe Operations**: Reliable multi-threading for UI responsiveness

## 🏗️ Architecture

The application follows a modular architecture with clear separation of concerns:

```
project-runner/
├── main.py                 # Application entry point
├── config/
│   └── settings.py        # Configuration and theme definitions
├── core/
│   ├── process_manager.py # Process handling and threading
│   └── port_manager.py    # Port management utilities
└── gui/
    ├── main_window.py     # Main application window
    └── widgets.py         # Custom UI components
```

## 🎯 Usage

### Starting the Application
```bash
python3 main.py
```

### Creating Projects
1. Click **"+ Create New Project"** in the sidebar or welcome screen
2. Enter a project name and optional description
3. Select your project type (Angular, Laravel, or Custom)
4. Click **"Create Project"**

### Managing Projects
- **Select**: Click on any project in the sidebar to view/edit it
- **Run**: Click "Run Command" to start the project
- **Stop**: Click "Stop Command" to stop a running project
- **Delete**: Click the red "×" button to delete a project (with confirmation)

### Theme Switching
- Click the theme toggle button (🌙/☀️) in the sidebar header
- The entire interface will instantly switch between light and dark themes
- Your theme preference is maintained during the session

## 🎨 Theme System

### Light Theme
- **Background**: Clean whites and light grays
- **Text**: Dark text for excellent readability
- **Accents**: Professional blue and green highlights
- **Perfect for**: Bright environments and daytime coding

### Dark Theme
- **Background**: Deep grays and blacks
- **Text**: Light text optimized for dark backgrounds
- **Accents**: Vibrant colors that pop against dark backgrounds
- **Perfect for**: Low-light environments and extended coding sessions

### Theme Configuration
Themes are defined in `config/settings.py` with comprehensive color schemes:

```python
THEMES = {
    "light": {
        "main": {"bg": "#ffffff", "fg": "#212529"},
        "sidebar": {"bg": "#f8f9fa", "selected_bg": "#e3f2fd"},
        "content": {"bg": "#ffffff", "fg": "#212529"},
        "buttons": {"success_bg": "#28a745", "primary_bg": "#007bff"}
    },
    "dark": {
        "main": {"bg": "#1a1a1a", "fg": "#e9ecef"},
        "sidebar": {"bg": "#2d3748", "selected_bg": "#4a5568"},
        "content": {"bg": "#1a1a1a", "fg": "#e9ecef"},
        "buttons": {"success_bg": "#198754", "primary_bg": "#0d6efd"}
    }
}
```

## 🔧 Requirements

- **Python 3.9+**
- **tkinter** (usually included with Python)
- **macOS, Windows, or Linux**

## 📦 Installation

1. Clone or download the project files
2. Ensure Python 3.9+ is installed
3. Run the application:
   ```bash
   python3 main.py
   ```

No additional dependencies required - uses only Python standard library!

## 🎮 Keyboard Shortcuts

- **Cmd/Ctrl + Q**: Quit application
- **Enter**: In create dialog, creates the project
- **Escape**: Closes dialogs

## 🔍 Project Types

### Angular Projects
- **Default Command**: `ng serve`
- **Default Port**: 4200
- **Auto-configured**: Ready to run Angular development server

### Laravel Projects
- **Default Command**: `php artisan serve`
- **Default Port**: 8000
- **Auto-configured**: Ready to run Laravel development server

### Custom Projects
- **Flexible Command**: Enter any command you need
- **No Port Restrictions**: Perfect for scripts, build tools, or any custom workflow

## 🛡️ Safety Features

- **Confirmation Dialogs**: Prevents accidental project deletion
- **Process Cleanup**: Automatically stops processes when deleting projects
- **Port Conflict Resolution**: Handles port conflicts gracefully
- **Thread Safety**: Prevents UI freezing during long operations

## 🎨 Customization

The theming system is highly customizable. You can:

1. **Modify Existing Themes**: Edit colors in `config/settings.py`
2. **Add New Themes**: Create additional theme definitions
3. **Extend Theme Properties**: Add new theme-aware properties to components

## 🚀 Performance

- **Lightweight**: Minimal resource usage
- **Responsive**: Non-blocking UI operations
- **Efficient**: Smart process and memory management
- **Fast Startup**: Quick application launch time

## 📝 Version History

- **V8**: Modern theming system with light/dark themes
- **V7**: Sidebar interface with status indicators
- **V6**: Multi-instance tabbed interface
- **V5**: Enhanced project management with custom names
- **V4**: Delete functionality and UI improvements
- **V3**: Custom project names and descriptions
- **V2**: Multi-instance support
- **V1**: Basic single-instance functionality

## 🤝 Contributing

This project demonstrates modern Python GUI development with:
- Clean architecture and modular design
- Comprehensive theming system
- Professional UI/UX practices
- Thread-safe operations
- Robust error handling

Feel free to extend and customize for your specific needs!

## 📄 License

Open source - feel free to use, modify, and distribute.

---

**Project Runner App V8** - Where productivity meets beautiful design! 🎨✨ 