#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sourcehold Maps Converter GUI
A graphical interface for converting Stronghold Crusader map files
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
import subprocess
from pathlib import Path
import queue

# Add the sourcehold package to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from sourcehold import load_map, save_map
    from sourcehold.maps.Map import Map
    SOURCEHOLD_AVAILABLE = True
except ImportError:
    SOURCEHOLD_AVAILABLE = False

class SourceholdConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sourcehold Maps Converter v1.1.0")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Set icon if available
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
        
        self.setup_ui()
        self.log_queue = queue.Queue()
        self.check_dependencies()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Sourcehold Maps Converter", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Input file selection
        ttk.Label(main_frame, text="Input File:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.input_var = tk.StringVar()
        input_entry = ttk.Entry(main_frame, textvariable=self.input_var, width=50)
        input_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_input).grid(row=1, column=2, pady=5)
        
        # Output directory selection
        ttk.Label(main_frame, text="Output Directory:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.output_var = tk.StringVar()
        output_entry = ttk.Entry(main_frame, textvariable=self.output_var, width=50)
        output_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_output).grid(row=2, column=2, pady=5)
        
        # Operation selection
        ttk.Label(main_frame, text="Operation:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.operation_var = tk.StringVar(value="unpack")
        operation_frame = ttk.Frame(main_frame)
        operation_frame.grid(row=3, column=1, sticky=tk.W, padx=(5, 0), pady=5)
        
        ttk.Radiobutton(operation_frame, text="Unpack (.map/.sav/.msv → Folder)", 
                       variable=self.operation_var, value="unpack").pack(side=tk.LEFT)
        ttk.Radiobutton(operation_frame, text="Pack (Folder → .map/.sav/.msv)", 
                       variable=self.operation_var, value="pack").pack(side=tk.LEFT, padx=(10, 0))
        
        # Convert button
        self.convert_btn = ttk.Button(main_frame, text="Convert", command=self.start_conversion)
        self.convert_btn.grid(row=3, column=2, pady=5)
        
        # Progress bar
        self.progress_var = tk.StringVar(value="Ready")
        ttk.Label(main_frame, textvariable=self.progress_var).grid(row=4, column=0, columnspan=3, sticky=tk.W, pady=(10, 5))
        
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Log area
        ttk.Label(main_frame, text="Log:").grid(row=6, column=0, sticky=tk.W, pady=(10, 5))
        
        log_frame = ttk.Frame(main_frame)
        log_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Bind events
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def check_dependencies(self):
        """Check if all required dependencies are available"""
        if not SOURCEHOLD_AVAILABLE:
            self.log("ERROR: Sourcehold package not found. Please ensure it's properly installed.")
            self.convert_btn.config(state='disabled')
            return
            
        try:
            import PIL
            import pymem
            import dclimplode
            import numpy
            import cv2
            self.log("All dependencies are available.")
        except ImportError as e:
            self.log(f"WARNING: Missing dependency: {e}")
            self.log("Some features may not work properly.")
            
    def browse_input(self):
        """Browse for input file or directory"""
        if self.operation_var.get() == "unpack":
            filename = filedialog.askopenfilename(
                title="Select map file",
                filetypes=[
                    ("Map files", "*.map *.sav *.msv"),
                    ("All files", "*.*")
                ]
            )
        else:
            filename = filedialog.askdirectory(title="Select folder to pack")
            
        if filename:
            self.input_var.set(filename)
            
    def browse_output(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory(title="Select output directory")
        if directory:
            self.output_var.set(directory)
            
    def log(self, message):
        """Add message to log"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def start_conversion(self):
        """Start the conversion process in a separate thread"""
        if not self.validate_inputs():
            return
            
        self.convert_btn.config(state='disabled')
        self.progress.start()
        self.progress_var.set("Converting...")
        
        # Start conversion in separate thread
        thread = threading.Thread(target=self.convert, daemon=True)
        thread.start()
        
    def validate_inputs(self):
        """Validate input parameters"""
        input_path = self.input_var.get().strip()
        output_path = self.output_var.get().strip()
        
        if not input_path:
            messagebox.showerror("Error", "Please select an input file/folder.")
            return False
            
        if not output_path:
            messagebox.showerror("Error", "Please select an output directory.")
            return False
            
        if not os.path.exists(input_path):
            messagebox.showerror("Error", f"Input path does not exist: {input_path}")
            return False
            
        return True
        
    def convert(self):
        """Perform the actual conversion"""
        try:
            input_path = self.input_var.get().strip()
            output_path = self.output_var.get().strip()
            operation = self.operation_var.get()
            
            self.log(f"Starting {operation} operation...")
            self.log(f"Input: {input_path}")
            self.log(f"Output: {output_path}")
            
            if operation == "unpack":
                self.unpack_file(input_path, output_path)
            else:
                self.pack_folder(input_path, output_path)
                
            self.log("Conversion completed successfully!")
            self.progress_var.set("Completed")
            
        except Exception as e:
            self.log(f"ERROR: {str(e)}")
            self.progress_var.set("Failed")
            messagebox.showerror("Error", f"Conversion failed: {str(e)}")
        finally:
            self.progress.stop()
            self.convert_btn.config(state='normal')
            
    def unpack_file(self, input_path, output_path):
        """Unpack a map file to a folder"""
        self.log("Loading map file...")
        map_obj = load_map(input_path)
        
        input_name = Path(input_path).stem
        output_folder = Path(output_path) / input_name
        
        if not output_folder.exists():
            output_folder.mkdir(parents=True)
            
        self.log(f"Unpacking to: {output_folder}")
        map_obj.dump_to_folder(str(output_folder))
        
        self.log(f"Successfully unpacked {input_name}")
        
    def pack_folder(self, input_path, output_path):
        """Pack a folder into a map file"""
        self.log("Loading folder...")
        map_obj = Map().load_from_folder(input_path)
        
        input_name = Path(input_path).name
        output_file = Path(output_path) / f"{input_name}.map"
        
        self.log(f"Packing to: {output_file}")
        map_obj.pack(True)
        save_map(map_obj, str(output_file))
        
        self.log(f"Successfully packed {input_name}")
        
    def on_closing(self):
        """Handle window closing"""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()

def main():
    """Main entry point"""
    root = tk.Tk()
    app = SourceholdConverterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()