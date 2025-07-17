import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
import pathlib
import threading
import os
from sourcehold.tool.convert.aiv.exports import to_json

class AIV2JSONGui(tb.Window):
    def __init__(self):
        super().__init__(themename="superhero")  # Современная тема Windows 10/11
        self.title("AIV to AIVJSON Converter")
        self.geometry("600x400")
        self.resizable(False, False)

        self.input_path = tb.StringVar()
        self.output_dir = tb.StringVar()
        self.batch_mode = tb.BooleanVar(value=False)

        # Чекбокс пакетного режима
        batch_frame = tb.Frame(self)
        batch_frame.pack(fill=X, padx=10, pady=(10,0))
        self.batch_check = tb.Checkbutton(batch_frame, text="Пакетная обработка папки", variable=self.batch_mode, bootstyle="round-toggle")
        self.batch_check.pack(side=LEFT)

        # Фрейм выбора файла/папки
        tb.Label(self, text="Выберите .aiv файл или папку с .aiv файлами:").pack(anchor='w', padx=10, pady=(10,0))
        input_frame = tb.Frame(self)
        input_frame.pack(fill=X, padx=10)
        self.input_entry = tb.Entry(input_frame, textvariable=self.input_path, width=60)
        self.input_entry.pack(side=LEFT, fill=X, expand=True)
        self.input_btn = tb.Button(input_frame, text="Обзор...", command=self.select_input, bootstyle=PRIMARY)
        self.input_btn.pack(side=LEFT, padx=5)

        # Фрейм выбора папки вывода
        tb.Label(self, text="Папка для вывода .aivjson файлов:").pack(anchor='w', padx=10, pady=(10,0))
        output_frame = tb.Frame(self)
        output_frame.pack(fill=X, padx=10)
        tb.Entry(output_frame, textvariable=self.output_dir, width=60).pack(side=LEFT, fill=X, expand=True)
        tb.Button(output_frame, text="Обзор...", command=self.select_output_dir, bootstyle=PRIMARY).pack(side=LEFT, padx=5)

        tb.Button(self, text="Конвертировать", command=self.start_conversion, bootstyle=SUCCESS).pack(pady=10)

        self.log = tb.ScrolledText(self, height=10, state='disabled', bootstyle=INFO)
        self.log.pack(fill='both', padx=10, pady=(0,10), expand=True)

    def select_input(self):
        if self.batch_mode.get():
            path = filedialog.askdirectory(title="Выберите папку с .aiv файлами")
        else:
            path = filedialog.askopenfilename(title="Выберите .aiv файл", filetypes=[("AIV files", "*.aiv"), ("All files", "*.*")])
        if path:
            self.input_path.set(path)

    def select_output_dir(self):
        path = filedialog.askdirectory(title="Выберите папку для вывода .aivjson файлов")
        if path:
            self.output_dir.set(path)

    def start_conversion(self):
        input_path = self.input_path.get().strip()
        output_dir = self.output_dir.get().strip()
        batch = self.batch_mode.get()
        if not input_path:
            messagebox.showerror("Ошибка", "Не выбран файл или папка для конвертации!")
            return
        if not output_dir:
            messagebox.showerror("Ошибка", "Не выбрана папка для вывода!")
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