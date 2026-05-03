"""
Скрипт для генерации большого CSV-файла (~1 GB) для тестирования памяти.
"""

import csv
import random
import string
from pathlib import Path

OUTPUT_FILE = Path("data/big_test.csv")
TARGET_SIZE_BYTES = 1_000_000_000  # 1 GB

CATEGORIES = ["food", "transport", "entertainment", "health", "salary", "utilities"]
DATE_START = "2020-01-01"
DATE_END = "2026-01-01"


def generate_random_id():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=10))


def generate_random_amount():
    return round(random.uniform(1.0, 5000.0), 2)


def generate_random_date():
    # Упрощенная генерация даты
    year = random.randint(2020, 2025)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return f"{year}-{month:02d}-{day:02d}"


def main():
    print(f"Начинаю генерацию файла {OUTPUT_FILE}...")
    print(f"Целевой размер: ~{TARGET_SIZE_BYTES / (1024**3):.2f} GB")

    # Убедимся, что папка data существует
    OUTPUT_FILE.parent.mkdir(exist_ok=True)

    count = 0
    # Открываем файл для записи
    with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        # Пишем заголовок
        writer.writerow(["id", "amount", "category", "date"])

        # Пишем строки, пока не достигнем размера
        # Примерный размер одной строки ~60-70 байт.
        # 1 ГБ / 70 байт ≈ 14-15 миллионов строк.

        while OUTPUT_FILE.stat().st_size < TARGET_SIZE_BYTES:
            row = [
                generate_random_id(),
                generate_random_amount(),
                random.choice(CATEGORIES),
                generate_random_date(),
            ]
            writer.writerow(row)
            count += 1

            if count % 1_000_000 == 0:
                size_mb = OUTPUT_FILE.stat().st_size / (1024 * 1024)
                print(f"  Сгенерировано строк: {count:,}. Размер: {size_mb:.2f} MB")

    final_size_gb = OUTPUT_FILE.stat().st_size / (1024**3)
    print(f"Готово! Всего строк: {count:,}")
    print(f"Итоговый размер файла: {final_size_gb:.2f} GB")


if __name__ == "__main__":
    main()
