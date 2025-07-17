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
        self.geometry("600x400")
        self.resizable(False, False)

        self.input_file = tk.StringVar()
        self.input_dir = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.batch_mode = tk.BooleanVar(value=False)

        # Фрейм выбора файла
        tk.Label(self, text="Выберите .aiv файл:").pack(anchor='w', padx=10, pady=(10,0))
        file_frame = tk.Frame(self)
        file_frame.pack(fill='x', padx=10)
        self.file_entry = tk.Entry(file_frame, textvariable=self.input_file, width=60)
        self.file_entry.pack(side='left', fill='x', expand=True)
        self.file_btn = tk.Button(file_frame, text="Обзор...", command=self.select_input_file)
        self.file_btn.pack(side='left', padx=5)

        # Чекбокс пакетного режима
        batch_frame = tk.Frame(self)
        batch_frame.pack(fill='x', padx=10, pady=(5,0))
        self.batch_check = tk.Checkbutton(batch_frame, text="Пакетная обработка папки", variable=self.batch_mode, command=self.toggle_batch_mode)
        self.batch_check.pack(side='left')

        # Фрейм выбора папки
        tk.Label(self, text="Папка с .aiv файлами:").pack(anchor='w', padx=10, pady=(10,0))
        dir_frame = tk.Frame(self)
        dir_frame.pack(fill='x', padx=10)
        self.dir_entry = tk.Entry(dir_frame, textvariable=self.input_dir, width=60, state='disabled')
        self.dir_entry.pack(side='left', fill='x', expand=True)
        self.dir_btn = tk.Button(dir_frame, text="Обзор...", command=self.select_input_dir, state='disabled')
        self.dir_btn.pack(side='left', padx=5)

        # Фрейм выбора папки вывода
        tk.Label(self, text="Папка для вывода .aivjson файлов:").pack(anchor='w', padx=10, pady=(10,0))
        output_frame = tk.Frame(self)
        output_frame.pack(fill='x', padx=10)
        tk.Entry(output_frame, textvariable=self.output_dir, width=60).pack(side='left', fill='x', expand=True)
        tk.Button(output_frame, text="Обзор...", command=self.select_output_dir).pack(side='left', padx=5)

        tk.Button(self, text="Конвертировать", command=self.start_conversion).pack(pady=10)

        self.log = scrolledtext.ScrolledText(self, height=10, state='disabled')
        self.log.pack(fill='both', padx=10, pady=(0,10), expand=True)

    def toggle_batch_mode(self):
        if self.batch_mode.get():
            self.dir_entry.config(state='normal')
            self.dir_btn.config(state='normal')
            self.file_entry.config(state='disabled')
            self.file_btn.config(state='disabled')
        else:
            self.dir_entry.config(state='disabled')
            self.dir_btn.config(state='disabled')
            self.file_entry.config(state='normal')
            self.file_btn.config(state='normal')

    def select_input_file(self):
        path = filedialog.askopenfilename(title="Выберите .aiv файл", filetypes=[("AIV files", "*.aiv"), ("All files", "*.*")])
        if path:
            self.input_file.set(path)

    def select_input_dir(self):
        path = filedialog.askdirectory(title="Выберите папку с .aiv файлами")
        if path:
            self.input_dir.set(path)

    def select_output_dir(self):
        path = filedialog.askdirectory(title="Выберите папку для вывода .aivjson файлов")
        if path:
            self.output_dir.set(path)

    def start_conversion(self):
        if self.batch_mode.get():
            input_path = self.input_dir.get().strip()
        else:
            input_path = self.input_file.get().strip()
        output_dir = self.output_dir.get().strip()
        if not input_path:
            messagebox.showerror("Ошибка", "Не выбран файл или папка для конвертации!")
            return
        if not output_dir:
            messagebox.showerror("Ошибка", "Не выбрана папка для вывода!")
            return
        threading.Thread(target=self.convert, args=(input_path, output_dir, self.batch_mode.get()), daemon=True).start()

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
                    self.log_message("Выбранный путь не является папкой!")
                    return
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
                if not input_path.is_file() or input_path.suffix.lower() != '.aiv':
                    self.log_message("Выберите .aiv файл!")
                    return
                self.log_message(f"Конвертация файла: {input_path.name}")
                out_file = output_dir / (input_path.stem + '.aivjson')
                json_data = to_json(path=str(input_path))
                out_file.write_text(json_data)
                self.log_message(f"Готово: {out_file}")
        except Exception as e:
            self.log_message(f"Ошибка: {e}")

if __name__ == "__main__":
    app = AIV2JSONGui()
    app.mainloop()