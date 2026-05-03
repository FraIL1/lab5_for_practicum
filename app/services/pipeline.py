"""
Конвейер обработки данных (Pipeline)
Использует ленивые вычисления для экономии памяти.
"""

from typing import Generator, Dict, List

from app.core.core import Transaction, BaseAppError
from app.services.services import validate_record


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

            # Используем logging здесь для немедленной реакции.
            import logging

            logging.warning(error_msg)
