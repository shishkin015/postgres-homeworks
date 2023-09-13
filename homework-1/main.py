"""Скрипт для заполнения данными таблиц в БД Postgres."""
import csv

import psycopg2

employees = 'north_data/employees_data.csv'
customers = 'north_data/customers_data.csv'
orders = 'north_data/orders_data.csv'

tables = [employees, customers, orders]

# connect to db
conn = psycopg2.connect(host='localhost', database='north', user='postgres', password='admin@123')
try:
    with conn:
        with conn.cursor() as cur:
            for table in tables:
                if table == employees:
                    with open(table, 'r', newline="") as csv_f:
                        reader = csv.reader(csv_f)
                        values = []
                        for row in reader:
                            values.append(tuple(row))
                        cur.executemany("INSERT INTO employees VALUES (%s, %s, %s, %s, %s, %s)", values[1:])
                        cur.execute("SELECT * FROM employees")
                elif table == customers:
                    with open(table, 'r', newline="") as csv_f:
                        reader = csv.reader(csv_f)
                        values = []
                        for row in reader:
                            values.append(tuple(row))
                        cur.executemany("INSERT INTO customers VALUES (%s, %s, %s)", values[1:])
                        cur.execute("SELECT * FROM customers")
                else:
                    with open(table, 'r', newline="") as csv_f:
                        reader = csv.reader(csv_f)
                        values = []
                        for row in reader:
                            values.append(tuple(row))
                        cur.executemany("INSERT INTO orders VALUES (%s, %s, %s, %s, %s)", values[1:])
                        cur.execute("SELECT * FROM orders")


finally:
    # close cursor and connection
    conn.close()

