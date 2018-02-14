#/bin/bash
import os
import sqlite3 as lite

os.makedirs('keys')
con = lite.connect('bar_tunnel/db/bar.db')

with con:
    cur = con.cursor()
    cur.execute("CREATE TABLE List(id INTEGER PRIMARY KEY AUTOINCREMENT, nym TEXT, pk TEXT, shared_key TEXT, label TEXT)")