"""
Конвейер обработки данных (Pipeline)
Использует ленивые вычисления для экономии памяти.
"""

from typing import Generator, Dict, List

from app.core.core import Transaction, BaseAppError
from app.services.services import validate_record


def parse_transactions(
    raw_data: Generator[Dict[str, str], None, None],
) -> Generator[Transaction, None, None]:
    """
    Принимает генератор сырых словарей и преобразует их в объекты Transaction.

    Args:
        raw_data: Генератор словарей из CSVReader.

    Yields:
        Transaction: Валидный объект транзакции.

    Note:
        Если валидация не проходит, исключение пробрасывается выше.
        Обработка исключений должна происходить на уровне выше (в main),
        чтобы можно было залогировать ошибку и продолжить итерацию.
    """
    for record in raw_data:
        # validate_record может выбросить исключение
        transaction = validate_record(record)
        yield transaction


def filter_and_log_errors(
    transactions: Generator[Transaction, None, None], errors: List[str], filename: str
) -> Generator[Transaction, None, None]:
    """
    Пропускает валидные транзакции дальше, а ошибки сохраняет в список.

    Args:
        transactions: Генератор транзакций (может содержать ошибки при получении).
        errors: Список для накопления сообщений об ошибках.
        filename: Имя файла для логирования источника ошибки.

    Yields:
        Transaction: Только успешно созданные транзакции.
    """
    # Так как исключения в генераторах прерывают итерацию,
    # нам нужно аккуратно обрабатывать их внутри цикла,
    # который ПОТРЕБЛЯЕТ этот генератор.
    # Однако, архитектура "генератор внутри генератора" с обработкой ошибок
    # лучше всего реализуется так:

    # В данном случае, мы не можем "поймать" ошибку внутри parse_transactions,
    # не прервав его. Поэтому паттерн немного меняется:
    # Мы будем итерировать источник ВНУТРИ этого генератора.

    # Но так как мы передаем уже готовый генератор, давайте сделаем проще:
    # Этот генератор просто передает данные, а обработку ошибок вынесем в main?
    # Нет, по ТЗ нужна фильтрация.

    # Правильный подход для конвейера с ошибками:
    # Источник данных должен быть "безопасным".
    # Давайте перепишем логику так, чтобы этот генератор сам дергал исходный итератор
    # и ловил ошибки.
    pass


# ПЕРЕПИСЫВАЕМ ПРАВИЛЬНЕЕ:
# Объединим парсинг и безопасную фильтрацию в один шаг для простоты управления ошибками,
# либо сделаем обертку.


def safe_transaction_parser(
    raw_data: Generator[Dict[str, str], None, None], errors: List[str], filename: str
) -> Generator[Transaction, None, None]:
    """
    Парсит сырые данные в Транзакции, отлавливает ошибки валидации.

    Yields:
        Transaction: Только валидные транзакции.
    """
    for record in raw_data:
        try:
            transaction = validate_record(record)
            yield transaction
        except BaseAppError as exc:
            error_msg = f"{filename}: {exc}"
            errors.append(error_msg)
            # Логируем сразу здесь или в main?
            # В main у нас есть logging, но сюда передается только список errors.
            # Чтобы соблюсти разделенность, лучше логировать в main,
            # но тогда нам нужно вернуть и ошибку.
            # Для упрощения ЛР5: добавляем в список ошибок, а логирование делаем в main
            # при финальном выводе, ИЛИ используем logging прямо здесь.
            # Используем logging здесь для немедленной реакции.
            import logging

            logging.warning(error_msg)
