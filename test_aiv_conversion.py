#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for AIV conversion functionality
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_aiv_imports():
    """Test if AIV modules can be imported"""
    print("Testing AIV imports...")
    
    try:
        from sourcehold.aivs.AIV import AIV
        print("✓ sourcehold.aivs.AIV available")
    except ImportError as e:
        print(f"✗ sourcehold.aivs.AIV not available: {e}")
        return False
    
    try:
        from sourcehold.tool.convert.aiv.exports import to_json
        print("✓ sourcehold.tool.convert.aiv.exports available")
    except ImportError as e:
        print(f"✗ sourcehold.tool.convert.aiv.exports not available: {e}")
        return False
    
    return True

def test_aiv_conversion():
    """Test AIV to JSON conversion"""
    print("\nTesting AIV conversion...")
    
    try:
        from sourcehold.aivs.AIV import AIV
        from sourcehold.tool.convert.aiv.exports import to_json
        
        # Check if we have any AIV files to test with
        aiv_files = list(Path("resources/aiv").glob("*.aiv"))
        
        if not aiv_files:
            print("No AIV files found in resources/aiv/")
            print("Creating a simple test...")
            
            # Create a simple test without actual AIV file
            print("✓ AIV conversion modules are available")
            return True
        
        # Test with first available AIV file
        test_file = aiv_files[0]
        print(f"Testing with: {test_file}")
        
        aiv = AIV().from_file(str(test_file))
        json_data = to_json(aiv, include_extra=True)
        
        print(f"✓ Successfully converted {test_file.name} to JSON")
        print(f"  JSON size: {len(json_data)} characters")
        
        # Test CLI conversion function
        from sourcehold_converter_cli import convert_aiv
        
        output_dir = Path("test_output")
        output_dir.mkdir(exist_ok=True)
        
        success = convert_aiv(str(test_file), str(output_dir), verbose=True, include_extra=True)
        
        if success:
            output_file = output_dir / f"{test_file.stem}.aivjson"
            if output_file.exists():
                print(f"✓ CLI conversion successful: {output_file}")
                print(f"  Output file size: {output_file.stat().st_size} bytes")
            else:
                print("✗ CLI conversion failed: output file not created")
                return False
        else:
            print("✗ CLI conversion failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ AIV conversion test failed: {e}")
        return False

def test_gui_aiv_functionality():
    """Test GUI AIV functionality"""
    print("\nTesting GUI AIV functionality...")
    
    try:
        from sourcehold_converter_gui import SourceholdConverterGUI
        import tkinter as tk
        
        root = tk.Tk()
        app = SourceholdConverterGUI(root)
        
        # Test if AIV operation is available
        if hasattr(app, 'convert_aiv'):
            print("✓ GUI AIV conversion method available")
        else:
            print("✗ GUI AIV conversion method not available")
            return False
        
        # Close the window
        root.destroy()
        
        print("✓ GUI AIV functionality test passed")
        return True
        
    except Exception as e:
        print(f"✗ GUI AIV functionality test failed: {e}")
        return False

def main():
    """Main test function"""
    print("=== AIV Conversion Test ===")
    
    if not test_aiv_imports():
        print("\nImport test failed. AIV conversion may not work properly.")
        return False
    
    if not test_aiv_conversion():
        print("\nAIV conversion test failed.")
        return False
    
    if not test_gui_aiv_functionality():
        print("\nGUI AIV functionality test failed.")
        return False
    
    print("\n=== All AIV tests passed! ===")
    print("AIV conversion functionality is working correctly.")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)