#/bin/bash
import os
import sqlite3 as lite

os.makedirs('/keys')
con = lite.connect('bar_tunnel/db/bar.db')

with con:
    cur = con.cursor()
    cur.execute("CREATE TABLE contacts(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, label TEXT, publickey TEXT, sharedkey TEXT)")
    cur.execute("CREATE TABLE clients(id INTEGER PRIMARY KEY AUTOINCREMENT, ip TEXT, port INT, timelogout TEXT)")
    cur.execute("CREATE TABLE messages(id INTEGER PRIMARY KEY AUTOINCREMENT, message TEXT)")
    cur.execute("CREATE TABLE history(id INTEGER PRIMARY KEY AUTOINCREMENT, message TEXT, time TEXT)")

cur.execute("CREATE UNIQUE INDEX 'id_UNIQUE' ON 'contacts' ('id' ASC);")