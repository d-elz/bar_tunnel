#/bin/bash
import os
import sqlite3 as lite

os.makedirs('keys')
os.makedirs('bar_tunnel/db')
con = lite.connect('bar_tunnel/db/database.db')

with con:
    cur = con.cursor()
    cur.execute("CREATE TABLE List(id INTEGER PRIMARY KEY AUTOINCREMENT, nym TEXT, pk TEXT, shared_key TEXT, label TEXT)")