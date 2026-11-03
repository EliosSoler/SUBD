# Тесты СУБД.
# Проверяем создание, удаление, изменение структуры, вставку данных,
# выборку с фильтрацией и граничные случаи.


import unittest
import os
import shutil
from db import Database, TableAlreadyExists, TableNotFound, ColumnNotFound


class StartTest(unittest.TestCase):
    """
    Базовый класс для тестов. Готовит общее окружение.
    """

    @classmethod
    def setUpClass(cls):
        """
        Создает чистую тестовую базу и таблицу users перед всеми тестами.
        """
        if os.path.exists("test_database"):
            shutil.rmtree("test_database")

        cls.db = Database("test_database")
        cls.db.create_table("users", ["id", "name", "age"])

    @classmethod
    def tearDownClass(cls):
        """
        Удаляет тестовую папку после всех тестов.
        """
        if os.path.exists("test_database"):
            shutil.rmtree("test_database")


class TestCreate(StartTest):
    """
    Тесты метода create_table.
    """

    def test_create(self):
        """
        Создает новую таблицу tmp и проверяет её наличие в схеме.
        """
        self.db.create_table("tmp", ["id"])
        self.assertIn("tmp", self.db.schema)
        self.db.drop_table("tmp")

    def test_create_error(self):
        """
        Вызывает TableAlreadyExists при создании уже существующей таблицы.
        """
        with self.assertRaises(TableAlreadyExists):
            self.db.create_table("users", ["id", "name", "age"])


class TestDrop(StartTest):
    """
    Тесты метода drop_table.
    """

    def test_drop(self):
        """
        Удаляет таблицу tmp и проверяет, что её больше нет в схеме.
        """
        self.db.create_table("tmp", ["id"])
        self.db.drop_table("tmp")
        self.assertNotIn("tmp", self.db.schema)

    def test_drop_error(self):
        """
        Вызывает TableNotFound при удалении несуществующей таблицы.
        """
        with self.assertRaises(TableNotFound):
            self.db.drop_table("no_table")


class TestAlter(StartTest):
    """
    Тесты метода alter_table.
    """

    def test_alter(self):
        """
        Меняет колонки таблицы и сверяет их со схемой.
        """
        self.db.create_table("tmp", ["id"])
        self.db.alter_table("tmp", ["id", "name"])
        self.assertEqual(self.db.schema["tmp"], ["id", "name"])
        self.db.drop_table("tmp")

    def test_alter_error(self):
        """
        Вызывает TableNotFound при изменении несуществующей таблицы.
        """
        with self.assertRaises(TableNotFound):
            self.db.alter_table("no_table", ["id"])

    def test_alter_keeps_data(self):
        """
        Меняет структуру и проверяет, что старые данные не стерлись.
        """
        self.db.create_table("tmp2", ["id", "name"])
        self.db.insert("tmp2", ["1", "Тест"])

        self.db.alter_table("tmp2", ["id", "name", "age"])

        result = self.db.select("tmp2", "id,name")
        self.assertEqual(len(result.rows), 1)
        self.assertEqual(result.rows[0], ["1", "Тест"])
        self.db.drop_table("tmp2")


class TestInsert(StartTest):
    """
    Тесты метода insert.
    """

    def setUp(self):
        """
        Очищает таблицу users перед каждым тестом.
        """
        self.db._write_lines(self.db._table_file("users"), [])

    def test_insert(self):
        """
        Добавляет строку в users и проверяет, что она появилась в файле.
        """
        self.db.insert("users", ["1", "Вася", "20"])
        rows = self.db._read_lines(self.db._table_file("users"))
        self.assertEqual(len(rows), 1)

    def test_insert_wrong_count(self):
        """
        Вызывает ValueError, если передали меньше значений.
        """
        with self.assertRaises(ValueError):
            self.db.insert("users", ["1", "Вася"])

    def test_insert_too_many(self):
        """
        Вызывает ValueError, если передали больше значений.
        """
        with self.assertRaises(ValueError):
            self.db.insert("users", ["1", "Вася", "20", "Лишнее"])

    def test_insert_error(self):
        """
        Вызывает TableNotFound при вставке в несуществующую таблицу.
        """
        with self.assertRaises(TableNotFound):
            self.db.insert("no_table", ["1"])


class TestSelect(StartTest):
    """
    Тесты метода select.
    """

    def setUp(self):
        """
        Заполняет users тремя тестовыми строками перед каждым тестом.
        """
        self.db._write_lines(self.db._table_file("users"), [])
        self.db.insert("users", ["1", "Вася", "20"])
        self.db.insert("users", ["2", "Петя", "22"])
        self.db.insert("users", ["3", "Маша", "19"])

    def test_select_all(self):
        """
        Возвращает все поля и все строки таблицы.
        """
        result = self.db.select("users")
        self.assertEqual(result.fields, ["id", "name", "age"])
        self.assertEqual(len(result.rows), 3)

    def test_select_fields(self):
        """
        Возвращает только те поля, которые указали (name, age).
        """
        result = self.db.select("users", "name,age")
        self.assertEqual(result.fields, ["name", "age"])
        self.assertEqual(result.rows[0], ["Вася", "20"])

    def test_select_order(self):
        """
        Возвращает поля в другом порядке (сначала age, потом name).
        """
        result = self.db.select("users", "age,name")
        self.assertEqual(result.fields, ["age", "name"])
        self.assertEqual(result.rows[0], ["20", "Вася"])

    def test_select_duplicate(self):
        """
        Возвращает одно и то же поле несколько раз (name, name).
        """
        result = self.db.select("users", "name,name")
        self.assertEqual(result.fields, ["name", "name"])
        self.assertEqual(result.rows[0], ["Вася", "Вася"])

    def test_select_col_error(self):
        """
        Вызывает ColumnNotFound при запросе несуществующего поля.
        """
        with self.assertRaises(ColumnNotFound):
            self.db.select("users", "email")

    def test_select_table_error(self):
        """
        Вызывает TableNotFound при запросе из несуществующей таблицы.
        """
        with self.assertRaises(TableNotFound):
            self.db.select("no_table")


class TestFilter(StartTest):
    """
    Тесты фильтрации данных через Result.
    """

    def setUp(self):
        """
        Заполняет таблицу users данными для фильтрации.
        """
        self.db._write_lines(self.db._table_file("users"), [])
        self.db.insert("users", ["1", "Вася", "20"])
        self.db.insert("users", ["2", "Петя", "22"])
        self.db.insert("users", ["3", "Маша", "19"])

    def test_filter_age(self):
        """
        Фильтрует по возрасту (оставляет старше 20).
        """
        res = self.db.select("users", "name,age").filter(lambda r: int(r["age"]) > 20)
        self.assertEqual(len(res.rows), 1)
        self.assertEqual(res.rows[0], ["Петя", "22"])

    def test_filter_name(self):
        """
        Фильтрует по имени (оставляет только Машу).
        """
        res = self.db.select("users", "name,age").filter(lambda r: r["name"] == "Маша")
        self.assertEqual(len(res.rows), 1)
        self.assertEqual(res.rows[0], ["Маша", "19"])

    def test_filter_empty(self):
        """
        Фильтрует и возвращает пустой результат, если нет подходящих.
        """
        res = self.db.select("users", "name,age").filter(lambda r: int(r["age"]) > 100)
        self.assertEqual(len(res.rows), 0)

    def test_filter_all(self):
        """
        Фильтрует и оставляет все строки, так как условие верное для всех.
        """
        res = self.db.select("users", "name,age").filter(lambda r: int(r["age"]) > 0)
        self.assertEqual(len(res.rows), 3)


class TestEmpty(StartTest):
    """
    Граничные тесты (пустая таблица и таблица с одной строкой).
    """

    def setUp(self):
        """
        Создает пустую таблицу empty перед тестом.
        """
        if "empty" not in self.db.schema:
            self.db.create_table("empty", ["id"])
        self.db._write_lines(self.db._table_file("empty"), [])

    def test_empty_table(self):
        """
        Возвращает 0 строк при выборке из пустой таблицы.
        """
        res = self.db.select("empty")
        self.assertEqual(len(res.rows), 0)
        self.assertEqual(res.fields, ["id"])

    def test_one_row(self):
        """
        Возвращает ровно одну строку, если в таблице одна запись.
        """
        self.db.insert("empty", ["1"])
        res = self.db.select("empty")
        self.assertEqual(len(res.rows), 1)

    def test_filter_empty(self):
        """
        Возвращает пустой результат при фильтрации пустой таблицы.
        """
        res = self.db.select("empty").filter(lambda r: True)
        self.assertEqual(len(res.rows), 0)


if __name__ == "__main__":
    unittest.main()