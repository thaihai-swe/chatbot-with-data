import sqlite3
from contextlib import contextmanager


def dict_row(cursor, row):
    return {description[0]: row[index] for index, description in enumerate(cursor.description)}


@contextmanager
def get_connection(sqlite_path):
    connection = sqlite3.connect(sqlite_path)
    connection.row_factory = dict_row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()
