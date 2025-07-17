#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for the GUI application
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import tkinter
        print("✓ tkinter available")
    except ImportError as e:
        print(f"✗ tkinter not available: {e}")
        return False
    
    try:
        from sourcehold import load_map, save_map
        print("✓ sourcehold package available")
    except ImportError as e:
        print(f"✗ sourcehold package not available: {e}")
        return False
    
    try:
        import PIL
        print("✓ Pillow available")
    except ImportError as e:
        print(f"✗ Pillow not available: {e}")
    
    try:
        import pymem
        print("✓ pymem available")
    except ImportError as e:
        print(f"✗ pymem not available: {e}")
    
    try:
        import dclimplode
        print("✓ dclimplode available")
    except ImportError as e:
        print(f"✗ dclimplode not available: {e}")
    
    try:
        import numpy
        print("✓ numpy available")
    except ImportError as e:
        print(f"✗ numpy not available: {e}")
    
    try:
        import cv2
        print("✓ opencv-python available")
    except ImportError as e:
        print(f"✗ opencv-python not available: {e}")
    
    return True

def test_gui():
    """Test the GUI application"""
    print("\nTesting GUI application...")
    
    try:
        from sourcehold_converter_gui import SourceholdConverterGUI
        import tkinter as tk
        
        root = tk.Tk()
        app = SourceholdConverterGUI(root)
        print("✓ GUI application created successfully")
        
        # Close the window after a short delay
        root.after(2000, root.destroy)
        root.mainloop()
        
        print("✓ GUI application test completed")
        return True
        
    except Exception as e:
        print(f"✗ GUI application test failed: {e}")
        return False

def main():
    """Main test function"""
    print("=== Sourcehold Maps Converter GUI Test ===")
    
    if not test_imports():
        print("\nImport test failed. Please install missing dependencies.")
        return False
    
    if not test_gui():
        print("\nGUI test failed.")
        return False
    
    print("\n=== All tests passed! ===")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)