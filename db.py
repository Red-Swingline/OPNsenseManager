import sqlite3

mydb = sqlite3.connect("rules.db", check_same_thread=False)
db = mydb.cursor()


def create_tables():
    db.execute("""CREATE TABLE  IF NOT EXISTS rules(
    id integer PRIMARY KEY,
    rname TEXT,
    uuid TEXT NOT NULL UNIQUE
    );""")

    db.execute("""CREATE TABLE  IF NOT EXISTS api_info(
    id integer PRIMARY KEY,
    api_key TEXT NOT NULL UNIQUE,
    api_secret TEXT NOT NULL UNIQUE,
    url TEXT NOT NULL UNIQUE,
    port INTEGER
    );""")