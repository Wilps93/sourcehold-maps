import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import pathlib
import threading
import os
from sourcehold.tool.convert.aiv.exports import to_json

class AIV2JSONGui(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AIV to AIVJSON Converter")
        self.geometry("600x350")
        self.resizable(False, False)

        self.input_path = tk.StringVar()
        self.output_dir = tk.StringVar()

        tk.Label(self, text="Выберите .aiv файл или папку с .aiv файлами:").pack(anchor='w', padx=10, pady=(10,0))
        input_frame = tk.Frame(self)
        input_frame.pack(fill='x', padx=10)
        tk.Entry(input_frame, textvariable=self.input_path, width=60).pack(side='left', fill='x', expand=True)
        tk.Button(input_frame, text="Обзор...", command=self.select_input).pack(side='left', padx=5)

        tk.Label(self, text="Папка для вывода .aivjson файлов:").pack(anchor='w', padx=10, pady=(10,0))
        output_frame = tk.Frame(self)
        output_frame.pack(fill='x', padx=10)
        tk.Entry(output_frame, textvariable=self.output_dir, width=60).pack(side='left', fill='x', expand=True)
        tk.Button(output_frame, text="Обзор...", command=self.select_output_dir).pack(side='left', padx=5)

        tk.Button(self, text="Конвертировать", command=self.start_conversion).pack(pady=10)

        self.log = scrolledtext.ScrolledText(self, height=10, state='disabled')
        self.log.pack(fill='both', padx=10, pady=(0,10), expand=True)

    def select_input(self):
        path = filedialog.askopenfilename(title="Выберите .aiv файл или папку", filetypes=[("AIV files", "*.aiv"), ("All files", "*.*")])
        if not path:
            path = filedialog.askdirectory(title="Выберите папку с .aiv файлами")
        if path:
            self.input_path.set(path)

    def select_output_dir(self):
        path = filedialog.askdirectory(title="Выберите папку для вывода .aivjson файлов")
        if path:
            self.output_dir.set(path)

    def start_conversion(self):
        input_path = self.input_path.get().strip()
        output_dir = self.output_dir.get().strip()
        if not input_path:
            messagebox.showerror("Ошибка", "Не выбран файл или папка для конвертации!")
            return
        if not output_dir:
            messagebox.showerror("Ошибка", "Не выбрана папка для вывода!")
            return
        threading.Thread(target=self.convert, args=(input_path, output_dir), daemon=True).start()

    def log_message(self, msg):
        self.log.config(state='normal')
        self.log.insert('end', msg + '\n')
        self.log.see('end')
        self.log.config(state='disabled')

    def convert(self, input_path, output_dir):
        self.log.config(state='normal')
        self.log.delete('1.0', 'end')
        self.log.config(state='disabled')
        input_path = pathlib.Path(input_path)
        output_dir = pathlib.Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        try:
            if input_path.is_file() and input_path.suffix.lower() == '.aiv':
                self.log_message(f"Конвертация файла: {input_path.name}")
                out_file = output_dir / (input_path.stem + '.aivjson')
                json_data = to_json(path=str(input_path))
                out_file.write_text(json_data)
                self.log_message(f"Готово: {out_file}")
            elif input_path.is_dir():
                aiv_files = list(input_path.glob('*.aiv'))
                if not aiv_files:
                    self.log_message(f"В папке {input_path} нет .aiv файлов!")
                    return
                for aiv_file in aiv_files:
                    self.log_message(f"Конвертация файла: {aiv_file.name}")
                    out_file = output_dir / (aiv_file.stem + '.aivjson')
                    try:
                        json_data = to_json(path=str(aiv_file))
                        out_file.write_text(json_data)
                        self.log_message(f"Готово: {out_file}")
                    except Exception as e:
                        self.log_message(f"Ошибка для {aiv_file.name}: {e}")
                self.log_message("\nВсе файлы обработаны!")
            else:
                self.log_message("Выберите .aiv файл или папку с .aiv файлами!")
        except Exception as e:
            self.log_message(f"Ошибка: {e}")

if __name__ == "__main__":
    app = AIV2JSONGui()
    app.mainloop()