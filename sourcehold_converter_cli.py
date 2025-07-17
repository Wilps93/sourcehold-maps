#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sourcehold Maps Converter CLI
Command line interface for converting Stronghold Crusader map files
"""

import argparse
import sys
import os
from pathlib import Path

# Add the sourcehold package to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from sourcehold import load_map, save_map
    from sourcehold.maps.Map import Map
    SOURCEHOLD_AVAILABLE = True
except ImportError:
    SOURCEHOLD_AVAILABLE = False
    print("ERROR: Sourcehold package not found. Please ensure it's properly installed.")
    sys.exit(1)

def check_dependencies():
    """Check if all required dependencies are available"""
    missing_deps = []
    
    try:
        import PIL
    except ImportError:
        missing_deps.append("Pillow")
    
    try:
        import pymem
    except ImportError:
        missing_deps.append("pymem")
    
    try:
        import dclimplode
    except ImportError:
        missing_deps.append("dclimplode")
    
    try:
        import numpy
    except ImportError:
        missing_deps.append("numpy")
    
    try:
        import cv2
    except ImportError:
        missing_deps.append("opencv-python")
    
    if missing_deps:
        print(f"WARNING: Missing dependencies: {', '.join(missing_deps)}")
        print("Some features may not work properly.")
        return False
    
    return True

def unpack_file(input_path, output_path, verbose=False):
    """Unpack a map file to a folder"""
    if verbose:
        print(f"Loading map file: {input_path}")
    
    map_obj = load_map(input_path)
    
    input_name = Path(input_path).stem
    output_folder = Path(output_path) / input_name
    
    if not output_folder.exists():
        output_folder.mkdir(parents=True)
    
    if verbose:
        print(f"Unpacking to: {output_folder}")
    
    map_obj.dump_to_folder(str(output_folder))
    
    if verbose:
        print(f"Successfully unpacked {input_name}")
    
    return True

def pack_folder(input_path, output_path, verbose=False):
    """Pack a folder into a map file"""
    if verbose:
        print(f"Loading folder: {input_path}")
    
    map_obj = Map().load_from_folder(input_path)
    
    input_name = Path(input_path).name
    output_file = Path(output_path) / f"{input_name}.map"
    
    if verbose:
        print(f"Packing to: {output_file}")
    
    map_obj.pack(True)
    save_map(map_obj, str(output_file))
    
    if verbose:
        print(f"Successfully packed {input_name}")
    
    return True

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Sourcehold Maps Converter - Convert Stronghold Crusader map files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Unpack a map file
  python sourcehold_converter_cli.py unpack --input map1.map --output ./output
  
  # Pack a folder into a map file
  python sourcehold_converter_cli.py pack --input ./map_folder --output ./output
  
  # Verbose mode
  python sourcehold_converter_cli.py unpack --input map1.map --output ./output --verbose
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Unpack command
    unpack_parser = subparsers.add_parser('unpack', help='Unpack a map file to a folder')
    unpack_parser.add_argument('--input', '-i', required=True, help='Input map file (.map, .sav, .msv)')
    unpack_parser.add_argument('--output', '-o', required=True, help='Output directory')
    unpack_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    # Pack command
    pack_parser = subparsers.add_parser('pack', help='Pack a folder into a map file')
    pack_parser.add_argument('--input', '-i', required=True, help='Input folder')
    pack_parser.add_argument('--output', '-o', required=True, help='Output directory')
    pack_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Check dependencies
    if not check_dependencies():
        print("Some dependencies are missing. Consider installing them:")
        print("pip install Pillow pymem dclimplode numpy opencv-python")
    
    # Validate inputs
    if not os.path.exists(args.input):
        print(f"ERROR: Input path does not exist: {args.input}")
        sys.exit(1)
    
    if not os.path.exists(args.output):
        try:
            os.makedirs(args.output, exist_ok=True)
        except Exception as e:
            print(f"ERROR: Cannot create output directory: {e}")
            sys.exit(1)
    
    try:
        if args.command == 'unpack':
            if not args.input.lower().endswith(('.map', '.sav', '.msv')):
                print("WARNING: Input file doesn't have expected extension (.map, .sav, .msv)")
            
            success = unpack_file(args.input, args.output, args.verbose)
        elif args.command == 'pack':
            if not os.path.isdir(args.input):
                print(f"ERROR: Input must be a directory for pack command: {args.input}")
                sys.exit(1)
            
            success = pack_folder(args.input, args.output, args.verbose)
        
        if success:
            print("Operation completed successfully!")
        else:
            print("Operation failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()