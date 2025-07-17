#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build script for creating executable file
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and return the result"""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    print(f"Success: {result.stdout}")
    return True

def main():
    """Main build function"""
    print("Building Sourcehold Maps Converter executable...")
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print("PyInstaller is available")
    except ImportError:
        print("Installing PyInstaller...")
        if not run_command("pip install pyinstaller"):
            print("Failed to install PyInstaller")
            return False
    
    # Create dist directory if it doesn't exist
    dist_dir = Path("dist")
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir()
    
    # Build the GUI executable
    print("Building GUI executable...")
    gui_cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=sourcehold-converter-gui",
        "--add-data=sourcehold;sourcehold",
        "--hidden-import=PIL",
        "--hidden-import=pymem",
        "--hidden-import=dclimplode",
        "--hidden-import=numpy",
        "--hidden-import=cv2",
        "--hidden-import=tkinter",
        "--hidden-import=tkinter.ttk",
        "--hidden-import=tkinter.filedialog",
        "--hidden-import=tkinter.messagebox",
        "--hidden-import=tkinter.scrolledtext",
        "--hidden-import=sourcehold.aivs",
        "--hidden-import=sourcehold.tool.convert.aiv",
        "sourcehold_converter_gui.py"
    ]
    
    if not run_command(" ".join(gui_cmd)):
        print("Failed to build GUI executable")
        return False
    
    # Build the CLI executable
    print("Building CLI executable...")
    cli_cmd = [
        "pyinstaller",
        "--onefile",
        "--name=sourcehold-converter-cli",
        "--add-data=sourcehold;sourcehold",
        "--hidden-import=PIL",
        "--hidden-import=pymem",
        "--hidden-import=dclimplode",
        "--hidden-import=numpy",
        "--hidden-import=cv2",
        "--hidden-import=sourcehold.aivs",
        "--hidden-import=sourcehold.tool.convert.aiv",
        "sourcehold_converter_cli.py"
    ]
    
    if not run_command(" ".join(cli_cmd)):
        print("Failed to build CLI executable")
        return False
    
    # Copy GUI executable to main name for installer
    import shutil
    gui_exe = dist_dir / "sourcehold-converter-gui.exe"
    main_exe = dist_dir / "sourcehold-converter.exe"
    if gui_exe.exists():
        shutil.copy2(gui_exe, main_exe)
        print(f"Copied {gui_exe} to {main_exe}")
    
    print("Build completed successfully!")
    print(f"GUI executable: {dist_dir / 'sourcehold-converter-gui.exe'}")
    print(f"CLI executable: {dist_dir / 'sourcehold-converter-cli.exe'}")
    print(f"Main executable: {dist_dir / 'sourcehold-converter.exe'}")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)