import os
import pathlib
import unittest
import logging
from sourcehold.aivs.AIV import AIV
from sourcehold.tool.convert.aiv.exports import to_json

# Настройка логирования для отладки
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Используем переменную окружения для BASEPATH
BASEPATH = pathlib.Path(os.getenv('BASEPATH', 'resources/aiv'))
OUTPUT_DIR = pathlib.Path("output")

class TestAIVConversion(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.override = not BASEPATH.exists()
        OUTPUT_DIR.mkdir(exist_ok=True)
        logger.debug(f"Используется BASEPATH: {BASEPATH}")

    def test_rat(self):
        if self.override:
            self.skipTest(f"Директория {BASEPATH} не существует, пропуск test_rat")
        
        files = list(BASEPATH.glob("rat*.aiv"))
        logger.debug(f"Найдено {len(files)} файлов rat*.aiv в {BASEPATH}")
        self.assertGreater(len(files), 0, f"Файлы rat*.aiv не найдены в {BASEPATH}")
        for path in files:
            logger.debug(f"Обработка файла: {path}")
            aiv = AIV().from_file(str(path))
            json_data = to_json(aiv, include_extra=True)
            self.assertIsInstance(json_data, str, f"Ошибка преобразования JSON для {path}")

    def test_abbot(self):
        if self.override:
            self.skipTest(f"Директория {BASEPATH} не существует, пропуск test_abbot")
        
        files = list(BASEPATH.glob("Abbot*.aiv"))
        logger.debug(f"Найдено {len(files)} файлов Abbot*.aiv в {BASEPATH}")
        self.assertGreater(len(files), 0, f"Файлы Abbot*.aiv не найдены в {BASEPATH}")
        for path in files:
            logger.debug(f"Обработка файла: {path}")
            aiv = AIV().from_file(str(path))
            json_data = to_json(aiv, include_extra=True)
            self.assertIsInstance(json_data, str, f"Ошибка преобразования JSON для {path}")

    def test_all(self):
        if self.override:
            self.skipTest(f"Директория {BASEPATH} не существует, пропуск test_all")
        
        for path in BASEPATH.glob("*.aiv"):
            logger.debug(f"Обработка файла: {path}")
            aiv = AIV().from_file(str(path))
            json_data = to_json(aiv, include_extra=True)
            output_path = OUTPUT_DIR / f"{path.name}.aivjson"
            output_path.write_text(json_data)
            self.assertTrue(output_path.exists(), f"Не удалось записать {output_path}")

if __name__ == '__main__':
    unittest.main()
