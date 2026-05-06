"""
Точка входа в приложение (ЛР5: Lazy Evaluation & Big Data)
"""

import json
import logging
import tracemalloc
from pathlib import Path
from typing import List, Dict

from app.core.core import BaseAppError
from app.io.readers import get_reader
from app.services.services import Aggregator
from app.services.pipeline import safe_transaction_parser

# Настройка логирования
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8",
)


def save_result(data: Dict) -> None:
    tmp = Path("result.json.tmp")
    final = Path("result.json")

    try:
        with tmp.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

        tmp.replace(final)

    except OSError as exc:
        logging.error(f"Ошибка записи файла: {exc}")


def print_report(
        total_files: int, success_files: int, errors: List[str]
        ) -> None:
    """
    Выводит итоговый отчёт в консоль
    """
    print(f"Обработано файлов: {total_files}")
    print(f"Успешно обработано: {success_files}")
    print(f"Всего ошибок записей: {len(errors)}")

    if errors:
        # Выводим только первые 5 ошибок
        print("Первые ошибки:")
        for err in errors[:5]:
            print(f"- {err}")
        if len(errors) > 5:
            print(f"... и еще {len(errors) - 5} ошибок (см. app.log)")


def process_file(
        file_path: Path, aggregator: Aggregator, errors: List[str]
        ) -> bool:
    """
    Обрабатывает один файл через ленивый конвейер.
    Возвращает True, если найдена хотя бы одна валидная запись.
    """
    reader = get_reader(file_path)
    if reader is None:
        msg = f"Неподдерживаемый файл: {file_path.name}"
        logging.warning(msg)
        errors.append(msg)
        return False

    try:
        # 1. Ленивое чтение (Генератор словарей)
        raw_data_gen = reader.read(file_path)

        # 2. Конвейер: Парсинг + Фильтрация ошибок (Генератор Транзакций)
        transaction_gen = safe_transaction_parser(
            raw_data_gen, errors, file_path.name
            )

        valid_found = False

        # 3. Агрегация "на лету"
        for transaction in transaction_gen:
            aggregator.add(transaction)
            valid_found = True

        return valid_found

    except BaseAppError as exc:
        # Ошибки чтения файла целиком (например, битый CSV хедер)
        logging.error(f"{file_path.name}: {exc}")
        errors.append(f"{file_path.name}: {exc}")
        return False


def main() -> None:
    """
    Основная логика работы приложения с замером памяти
    """
    # Запуск трассировщика памяти
    tracemalloc.start()

    data_dir = Path("data")

    if not data_dir.exists():
        logging.critical("Папка data не найдена")
        raise SystemExit(1)

    aggregator = Aggregator()
    errors: List[str] = []

    total_files = 0
    success_files = 0

    # Сортируем файлы для детерминированности
    files = sorted([f for f in data_dir.iterdir() if f.is_file()])

    for file_path in files:
        total_files += 1
        if process_file(file_path, aggregator, errors):
            success_files += 1

    save_result(aggregator.result())
    print_report(total_files, success_files, errors)

    # Замер пиковой памяти
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print("-" * 30)
    print(f"Текущее потребление памяти: {current / 1024 / 1024:.2f} MB")
    print(f"Пиковое потребление памяти: {peak / 1024 / 1024:.2f} MB")
    print("-" * 30)


if __name__ == "__main__":
    main()
