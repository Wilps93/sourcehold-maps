#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main build script for creating the complete installer
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, cwd=None, check=True):
    """Run a command and return the result"""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        if check:
            return False
    else:
        print(f"Success: {result.stdout}")
    return True

def check_nsis():
    """Check if NSIS is available"""
    try:
        result = subprocess.run(["makensis", "/VERSION"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"NSIS found: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    
    print("NSIS not found. Please install NSIS and add it to PATH.")
    print("Download from: https://nsis.sourceforge.io/Download")
    return False

def main():
    """Main build function"""
    print("=== Sourcehold Maps Converter Installer Builder ===")
    
    # Step 1: Download dependencies
    print("\n1. Downloading dependencies...")
    if not run_command("python download_dependencies.py"):
        print("Failed to download dependencies")
        return False
    
    # Step 2: Install Python dependencies
    print("\n2. Installing Python dependencies...")
    if not run_command("pip install -r requirements.txt"):
        print("Failed to install Python dependencies")
        return False
    
    # Step 3: Build executable
    print("\n3. Building executable...")
    if not run_command("python build_exe.py"):
        print("Failed to build executable")
        return False
    
    # Step 4: Check NSIS
    print("\n4. Checking NSIS...")
    if not check_nsis():
        return False
    
    # Step 5: Build installer
    print("\n5. Building installer...")
    if not run_command("makensis installer.nsi"):
        print("Failed to build installer")
        return False
    
    # Step 6: Cleanup
    print("\n6. Cleaning up...")
    build_dir = Path("build")
    if build_dir.exists():
        shutil.rmtree(build_dir)
    
    spec_file = Path("sourcehold-converter.spec")
    if spec_file.exists():
        spec_file.unlink()
    
    print("\n=== Build completed successfully! ===")
    print("Installer created: SourceholdMapsConverter-Setup.exe")
    print("\nThe installer will:")
    print("- Install Python 3.11 if not present")
    print("- Install Visual C++ Redistributable if needed")
    print("- Install Python dependencies (Pillow, pymem, dclimplode, numpy, opencv-python)")
    print("- Create desktop and start menu shortcuts")
    print("- Register the application for easy uninstallation")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)