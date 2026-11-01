# Тесты СУБД через встроенный модуль unittest.
# Класс на каждую функцию. Метод на каждый сценарий.
# setUp создаёт чистую среду. tearDown убирает за собой.

import unittest
from db import Database, TableAlreadyExists, TableNotFound, ColumnNotFound


class BaseTest(unittest.TestCase):
    """
    Базовый класс: общая подготовка для всех тестов.
    """

    def setUp(self):
        """
        Перед каждым тестом — создать объект базы.
        """
        self.db = Database("database")

    def tearDown(self):
        """
        После каждого теста — удалить таблицу test, если есть.
        """
        try:
            self.db.drop_table("test")
        except TableNotFound:
            pass


class TestCreateTable(BaseTest):
    """
    Тесты функции create_table.
    """

    def test_create_ok(self):
        """
        Успешное создание таблицы.
        """
        self.db.create_table("test", ["id", "name"])

    def test_create_exists(self):
        """
        Повторное создание — должно кинуть TableAlreadyExists.
        """
        self.db.create_table("test", ["id", "name"])
        with self.assertRaises(TableAlreadyExists):
            self.db.create_table("test", ["id", "name"])


class TestDropTable(BaseTest):
    """
    Тесты функции drop_table.
    """

    def test_drop_ok(self):
        """
        Успешное удаление таблицы.
        """
        self.db.create_table("test", ["id"])
        self.db.drop_table("test")

    def test_drop_not_found(self):
        """
        Удаление несуществующей таблицы — TableNotFound.
        """
        with self.assertRaises(TableNotFound):
            self.db.drop_table("test")


class TestAlterTable(BaseTest):
    """
    Тесты функции alter_table.
    """

    def test_alter_ok(self):
        """
        Успешное изменение структуры.
        """
        self.db.create_table("test", ["id"])
        self.db.alter_table("test", ["id", "name", "age"])

    def test_alter_not_found(self):
        """
        Изменение несуществующей — TableNotFound.
        """
        with self.assertRaises(TableNotFound):
            self.db.alter_table("test", ["id"])


class TestInsert(BaseTest):
    """
    Тесты функции insert.
    """

    def test_insert_ok(self):
        """
        Успешное добавление строки.
        """
        self.db.create_table("test", ["id", "name"])
        self.db.insert("test", ["1", "Вася"])

    def test_insert_wrong_count(self):
        """
        Неверное число значений — ValueError.
        """
        self.db.create_table("test", ["id", "name"])
        with self.assertRaises(ValueError):
            self.db.insert("test", ["1"])

    def test_insert_not_found(self):
        """
        Вставка в несуществующую таблицу — TableNotFound.
        """
        with self.assertRaises(TableNotFound):
            self.db.insert("test", ["1", "Вася"])


class TestSelect(BaseTest):
    """
    Тесты функции select.
    """

    def setUp(self):
        """
        Перед каждым тестом — создать таблицу test и заполнить.
        """
        super().setUp()
        self.db.create_table("test", ["id", "name", "age"])
        self.db.insert("test", ["1", "Вася", "20"])
        self.db.insert("test", ["2", "Петя", "22"])

    def test_select_all(self):
        """
        select без параметра — все поля.
        """
        result = self.db.select("test")
        expected = [
            ["id", "name", "age"],
            ["1", "Вася", "20"],
            ["2", "Петя", "22"],
        ]
        self.assertEqual(result, expected)

    def test_select_fields(self):
        """
        select с полями — только name, age.
        """
        result = self.db.select("test", "name,age")
        expected = [
            ["name", "age"],
            ["Вася", "20"],
            ["Петя", "22"],
        ]
        self.assertEqual(result, expected)

    def test_select_fields_order(self):
        """
        Другой порядок — age, name.
        """
        result = self.db.select("test", "age,name")
        expected = [
            ["age", "name"],
            ["20", "Вася"],
            ["22", "Петя"],
        ]
        self.assertEqual(result, expected)

    def test_select_fields_duplicate(self):
        """
        Дублирование поля — name, name.
        """
        result = self.db.select("test", "name,name")
        expected = [
            ["name", "name"],
            ["Вася", "Вася"],
            ["Петя", "Петя"],
        ]
        self.assertEqual(result, expected)

    def test_select_column_not_found(self):
        """
        Несуществующее поле — ColumnNotFound.
        """
        with self.assertRaises(ColumnNotFound):
            self.db.select("test", "email")

    def test_select_not_found(self):
        """
        Несуществующая таблица — TableNotFound.
        """
        with self.assertRaises(TableNotFound):
            self.db.select("no_table")


if __name__ == "__main__":
    unittest.main()