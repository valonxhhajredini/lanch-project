# Editor Selector Feature

## Overview
The Project Runner App now includes an editor selector that allows users to choose their preferred code editor for opening projects. The selector is located between the command input field and the output terminal.

## Supported Editors
- **Cursor** - Modern AI-powered code editor
- **VS Code** - Microsoft Visual Studio Code
- **PhpStorm** - JetBrains PHP IDE
- **WebStorm** - JetBrains JavaScript IDE

## Features
- **Visual Icons**: Each editor is represented by its official icon (32x32 pixels)
- **Selection State**: Selected editor is highlighted with primary theme color
- **Theme Support**: Icons and buttons adapt to light/dark themes
- **Fallback Support**: If icons can't be loaded, text-only buttons are displayed

## Technical Implementation
- Icons are stored in `assets/icons/` directory
- Uses Pillow (PIL) library for image processing and resizing
- Graceful fallback if Pillow is not available
- Inherits from `ThemedWidget` for consistent theming

## Dependencies
- Pillow >= 10.0.0 (for image processing)

## Installation
```bash
pip3 install Pillow
```

## Usage
1. Create or select a project
2. Set your working directory for the project
3. Click on any editor icon to:
   - Select that editor as your preference
   - Automatically open the project directory in that editor
4. The selection is maintained per project session
5. Default selection is VS Code

## Editor Commands
The following command-line tools are used to open projects:
- **Cursor**: `cursor <project_directory>`
- **VS Code**: `code <project_directory>`
- **PhpStorm**: `phpstorm <project_directory>`
- **WebStorm**: `webstorm <project_directory>`

**Note**: Make sure the respective editor's command-line tool is installed and available in your system PATH.

## File Structure
```
assets/
├── icons/
│   ├── cursor.png     # Cursor editor icon
│   ├── vscode.png     # VS Code icon
│   ├── phpstorm.png   # PhpStorm icon
│   └── webstorm.png   # WebStorm icon
```

## Installation Requirements
For the editor opening functionality to work, you need to install the command-line tools for your editors:

### VS Code
```bash
# Install VS Code, then enable shell command
# In VS Code: Cmd+Shift+P → "Shell Command: Install 'code' command in PATH"
```

### Cursor
```bash
# Install Cursor, then enable shell command
# In Cursor: Cmd+Shift+P → "Shell Command: Install 'cursor' command in PATH"
```

### PhpStorm
```bash
# Install PhpStorm, then enable shell command
# In PhpStorm: Tools → Create Command-line Launcher
```

### WebStorm
```bash
# Install WebStorm, then enable shell command  
# In WebStorm: Tools → Create Command-line Launcher
```

## Future Enhancements
- Custom editor addition support
- Editor-specific project templates
- Visual feedback for editor opening status
- Fallback options when command-line tools are not available 