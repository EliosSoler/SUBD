# Движок  СУБД.

class DBError(Exception):
    """
    Базовое исключение СУБД. От него наследуются все остальные
    исключения проекта, что позволяет ловить их одной строкой.
    """
    pass


class TableAlreadyExists(DBError):
    """
    Кидается функцией create_table, если таблица с таким именем
    уже существует в базе.
    """
    pass


class TableNotFound(DBError):
    """
    Кидается функциями drop_table, alter_table, insert, select,
    если указана таблица, которой нет в базе.
    """
    pass


DB_FOLDER = "database"
SCHEMA_FILE = "database/schema.txt"


def read_file(filename):
    """
    Читает файл целиком и возвращает его содержимое в виде строки.
    Если файла нет — возвращает пустую строку, а не кидает ошибку,
    потому что при первом запуске schema.txt может не быть.
    """
    try:
        f = open(filename, "r", encoding="utf-8")
    except FileNotFoundError:
        return ""

    content = f.read()
    f.close()
    return content


def write_file(filename, content):
    """
    Записывает строку в файл, полностью перезаписывая его содержимое.
    Если файла не было — создаёт новый.
    """
    f = open(filename, "w", encoding="utf-8")
    f.write(content)
    f.close()


def read_lines(filename):
    """
    Читает файл и возвращает список непустых строк.
    Пустые строки пропускаются, так как в файлах они служат
    только разделителями и смысла не несут.
    """
    content = read_file(filename)

    lines = []
    for line in content.split("\n"):
        if line != "":
            lines.append(line)
    return lines


def write_lines(filename, lines):
    """
    Записывает список строк в файл, соединяя их переводом строки.
    Каждая строка списка становится отдельной строкой в файле.
    """
    write_file(filename, "\n".join(lines))


def table_file(table_name):
    """
    Возвращает путь к файлу с данными указанной таблицы.
    Например, для таблицы users вернёт "database/users.txt".
    """
    return DB_FOLDER + "/" + table_name + ".txt"


def load_schema():
    """
    Читает файл schema.txt и возвращает словарь вида
    {имя_таблицы: [список колонок]}. Каждая строка файла имеет
    формат "имя_таблицы|колонка1,колонка2,колонка3".
    """
    schema = {}
    for line in read_lines(SCHEMA_FILE):
        parts = line.split("|")
        if len(parts) == 2:
            schema[parts[0]] = parts[1].split(",")
    return schema


def save_schema(schema):
    """
    Сохраняет словарь схемы в файл schema.txt, перезаписывая его.
    Каждая таблица записывается одной строкой в формате
    "имя_таблицы|колонка1,колонка2".
    """
    lines = []
    for table_name in schema:
        line = table_name + "|" + ",".join(schema[table_name])
        lines.append(line)
    write_lines(SCHEMA_FILE, lines)


def create_table(table_name, columns):
    """
    Создаёт новую таблицу с указанными колонками.
    Если таблица с таким именем уже существует — кидает
    TableAlreadyExists. При успехе создаёт пустой файл данных.
    """
    schema = load_schema()

    if table_name in schema:
        raise TableAlreadyExists("Таблица '" + table_name + "' уже существует")

    schema[table_name] = columns
    save_schema(schema)
    write_lines(table_file(table_name), [])


def drop_table(table_name):
    """
    Удаляет таблицу из схемы базы и очищает её файл данных.
    Если таблицы с таким именем нет — кидает TableNotFound.
    Без модуля os физически удалить файл нельзя, поэтому он очищается.
    """
    schema = load_schema()

    if table_name not in schema:
        raise TableNotFound("Таблицы '" + table_name + "' не существует")

    del schema[table_name]
    save_schema(schema)
    write_lines(table_file(table_name), [])


def alter_table(table_name, new_columns):
    """
    Меняет список колонок у существующей таблицы в схеме базы.
    Если таблицы нет — кидает TableNotFound. Данные в файле
    таблицы при этом не изменяются, меняется только схема.
    """
    schema = load_schema()

    if table_name not in schema:
        raise TableNotFound("Таблицы '" + table_name + "' не существует")

    schema[table_name] = new_columns
    save_schema(schema)


def insert(table_name, values):
    """
    Добавляет новую строку в указанную таблицу.
    Если таблицы нет — кидает TableNotFound. Если число значений
    не совпадает с числом колонок — кидает ValueError.
    """
    schema = load_schema()

    if table_name not in schema:
        raise TableNotFound("Таблицы '" + table_name + "' не существует")

    columns = schema[table_name]

    if len(values) != len(columns):
        raise ValueError(
            "Ожидалось " + str(len(columns)) +
            " значений, получено " + str(len(values))
        )

    rows = read_lines(table_file(table_name))
    rows.append("|".join(values))
    write_lines(table_file(table_name), rows)


def select(table_name):
    """
    озвращает все строки таблицы в виде матрицы — списка списков.
    Если таблицы нет — кидает TableNotFound. Пользователь сам решает,
    как показать эти данные: текстом, таблицей, отчётом.
    """
    schema = load_schema()

    if table_name not in schema:
        raise TableNotFound("Таблицы '" + table_name + "' не существует")

    rows = read_lines(table_file(table_name))

    matrix = []
    for row in rows:
        matrix.append(row.split("|"))
    return matrix