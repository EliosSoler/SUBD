# Движок СУБД.

import os


class DBError(Exception):
    """
    Базовое исключение СУБД. От него наследуются остальные.
    """
    pass


class TableAlreadyExists(DBError):
    """
    Таблица с таким именем уже есть.
    """
    pass


class TableNotFound(DBError):
    """
    Таблицы с таким именем нет.
    """
    pass


class ColumnNotFound(DBError):
    """
    Колонки с таким именем нет в таблице.
    """
    pass


class Record:
    """
    Запись позволяющая обращаться к полям через точку (r.age).
    """

    def __init__(self, data):
        for key in data:
            setattr(self, key, data[key])


class Asc:
    """
    Правило сортировки по возрастанию.
    """

    def __init__(self, field):
        self.field = field


class Desc(Asc):
    """
    Правило сортировки по убыванию.Наследник Asc.
    """

    def __init__(self, field):
        super().__init__(field)


class Result:
    """
    Класс результата выборки.
    Хранит выбранные поля и строки.
    Фильтрует строки через лямбда функцию.
    """

    def __init__(self, fields):
        """
        Создаёт пустой результат с указанными полями.
        """
        self.fields = fields
        self.rows = []

    def add(self, row):
        """Добавляет одну строку в результат."""
        self.rows.append(row)

    def to_dicts(self):
        """
        Собирает данные из строк в словари и упаковывает их в объекты Record.
        Для обращения к полям через (r.age)
        """
        dict_list = []
        for row in self.rows:
            record_dict = {}
            for i in range(len(self.fields)):
                record_dict[self.fields[i]] = row[i]
            dict_list.append(Record(record_dict))
        return dict_list

    def filter(self, func):
        """
        Фильтрует строки функцией.
        func принимает словарь (record) и возвращает True/False.
        Возвращает новый объект Result.
        """
        new_result = Result(self.fields)
        dict_rows = self.to_dicts()

        for i in range(len(self.rows)):
            if func(dict_rows[i]):
                new_result.add(self.rows[i])

        return new_result

    def order(self, *args):
        """
        Сортирует данные по правилам (Asc/Desc).
        """
        if not args:
            return self

        smart_rows = self.to_dicts()
        paired = list(zip(smart_rows, self.rows))

        def sort_recursive(items, rules):
            if not rules:
                return items

            last_rule = rules[-1]
            remaining_rules = rules[:-1]

            is_reverse = isinstance(last_rule, Desc)

            items.sort(key=lambda x: getattr(x[0], last_rule.field), reverse=is_reverse)

            return sort_recursive(items, remaining_rules)

        sorted_pairs = sort_recursive(paired, list(args))

        new_result = Result(self.fields)
        for smart_rec, original_row in sorted_pairs:
            new_result.add(original_row)

        return new_result


class Database:
    """
    Класс базы данных.
    При создании объекта схема читается один раз и хранится в памяти.
    Все операции работают с этим объектом, а не с файлами напрямую.
    """

    def __init__(self, folder="database"):
        """
        Создаёт объект базы. Создаёт папку, если её нет, и загружает схему.
        """
        self.folder = folder
        self.schema_file = folder + "/schema.txt"

        if not os.path.exists(self.folder):
            os.makedirs(self.folder)

        self.schema = self._load_schema()

    def _table_file(self, table_name):
        """
        Возвращает путь к файлу данных таблицы.
        """
        return self.folder + "/" + table_name + ".txt"

    def _read_lines(self, filename):
        """
        Читает файл и возвращает список непустых строк.
        """
        if not os.path.exists(filename):
            return []

        f = open(filename, "r", encoding="utf-8")
        content = f.read()
        f.close()

        lines = []
        for line in content.split("\n"):
            if line != "":
                lines.append(line)
        return lines

    def _write_lines(self, filename, lines):
        """
        Пишет список строк в файл.
        """
        f = open(filename, "w", encoding="utf-8")
        f.write("\n".join(lines))
        f.close()

    def _load_schema(self):
        """
        Читает schema.txt и возвращает словарь {имя: [колонки]}.
        """
        schema = {}
        for line in self._read_lines(self.schema_file):
            parts = line.split("|")
            if len(parts) == 2:
                schema[parts[0]] = parts[1].split(",")
        return schema

    def _save_schema(self):
        """
        Сохраняет схему в schema.txt.
        """
        lines = []
        for table_name in self.schema:
            line = table_name + "|" + ",".join(self.schema[table_name])
            lines.append(line)
        self._write_lines(self.schema_file, lines)

    def create_table(self, table_name, columns):
        """
        Создаёт новую таблицу с указанными колонками.
        Кидает TableAlreadyExists, если таблица уже есть.
        """
        if table_name in self.schema:
            raise TableAlreadyExists("Таблица '" + table_name + "' уже существует")

        self.schema[table_name] = columns
        self._save_schema()
        self._write_lines(self._table_file(table_name), [])

    def drop_table(self, table_name):
        """
        Удаляет таблицу из схемы и физически удаляет её файл данных.
        Кидает TableNotFound, если таблицы нет.
        """
        if table_name not in self.schema:
            raise TableNotFound("Таблицы '" + table_name + "' не существует")

        del self.schema[table_name]
        self._save_schema()

        filename = self._table_file(table_name)
        if os.path.exists(filename):
            os.remove(filename)

    def alter_table(self, table_name, new_columns):
        """
        Меняет список колонок таблицы. Данные не трогает.
        Кидает TableNotFound, если таблицы нет.
        """
        if table_name not in self.schema:
            raise TableNotFound("Таблицы '" + table_name + "' не существует")

        self.schema[table_name] = new_columns
        self._save_schema()

    def insert(self, table_name, values):
        """
        Добавляет строку в таблицу.
        Кидает TableNotFound, если таблицы нет, и ValueError,
        если число значений не совпадает с числом колонок.
        """
        if table_name not in self.schema:
            raise TableNotFound("Таблицы '" + table_name + "' не существует")

        columns = self.schema[table_name]

        if len(values) != len(columns):
            raise ValueError(
                "Ожидалось " + str(len(columns)) +
                " значений, получено " + str(len(values))
            )

        rows = self._read_lines(self._table_file(table_name))
        rows.append("|".join(values))
        self._write_lines(self._table_file(table_name), rows)

    def select(self, table_name, fields="*"):
        """
        Возвращает объект Result с выбранными полями.
        Второй параметр список полей через запятую в любом порядке.
        Можно дублировать поля. По умолчанию "*" — все поля.
        Кидает TableNotFound, если таблицы нет,
        и ColumnNotFound, если запрошено несуществующее поле.
        """
        if table_name not in self.schema:
            raise TableNotFound("Таблицы '" + table_name + "' не существует")

        columns = self.schema[table_name]

        if fields == "*":
            selected = columns
        else:
            selected = fields.split(",")
            for field in selected:
                if field not in columns:
                    raise ColumnNotFound(
                        "Колонки '" + field + "' нет в таблице '" + table_name + "'"
                    )

        indexes = []
        for field in selected:
            indexes.append(columns.index(field))

        result = Result(selected)

        rows = self._read_lines(self._table_file(table_name))
        for row in rows:
            values = row.split("|")
            new_row = []
            for i in indexes:
                new_row.append(values[i])
            result.add(new_row)

        return result