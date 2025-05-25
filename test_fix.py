#!/usr/bin/env python3
"""
Test script to verify the UI_CONFIG colors fix.
"""

import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported without errors."""
    try:
        print("Testing imports...")
        
        # Test config imports
        from config.settings import UI_CONFIG, THEMES, get_current_theme
        print("✅ Config imports successful")
        
        # Test core imports
        from core.process_manager import ProcessHandler
        from core.port_manager import find_and_kill_process_on_port
        print("✅ Core imports successful")
        
        # Test GUI imports
        from gui.widgets import ThemedWidget, OutputTextWidget, ProjectInstanceTab, ProjectSidebar
        from gui.main_window import MainWindow
        print("✅ GUI imports successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_theme_system():
    """Test that the theme system works correctly."""
    try:
        print("\nTesting theme system...")
        
        from config.settings import get_current_theme, set_theme, toggle_theme
        
        # Test getting current theme
        theme = get_current_theme()
        print(f"✅ Current theme: {theme['name']}")
        
        # Test theme structure
        required_sections = ['colors', 'main', 'sidebar', 'content', 'buttons']
        for section in required_sections:
            if section not in theme:
                raise KeyError(f"Missing theme section: {section}")
        print("✅ Theme structure is valid")
        
        # Test theme switching
        original_theme = theme['name']
        new_theme = toggle_theme()
        print(f"✅ Theme toggled to: {new_theme}")
        
        # Reset to original
        set_theme("light" if original_theme == "Light Theme" else "dark")
        print("✅ Theme reset successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Theme system error: {e}")
        return False

def test_widget_creation():
    """Test that themed widgets can be created without errors."""
    try:
        print("\nTesting widget creation...")
        
        import tkinter as tk
        from gui.widgets import ThemedWidget, OutputTextWidget
        
        # Create a test root window
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        # Test ThemedWidget
        themed_widget = ThemedWidget()
        print("✅ ThemedWidget created successfully")
        
        # Test OutputTextWidget
        output_widget = OutputTextWidget(root)
        print("✅ OutputTextWidget created successfully")
        
        # Clean up
        root.destroy()
        
        return True
        
    except Exception as e:
        print(f"❌ Widget creation error: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Project Runner App V8 - UI_CONFIG Fix")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_theme_system,
        test_widget_creation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The UI_CONFIG colors fix is working correctly.")
        print("✅ The application should now start without KeyError issues.")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 