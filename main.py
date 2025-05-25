#!/usr/bin/env python3
"""
Project Runner App - Main Entry Point

A desktop GUI application for running Angular, Laravel, and custom development projects
with real-time output display and process management.
"""

from gui.main_window import MainWindow


def main():
    """Main entry point for the Project Runner App."""
    app = MainWindow()
    app.run()


if __name__ == "__main__":
    main() 