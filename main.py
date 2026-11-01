# Демонстрация класса Database.
# Успех = метод завершился без исключения.

from db import Database, TableAlreadyExists, TableNotFound, ColumnNotFound


db = Database("database")

print("========== ДЕМОНСТРАЦИЯ СУБД ==========\n")


print("--- 1. Создание users ---")
try:
    db.create_table("users", ["id", "name", "age"])
except TableAlreadyExists as e:
    print("  ", e)
print()


print("--- 2. Повторное создание users ---")
try:
    db.create_table("users", ["id", "name", "age"])
except TableAlreadyExists as e:
    print("  ", e)
print()


print("--- 3. Добавление данных ---")
try:
    db.insert("users", ["1", "Вася", "20"])
    db.insert("users", ["2", "Петя", "22"])
    db.insert("users", ["3", "Маша", "19"])
except (TableNotFound, ValueError) as e:
    print("  ", e)
print()


print("--- 4. Все поля (select без параметра) ---")
try:
    matrix = db.select("users")
    for row in matrix:
        print("  " + " | ".join(row))
except TableNotFound as e:
    print("  ", e)
print()


print("--- 5. Только name,age ---")
try:
    matrix = db.select("users", "name,age")
    for row in matrix:
        print("  " + " | ".join(row))
except (TableNotFound, ColumnNotFound) as e:
    print("  ", e)
print()


print("--- 6. Порядок age,name ---")
try:
    matrix = db.select("users", "age,name")
    for row in matrix:
        print("  " + " | ".join(row))
except (TableNotFound, ColumnNotFound) as e:
    print("  ", e)
print()


print("--- 7. Дубли: name,name ---")
try:
    matrix = db.select("users", "name,name")
    for row in matrix:
        print("  " + " | ".join(row))
except (TableNotFound, ColumnNotFound) as e:
    print("  ", e)
print()


print("--- 8. Несуществующее поле: email ---")
try:
    matrix = db.select("users", "email")
    for row in matrix:
        print("  " + " | ".join(row))
except (TableNotFound, ColumnNotFound) as e:
    print("  ", e)
print()


print("--- 9. Удаление users ---")
try:
    db.drop_table("users")
except TableNotFound as e:
    print("  ", e)
print()


print("--- 10. Повторное удаление users ---")
try:
    db.drop_table("users")
except TableNotFound as e:
    print("  ", e)
print()


print("========== ГОТОВО ==========")