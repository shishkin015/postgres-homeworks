import json

import psycopg2

from config import config


def main():
    script_file = 'fill_db.sql'
    json_file = 'suppliers.json'
    db_name = 'my_new_db'

    params = config()
    conn = None

    create_database(params, db_name)
    print(f"БД {db_name} успешно создана")

    params.update({'dbname': db_name})
    try:
        with psycopg2.connect(**params) as conn:
            with conn.cursor() as cur:
                execute_sql_script(cur, script_file)
                print(f"БД {db_name} успешно заполнена")

                create_suppliers_table(cur)
                print("Таблица suppliers успешно создана")

                suppliers = get_suppliers_data(cur, json_file)
                insert_suppliers_data(cur, suppliers)
                print("Данные в suppliers успешно добавлены")

                add_foreign_keys(cur)
                print(f"FOREIGN KEY успешно добавлены")

    except(Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


def create_database(params, db_name) -> None:
    """Создает новую базу данных."""
    conn = psycopg2.connect(dbname='postgres', **params)
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute(F'DROP DATABASE {db_name}')
    cur.execute(F'CREATE DATABASE {db_name}')

    cur.close()
    conn.close()


def execute_sql_script(cur, script_file) -> None:
    """Выполняет скрипт из файла для заполнения БД данными."""
    # Открываем и читаем SQL-скрипт из файла
    with open(script_file, 'r') as f:
        sql_script = f.read()
        cur.execute(sql_script)


def create_suppliers_table(cur) -> None:
    """Создает таблицу suppliers."""
    cur.execute(
        """
        CREATE TABLE suppliers (
        company_name VARCHAR(255) NOT NULL,
        contact VARCHAR(255),
        address VARCHAR(255),
        phone VARCHAR(255),
        fax VARCHAR(255),
        homepage VARCHAR(255),
        product_id INT UNIQUE
        )
        """
    )


def get_suppliers_data(cur, json_file: str) -> list[dict]:
    """Извлекает данные о поставщиках из JSON-файла и возвращает список словарей с соответствующей информацией."""
    suppliers = []

    with open(json_file, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
        for item in json_data:
            for i in item['products']:
                suppliers.append({'company_name': item['company_name'],
                                  'contact': item['contact'],
                                  'address': item['address'],
                                  'phone': item['phone'],
                                  'fax': item['fax'],
                                  'homepage': item['homepage'],
                                  'products': i
                                  })

    for supplier in suppliers:
        for key, value in supplier.items():
            if key == "products":
                cur.execute("SELECT product_id FROM products WHERE product_name = %s", (value,))
                result = cur.fetchone()
                if result:
                    product_id = result[0]
                    supplier['products'] = product_id

    return suppliers


def insert_suppliers_data(cur, suppliers: list[dict]) -> None:
    """Добавляет данные из suppliers в таблицу suppliers."""
    insert_query = "INSERT INTO suppliers (company_name, contact, address, phone, fax, homepage, product_id) " \
                   "VALUES (%s, %s, %s, %s, %s, %s, %s)"

    # Проходим по списку словарей и вставляем данные
    for supplier in suppliers:
        values = (
            supplier.get("company_name"),
            supplier.get("contact"),
            supplier.get("address"),
            supplier.get("phone"),
            supplier.get("fax"),
            supplier.get("homepage"),
            supplier.get("products")
        )
        cur.execute(insert_query, values)


def add_foreign_keys(cur) -> None:
    """Добавляет foreign key со ссылкой на supplier_id в таблицу products."""
    sql = f"ALTER TABLE products ADD CONSTRAINT fk_supplier FOREIGN KEY (product_id) " \
          f"REFERENCES suppliers(product_id)"

    # Выполняем SQL-запрос
    cur.execute(sql)


if __name__ == '__main__':
    main()
