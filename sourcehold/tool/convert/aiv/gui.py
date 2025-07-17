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
        self.batch_check = tb.Checkbutton(self, text="Пакетная обработка папки", variable=self.batch_mode, bootstyle="round-toggle")
        self.batch_check.grid(row=0, column=0, columnspan=3, sticky=W, padx=10, pady=(10,0))

        # Поле и кнопка выбора файла/папки
        self.input_label = tb.Label(self, text="Выберите .aiv файл или папку с .aiv файлами:")
        self.input_label.grid(row=1, column=0, sticky=W, padx=10, pady=(10,0))
        self.input_entry = tb.Entry(self, textvariable=self.input_path, width=60)
        self.input_entry.grid(row=2, column=0, padx=(10,0), pady=5, sticky=EW)
        self.input_btn = tb.Button(self, text="Обзор...", command=self.select_input, bootstyle=PRIMARY)
        self.input_btn.grid(row=2, column=1, padx=5, pady=5, sticky=EW)
        self.grid_columnconfigure(0, weight=1)

        # Поле и кнопка выбора папки вывода
        self.output_label = tb.Label(self, text="Папка для вывода .aivjson файлов:")
        self.output_label.grid(row=3, column=0, sticky=W, padx=10, pady=(10,0))
        self.output_entry = tb.Entry(self, textvariable=self.output_dir, width=60)
        self.output_entry.grid(row=4, column=0, padx=(10,0), pady=5, sticky=EW)
        self.output_btn = tb.Button(self, text="Обзор...", command=self.select_output_dir, bootstyle=PRIMARY)
        self.output_btn.grid(row=4, column=1, padx=5, pady=5, sticky=EW)

        # Кнопка конвертации
        self.convert_btn = tb.Button(self, text="Конвертировать", command=self.start_conversion, bootstyle=SUCCESS)
        self.convert_btn.grid(row=5, column=0, columnspan=2, pady=10)

        # Лог
        self.log = tb.ScrolledText(self, height=10, state='disabled')
        self.log.grid(row=6, column=0, columnspan=3, padx=10, pady=(0,10), sticky=NSEW)
        self.grid_rowconfigure(6, weight=1)

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

# Для PyInstaller: используйте опцию --noconsole чтобы не было окна консоли:
# pyinstaller --onefile --noconsole --name aiv2json_gui sourcehold/tool/convert/aiv/gui.py