import sqlite3
import os
from datetime import datetime
import pytz


conn = sqlite3.connect(os.path.join("db", "base.db"))
cursor = conn.cursor()


def date_formatted(date=None) -> str:

    if date is None:
        return get_now_datetime().strftime("%Y-%m-%d-%H-%M-%S")
    else:
        return date.strftime("%Y-%m-%d-%H-%M-%S")


def get_now_datetime() -> datetime:

    tz = pytz.timezone("Europe/Moscow")
    now = datetime.now(tz)
    return now


def insert(table, column_values):
    columns = ', '.join( column_values.keys() )
    values = [tuple(column_values.values())]
    placeholders = ", ".join( "?" * len(column_values.keys()) )
    cursor.executemany(
        f"INSERT INTO {table} "
        f"({columns}) "
        f"VALUES ({placeholders})",
        values)
    conn.commit()


def select_date_create(table, columns):
    columns = ', '.join(columns)
    cursor.execute(
        f"SELECT {columns} "
        f"FROM {table} "
        f"ORDER BY date_create DESC "
        f"LIMIT 1 ")

    return cursor.fetchall()


def _init_db():

    with open("createdb.sql", "r") as f:
        sql = f.read()
    cursor.executescript(sql)
    conn.commit()


def check_db_exists():

    cursor.execute("SELECT name FROM sqlite_master "
                   "WHERE (type='table' AND name='shots') "
                   "OR (type='table' AND name='locations')")
    table_exists = cursor.fetchall()

    if table_exists:
        return

    _init_db()

check_db_exists()

