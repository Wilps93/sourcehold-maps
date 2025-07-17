import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
import pathlib
import threading
import os
from sourcehold.tool.convert.aiv.exports import to_json
import webbrowser

class AIV2JSONGui(tb.Window):
    def __init__(self):
        super().__init__(themename="superhero")  # Modern Windows 10/11 style
        self.title("AIV to AIVJSON Converter")
        self.geometry("600x400")
        self.resizable(True, True)

        # Adaptive columns and rows
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(6, weight=1)

        self.input_path = tb.StringVar()
        self.output_dir = tb.StringVar()
        self.batch_mode = tb.BooleanVar(value=False)

        # Batch mode checkbox
        self.batch_check = tb.Checkbutton(self, text="Batch convert folder", variable=self.batch_mode, bootstyle="round-toggle")
        self.batch_check.grid(row=0, column=0, columnspan=3, sticky=W, padx=10, pady=(10,0))

        # Input file/folder field and button
        self.input_label = tb.Label(self, text="Select .aiv file or folder with .aiv files:")
        self.input_label.grid(row=1, column=0, sticky=W, padx=10, pady=(10,0))
        self.input_entry = tb.Entry(self, textvariable=self.input_path, width=60)
        self.input_entry.grid(row=2, column=0, padx=(10,0), pady=5, sticky=EW)
        self.input_btn = tb.Button(self, text="Browse...", command=self.select_input, bootstyle=PRIMARY)
        self.input_btn.grid(row=2, column=1, padx=5, pady=5, sticky=EW)

        # Output folder field and button
        self.output_label = tb.Label(self, text="Output folder for .aivjson files:")
        self.output_label.grid(row=3, column=0, sticky=W, padx=10, pady=(10,0))
        self.output_entry = tb.Entry(self, textvariable=self.output_dir, width=60)
        self.output_entry.grid(row=4, column=0, padx=(10,0), pady=5, sticky=EW)
        self.output_btn = tb.Button(self, text="Browse...", command=self.select_output_dir, bootstyle=PRIMARY)
        self.output_btn.grid(row=4, column=1, padx=5, pady=5, sticky=EW)

        # Convert button
        self.convert_btn = tb.Button(self, text="Convert", command=self.start_conversion, bootstyle=SUCCESS)
        self.convert_btn.grid(row=5, column=0, columnspan=2, pady=10)

        # Log
        self.log = tb.ScrolledText(self, height=10, state='disabled')
        self.log.grid(row=6, column=0, columnspan=3, padx=10, pady=(0,10), sticky=NSEW)
        self.grid_rowconfigure(6, weight=1)

        # Code developed by Gynt (sourcehold) (clickable '(sourcehold)')
        dev_frame = tb.Frame(self)
        dev_frame.grid(row=7, column=0, columnspan=3, sticky=W, padx=10, pady=(0,2))
        dev_label = tb.Label(dev_frame, text="Code developed by Gynt ", anchor=W)
        dev_label.pack(side=LEFT)
        sourcehold_link = tb.Label(dev_frame, text="(sourcehold)", foreground="#2563eb", cursor="hand2", anchor=W, font=(None, 10, 'underline'))
        sourcehold_link.pack(side=LEFT)
        sourcehold_link.bind("<Button-1>", lambda e: webbrowser.open_new_tab("https://github.com/sourcehold"))

        # Code edited Wilps (clickable 'Wilps')
        code_frame = tb.Frame(self)
        code_frame.grid(row=8, column=0, columnspan=3, sticky=W, padx=10, pady=(0,10))
        code_label = tb.Label(code_frame, text="Code edited ", anchor=W)
        code_label.pack(side=LEFT)
        wilps_link = tb.Label(code_frame, text="Wilps", foreground="#2563eb", cursor="hand2", anchor=W, font=(None, 10, 'underline'))
        wilps_link.pack(side=LEFT)
        wilps_link.bind("<Button-1>", lambda e: webbrowser.open_new_tab("https://discordapp.com/users/306034441992667136"))

    def select_input(self):
        if self.batch_mode.get():
            path = filedialog.askdirectory(title="Select folder with .aiv files")
        else:
            path = filedialog.askopenfilename(title="Select .aiv file", filetypes=[("AIV files", "*.aiv"), ("All files", "*.*")])
        if path:
            self.input_path.set(path)

    def select_output_dir(self):
        path = filedialog.askdirectory(title="Select output folder for .aivjson files")
        if path:
            self.output_dir.set(path)

    def start_conversion(self):
        input_path = self.input_path.get().strip()
        output_dir = self.output_dir.get().strip()
        batch = self.batch_mode.get()
        if not input_path:
            messagebox.showerror("Error", "No file or folder selected for conversion!")
            return
        if not output_dir:
            messagebox.showerror("Error", "No output folder selected!")
            return
        threading.Thread(target=self.convert, args=(input_path, output_dir, batch), daemon=True).start()

    def log_message(self, msg):
        self.log.config(state='normal')
        self.log.insert('end', msg + '\n')
        self.log.see('end')
        self.log.config(state='disabled')

    def convert(self, input_path, output_dir, batch):
        self.log.config(state='normal')
        self.log.delete('1.0', 'end')
        self.log.config(state='disabled')
        input_path = pathlib.Path(input_path)
        output_dir = pathlib.Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        try:
            if batch:
                if not input_path.is_dir():
                    self.log_message("Selected path is not a folder!")
                    return
                aiv_files = list(input_path.glob('*.aiv'))
                if not aiv_files:
                    self.log_message(f"No .aiv files found in {input_path}!")
                    return
                for aiv_file in aiv_files:
                    self.log_message(f"Converting file: {aiv_file.name}")
                    out_file = output_dir / (aiv_file.stem + '.aivjson')
                    try:
                        json_data = to_json(path=str(aiv_file))
                        out_file.write_text(json_data)
                        self.log_message(f"Done: {out_file}")
                    except Exception as e:
                        self.log_message(f"Error for {aiv_file.name}: {e}")
                self.log_message("\nAll files processed!")
            else:
                if not input_path.is_file() or input_path.suffix.lower() != '.aiv':
                    self.log_message("Select a .aiv file!")
                    return
                self.log_message(f"Converting file: {input_path.name}")
                out_file = output_dir / (input_path.stem + '.aivjson')
                json_data = to_json(path=str(input_path))
                out_file.write_text(json_data)
                self.log_message(f"Done: {out_file}")
        except Exception as e:
            self.log_message(f"Error: {e}")

if __name__ == "__main__":
    app = AIV2JSONGui()
    app.mainloop()

# For PyInstaller: use --noconsole to avoid console window:
# pyinstaller --onefile --noconsole --name aiv2json_gui sourcehold/tool/convert/aiv/gui.py