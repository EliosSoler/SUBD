# Демонстрация программного интерфейса СУБД.
# Успех = функция завершилась без исключения

from db import (
    create_table, drop_table, alter_table, insert, select,
    TableAlreadyExists, TableNotFound,
)


print("========== ДЕМОНСТРАЦИЯ СУБД ==========\n")


# --- 1. Создание таблицы users ---
print("Создание users:")
try:
    create_table("users", ["id", "name", "age"])
except TableAlreadyExists as e:
    print("  ", e)
print()


# --- 2. Повторное создание (ошибка) ---
print("Повторное создание users:")
try:
    create_table("users", ["id", "name", "age"])
    print("   Таблица создана (не должно быть)")
except TableAlreadyExists as e:
    print("  ", e)
print()


# --- 3. Добавление данных ---
print("Добавление данных:")
try:
    insert("users", ["1", "Вася", "20"])
    insert("users", ["2", "Петя", "22"])
    insert("users", ["3", "Маша", "19"])
except (TableNotFound, ValueError) as e:
    print("  ", e)
print()


# --- 4. Insert с неверным числом значений ---
print("Insert с неверным числом значений:")
try:
    insert("users", ["4", "Коля"])
    print("   Строка добавлена (не должно быть)")
except ValueError as e:
    print("  ", e)
print()


# --- 5. Чтение данных (матрица) ---
print("Содержимое users:")
try:
    matrix = select("users")
    print("  Колонки: id, name, age")
    for row in matrix:
        print("  " + " | ".join(row))
except TableNotFound as e:
    print("  ", e)
print()


# --- 6. Создание таблицы orders ---
print("Создание orders:")
try:
    create_table("orders", ["id", "user_id", "amount"])
    insert("orders", ["1", "1", "500"])
    insert("orders", ["2", "2", "1200"])
except (TableAlreadyExists, TableNotFound, ValueError) as e:
    print("  ", e)
print()


# --- 7. Изменение таблицы users ---
print("Изменение структуры users:")
try:
    alter_table("users", ["id", "name", "age", "email"])
except TableNotFound as e:
    print("  ", e)
print()


# --- 8. Удаление orders ---
print("Удаление orders:")
try:
    drop_table("orders")
except TableNotFound as e:
    print("  ", e)
print()


# --- 9. Повторное удаление orders ---
print("Повторное удаление orders:")
try:
    drop_table("orders")
    print("   Удалено (не должно быть)")
except TableNotFound as e:
    print("  ", e)
print()


# --- 10. Финальный показ users ---
print("Финальное содержимое users:")
try:
    matrix = select("users")
    print("  Колонки: id, name, age, email")
    for row in matrix:
        print("  " + " | ".join(row))
except TableNotFound as e:
    print("  ", e)
print()


print("========== ГОТОВО ==========")