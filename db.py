import sqlite3
from sqlite3 import Error
from typing import Tuple, Union

DB_FILENAME = "db/finance.db"


def get_bucket(table: str):
    query = f"SELECT * FROM {table}"
    con, cur = execute(query)
    bucket = cur.fetchall()
    con.close()
    return bucket


def get_all_buckets():
    query = "SELECT name FROM sqlite_master WHERE type='table'"
    con, cur = execute(query)
    buckets = {}
    for row in cur.fetchall():
        buckets[row[0]] = get_bucket(row[0])
    con.close()
    return buckets


def add_transaction(table: str, name: str, amount: float):
    query = f"INSERT INTO {table} (name, amount) VALUES (?, ?);"
    con, cur = execute(
        query,
        (
            name,
            amount,
        ),
    )
    con.commit()
    transaction_id = cur.lastrowid
    con.close()
    return get_transaction_by_id(table, transaction_id)


def get_transaction_by_id(table: str, transaction_id: int):
    query = f"SELECT * FROM {table} where id=?"
    con, cur = execute(query, (transaction_id,))
    transaction = cur.fetchall()[0]
    con.close()
    return transaction


def edit_transaction(
    table: str, transaction_id: int, edit: Tuple[str, Union[str, float, int]]
):
    column, value = edit
    query = f"UPDATE {table} SET {column} = ? WHERE id = ?"
    con, cur = execute(
        query,
        (
            value,
            transaction_id,
        ),
    )
    con.commit()
    con.close()


def delete_transaction(table: str, transaction_id: int):
    query = f"DELETE FROM {table} WHERE id=?"
    con, cur = execute(query, (transaction_id,))
    con.commit()
    con.close()


def get_con():
    con = None
    try:
        con = sqlite3.connect(DB_FILENAME)
    except Error as e:
        print(e)
    return con


def execute(query: str, values=None):
    con = get_con()
    cur = con.cursor()
    if values:
        cur.execute(query, values)
    else:
        cur.execute(query)
    return con, cur
