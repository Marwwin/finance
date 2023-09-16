import sqlite3
from sqlite3 import Error

DB_FILENAME = "db/finance.db"


def get_bucket(key: str):
    query = f"SELECT * FROM {key}"
    con, cur = execute(query)
    bucket = cur.fetchall()
    con.close()
    return bucket


def add_transaction(bucket: str, name: str, amount: float):
    query = f"INSERT INTO {bucket} (name, amount) VALUES (?, ?);"
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
    return get_transaction_by_id(bucket, transaction_id)


def get_transaction_by_id(bucket: str, transaction_id: int):
    query = f"SELECT * FROM {bucket} where id=?"
    con, cur = execute(query, (transaction_id,))
    transaction = cur.fetchall()[0]
    con.close()
    return transaction


def delete_transaction(bucket: str, transaction_id: int):
    query = f"DELETE FROM {bucket} WHERE id=?"
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


