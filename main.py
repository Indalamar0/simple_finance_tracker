import os
import psycopg2
import re
import time
from psycopg2.extras import RealDictCursor

def db_connect():
    while True:
        try:
            conn = psycopg2.connect(
            dbname = os.environ.get("DB_NAME"),
            user = os.environ.get("DB_USER"),
            password = os.environ.get("DB_PASSWORD"),
            host = "db",
            port = "5432",
        )
            conn.cursor_factory = RealDictCursor
            return conn
        except Exception as err:
            print(f"[Ошибка] {err}")

conn = db_connect() # чтобы заходил под пользователем kolyan, а не postgres

time.sleep(1)

def main_menu():
    while True:
        print("\n" + "-" * 52)
        print(
    """
    Выберите, что вы хотите сделать
    [1] Добавить категорию
    [2] Добавить расход / доход
    [3] Показать текущий баланс
    [4] Вывести отчет по категориям
    [0] Выход
    """
    )
        try:
            value = int(input())
            if value == 1:
                db_create_category()
            elif value == 2:
                db_create_op()
            elif value == 3:
                print("-" * 52)
                print(f"\nТекущий баланс: {db_balance_value(balance_value=True)}")
                print("\nВозвращаю в главное меню")
            elif value == 4:
                db_show_expenses()
            elif value == 0:
                break
            else:
                print("[Ошибка] Введите значение 1, 2, 3, 4 или 0")
        except ValueError:
            print("[Ошибка] Введите значение 1, 2, 3, 4 или 0")

def db_create_category():
    print("-" * 52)
    try:
        with conn.cursor() as cursor:
            query = "SELECT LOWER(name) AS name FROM categories ORDER BY name ASC"
            cursor.execute(query)
            rows = cursor.fetchall()
            arr = []
            for row in rows:
                arr.append(str(row["name"]))
            print(arr)
            while True:
                raw_input = input("\nВведите название категории: ")
                entry_cat = re.sub(r'[^\w\s]', '', raw_input).replace('_','').strip()
                if not entry_cat:
                    print("[Ошибка] Название содержит недопустимые символы")
                    continue
                if entry_cat.lower() in arr:
                    print(f"{entry_cat} уже есть такая категория")
                else: 
                    break
    except Exception as err:
        print(f"[Ошибка] {err}")
        print("\nВозвращаю в главное меню")
        return
    print(
        """
        Выберите тип категории 
        [1] Расход
        [2] Доход
        [0] Выход
        """
        )
    while True:
        entry_type = input()
        if entry_type == '1':
            entry_type = "expense"
            break
        elif entry_type == '2':
            entry_type = "income"
            break
        elif entry_type == '0':
            print("\nВозвращаю в главное меню")
            return
        else:
            print("Введите значение 1, 2 или 0")
    try:
        with conn:
            with conn.cursor() as cursor:
                query = "INSERT INTO categories(name,type) VALUES(%s, %s)"
                cursor.execute(query,(entry_cat,entry_type))
                print('Категория добавлена')
                return
    except psycopg2.DatabaseError as err:
        print(f"[Ошибка база данных]: {err}")
    except Exception as err:
        print(f"[Непредвиденная ошибка]: {err}") 
        return

def db_create_op():
    print("-" * 52)
    while True:
        print(
    """
    Выберите, что вы хотите добавить
    [1] Расход
    [2] Доход
    [0] Выход
    """
    )
        try:
            value = int(input())
            if value == 1:
                trans_type = "expense"
            elif value == 2:
                trans_type = "income"
            elif value == 0:
                print("\nВозвращаю в главное меню")
                return
            else:
                print("[Ошибка] Введите значение 1, 2 или 0")
                continue
        except ValueError:
            print("[Ошибка] Введите значение 1, 2 или 0")
        if trans_type == "expense" and db_balance_value(balance_value=True) == 0.0:
                print ("Извините, у вас 0 баланс, вам нечего тратить :(")
                continue
        try:
            with conn:
                with conn.cursor() as cursor:
                    query = "SELECT id, name FROM categories WHERE type = %s"
                    cursor.execute(query,(trans_type,))
                    rows = cursor.fetchall()
                    values = []
                    for row in rows:
                        values.append(row["id"])
                    if not values:
                        print("[Ошибка]: У вас нет ни одной категории!")
                        print("Сначала добавьте хотя бы одну категорию в меню")
                        return
                    while True:
                        try:
                            amount = float(input("\nВведите сумму операции: "))
                            if trans_type == "expense":
                                if amount <= 0:
                                    print("Расход должен быть больше 0")
                                elif amount > db_balance_value(balance_value=True):
                                    print("\n[Ошибка] Недостаточно средств на балансе")
                                    print(f"Текущий баланс: {db_balance_value(balance_value=True)}\n")
                                    break
                                else:
                                    break
                            else:
                                if amount > 0:
                                    break
                                else:
                                    print("Доход должен быть больше 0")
                        except ValueError:
                            print("[Ошибка]: Введите число")
        except Exception as err:
            print(f"[Непредвиденная ошибка]: {err}") 
            return
        if trans_type == "expense" and amount > db_balance_value(balance_value=True):
            continue
        break
    while True:
        try:
            print("\nСписок категорий: \n")
            for row in rows:
                print(f"[{row["id"]}] {row["name"]}")
            entry_cat = int(input('\nВыберите категорию: '))
            if entry_cat in values:
                break
            else:
                print("[Ошибка] Вы ввели неверное значение")
        except ValueError:
            print('\n[Ошибка] Введите число')
        except Exception as err:
            print(f'[Непредвиденная ошибка] {err}')
    print("""
Хотите добавить описание?
[1] Да!
[2] Сегодня не -_-
            """
        )
    while True:
        descript = None
        try:
            choice = int(input())
            if choice == 1:
                descript = input("Введите описание:\n")
                break
            elif choice == 2:
                break
            else:
                print("[Ошибка] Введите значение 1 или 2")
        except ValueError:
            print("[Ошибка] Введите значение 1 или 2")
    for row in rows:
        if row['id'] == entry_cat:
            try:
                with conn:
                    with conn.cursor() as cursor:
                        query = ("INSERT INTO transactions(amount,category_id,description) VALUES (%s,%s,%s)")
                        cursor.execute(query,(float(amount),row["id"],descript))
                        query_str = """ 
                                        SELECT t.category_id, c.name, t.amount, t.description 
                                        FROM transactions t 
                                        INNER JOIN categories c ON t.category_id = c.id 
                                        WHERE t.category_id = %s
                                        ORDER BY t.id DESC;
                                        """
                        cursor.execute(query_str,(row['id'],))
                        result = cursor.fetchone()
                        if trans_type == "expense":
                            print(f'[Добавлено]: Категория: {result["name"]}, Расход: {result["amount"]}, Описание: {result["description"]}')
                        else:
                            print(f'[Добавлено]: Категория: {result["name"]}, Доход: {result["amount"]}, Описание: {result["description"]}')
                        break
            except Exception as err:
                print(f"[Ошибка]: {err}")
                break
    print("\nВозвращаю в главное меню")
    return
 
def db_balance_value(balance_value=False):
    try:
        with conn.cursor() as cursor:
            query = """ 
            SELECT 
            COALESCE(SUM(CASE WHEN c.type = 'income' THEN t.amount END),0)
            -
            COALESCE(SUM(CASE WHEN c.type = 'expense' THEN t.amount END),0) AS balance
            FROM transactions t
            INNER JOIN categories c ON t.category_id = c.id;
            """
            cursor.execute(query)
            row = cursor.fetchone()
            if row:
                balance = float(row['balance']) 
            else:
                balance = 0.0
            if balance_value:
                return balance
    except Exception as err:
        print(f"[Непредвиденная ошибка]: {err}")           
        
def db_show_expenses():
    print("-" * 52)
    try:
        with conn:
            with conn.cursor() as cursor:
                query = """
                SELECT t.id, c.name, c.type, t.amount, t.category_id, t.date, t.description
                FROM transactions t
                INNER JOIN categories c ON t.category_id = c.id
                WHERE DATE_TRUNC('month', t.date) = DATE_TRUNC('month', NOW())
                ORDER BY c.type, t.category_id, t.amount DESC, t.id; 
                """
                cursor.execute(query)
                rows = cursor.fetchall()
                value = ""
                print("\nТекущие траты")
                for row in rows:
                    if row["type"] == "expense":
                        if value != row["name"]:
                            print(f"\nВ категории {row["name"]}\n")
                            print(f"{'ID':^8}{'Сумма':^12}{'Дата':^14}{'Описание':^23}")
                            value = row["name"]
                        date_str = str(row["date"])
                        desc_str = str(row["description"])
                        print(f"{f'[{row["id"]}]':^8}{row["amount"]:^12}{date_str:^14} {desc_str:^20}")
                if not value:
                    print ("Пока что трат нет")
                print("-" * 52)
                print("\nТекущий доход")
                for row in rows:
                    if row["type"] == "income":
                        if value != row["name"]:
                            print(f"\nВ категории {row["name"]}\n")
                            print(f"{'ID':^8}{'Сумма':^12}{'Дата':^14}{'Описание':^23}")
                            value = row["name"]
                        date_str = str(row["date"])
                        desc_str = str(row["description"])
                        print(f"{f'[{row["id"]}]':^8}{row["amount"]:^12}{date_str:^14} {desc_str:^20}")
                if not value:
                    print ("Пока что доходов нет")
                print("-" * 52)
                print("\nВозвращаю в главное меню")
                return
    except psycopg2.DatabaseError as err:
        print(f"[Ошибка база данных]: {err}")
    except Exception as err:
        print(f"[Непредвиденная ошибка]: {err}")

if __name__ == "__main__":
    main_menu()