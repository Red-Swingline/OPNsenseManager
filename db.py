import sqlite3

mydb = sqlite3.connect("rules.db", check_same_thread=False)

db = mydb.cursor()
