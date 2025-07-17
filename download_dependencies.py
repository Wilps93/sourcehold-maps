#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Download dependencies for the installer
"""

import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

# URLs for dependencies
DEPENDENCIES = {
    "python-3.11.8-amd64.exe": "https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe",
    "vc_redist.x64.exe": "https://aka.ms/vs/17/release/vc_redist.x64.exe"
}

def download_file(url, filename):
    """Download a file from URL"""
    print(f"Downloading {filename}...")
    
    try:
        urllib.request.urlretrieve(url, filename)
        print(f"Successfully downloaded {filename}")
        return True
    except urllib.error.URLError as e:
        print(f"Failed to download {filename}: {e}")
        return False

def main():
    """Main function"""
    print("Downloading dependencies for Sourcehold Maps Converter installer...")
    
    # Create dependencies directory
    deps_dir = Path("dependencies")
    deps_dir.mkdir(exist_ok=True)
    
    # Download each dependency
    success_count = 0
    for filename, url in DEPENDENCIES.items():
        filepath = deps_dir / filename
        
        if filepath.exists():
            print(f"{filename} already exists, skipping...")
            success_count += 1
        else:
            if download_file(url, str(filepath)):
                success_count += 1
    
    print(f"\nDownloaded {success_count}/{len(DEPENDENCIES)} dependencies")
    
    if success_count == len(DEPENDENCIES):
        print("All dependencies downloaded successfully!")
        return True
    else:
        print("Some dependencies failed to download.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)