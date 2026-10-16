# Тесты функций интерфейса СУБД.
# Проверяют успешные и ошибочные сценарии.

from db import (
    create_table, drop_table, alter_table, insert, select,
    TableAlreadyExists, TableNotFound,
)


print("========== ТЕСТЫ ==========\n")


print("--- ТЕСТ 1: создание таблицы ---")
try:
    create_table("test", ["id", "name"])
    print("OK: таблица test создана")
except TableAlreadyExists as e:
    print("Ошибка:", e)
print()


print("--- ТЕСТ 2: повторное создание ---")
try:
    create_table("test", ["id", "name"])
    print("ОШИБКА ТЕСТА: исключение не сработало")
except TableAlreadyExists as e:
    print("OK: поймано TableAlreadyExists")
print()


print("--- ТЕСТ 3: insert ---")
try:
    insert("test", ["1", "Вася"])
    insert("test", ["2", "Петя"])
    print("OK: строки добавлены")
except (TableNotFound, ValueError) as e:
    print("Ошибка:", e)
print()


print("--- ТЕСТ 4: insert с малым числом значений ---")
try:
    insert("test", ["3"])
    print("ОШИБКА ТЕСТА: исключение не сработало")
except ValueError as e:
    print("OK: поймано ValueError")
print()


print("--- ТЕСТ 5: insert в несуществующую таблицу ---")
try:
    insert("no_table", ["1", "X"])
    print("ОШИБКА ТЕСТА: исключение не сработало")
except TableNotFound as e:
    print("OK: поймано TableNotFound")
print()


print("--- ТЕСТ 6: select возвращает матрицу ---")
try:
    matrix = select("test")
    print("OK: получено", matrix)
except TableNotFound as e:
    print("Ошибка:", e)
print()


print("--- ТЕСТ 7: alter_table ---")
try:
    alter_table("test", ["id", "name", "age"])
    print("OK: структура изменена")
except TableNotFound as e:
    print("Ошибка:", e)
print()


print("--- ТЕСТ 8: alter_table несуществующей ---")
try:
    alter_table("no_table", ["id"])
    print("ОШИБКА ТЕСТА: исключение не сработало")
except TableNotFound as e:
    print("OK: поймано TableNotFound")
print()


print("--- ТЕСТ 9: drop_table ---")
try:
    drop_table("test")
    print("OK: таблица удалена")
except TableNotFound as e:
    print("Ошибка:", e)
print()


print("--- ТЕСТ 10: повторный drop_table ---")
try:
    drop_table("test")
    print("ОШИБКА ТЕСТА: исключение не сработало")
except TableNotFound as e:
    print("OK: поймано TableNotFound")
print()


print("========== ТЕСТЫ ЗАВЕРШЕНЫ ==========")