from app.io.readers import CSVReader, get_reader


def test_csv_reader_success(tmp_path):
    """Проверка успешного чтения CSV через генератор"""
    file_path = tmp_path / "file.csv"
    file_path.write_text("id,amount,category,date\n1,100,food,2024-01-01")

    reader = CSVReader()
    # read теперь возвращает генератор, преобразуем в список для проверки
    data = list(reader.read(file_path))

    assert len(data) == 1
    assert data[0]["id"] == "1"
    assert data[0]["amount"] == "100"


def test_csv_reader_empty(tmp_path):
    """Проверка чтения пустого CSV (только заголовок)"""
    file_path = tmp_path / "empty.csv"
    file_path.write_text("id,amount,category,date\n")

    reader = CSVReader()
    data = list(reader.read(file_path))

    assert len(data) == 0


def test_get_reader_csv(tmp_path):
    """Проверка фабрики ридеров для CSV"""
    file = tmp_path / "test.csv"
    file.write_text("data")

    reader = get_reader(file)
    assert reader is not None
    assert isinstance(reader, CSVReader)


def test_get_reader_unknown_extension(tmp_path):
    """Проверка фабрики ридеров для неизвестного формата"""
    from app.io.readers import get_reader

    file = tmp_path / "file.txt"
    file.write_text("test")

    assert get_reader(file) is None


def test_get_reader_json_returns_none(tmp_path):
    """
    В рамках ЛР5 поддержка JSON отключена для фокуса на оптимизации CSV.
    get_reader должен возвращать None для json файлов.
    """
    file = tmp_path / "file.json"
    file.write_text('{"test": 1}')

    assert get_reader(file) is None
