import sqlite3

con = sqlite3.connect('users.db')
cur = con.cursor() 
cur.execute('CREATE TABLE IN NOT EXISTS ')
con.close()

