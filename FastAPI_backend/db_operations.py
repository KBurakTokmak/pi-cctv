import datetime
import sqlite3
from contextlib import contextmanager
from typing import Iterator


@contextmanager
def database_connection(database_path: str) -> Iterator[sqlite3.Connection]:
    """connect to main database in given path"""
    con = sqlite3.connect(database_path)
    try:
        yield con
    finally:
        con.close()


def create_table_if_not_exists(con: sqlite3.Connection) -> None:
    cur = con.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS detected_people
                   (time_date TEXT PRIMARY KEY, name TEXT)''')


def insert_person(con: sqlite3.Connection, name: str) -> None:
    """Inserts person to detected people table in given connected database"""
    cur = con.cursor()
    current_datetime = datetime.datetime.now()
    timestring = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    cur.execute('''INSERT INTO detected_people VALUES (?, ?)''', (timestring, name))
    con.commit()


def log_person_to_database(name: str) -> None:
    """given name as text will be logged to main database"""
    with database_connection("database/camera_log.db") as con:
        create_table_if_not_exists(con)
        insert_person(con, name)
