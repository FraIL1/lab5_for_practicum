"""
Модуль ленивого чтения файлов (CSV)
"""

import csv
from pathlib import Path
from typing import Generator, Dict, Optional

from app.core.core import DataFormatError


class CSVReader:
    """
    Класс для ленивого чтения CSV-файлов.
    Реализует итератор, выдающий данные по одной строке.
    """

    def read(self, file_path: Path) -> Generator[Dict[str, str], None, None]:
        """
        Генератор, считывающий CSV-файл построчно.

        Yields:
            Dict[str, str]: Словарь, представляющий одну строку CSV.
        """
        try:
            with file_path.open("r", encoding="utf-8") as file:
                # csv.reader тоже работает построчно, что экономит память
                reader = csv.DictReader(file)
                for row in reader:
                    yield row
        except Exception as exc:
            # Важно: в генераторах исключения при итерации могут быть сложными,
            # но здесь мы оборачиваем открытие файла.
            # Если ошибка случится внутри цикла, \
            # она всплывет к вызывающему коду.
            raise DataFormatError(f"Ошибка чтения CSV: {file_path.name}") from exc


def get_reader(file_path: Path) -> Optional[CSVReader]:
    """
    Возвращает CSV ридер, если расширение подходит.
    В рамках ЛР5 фокусируемся только на CSV для оптимизации памяти.
    """
    if file_path.suffix == ".csv":
        return CSVReader()
    return None
