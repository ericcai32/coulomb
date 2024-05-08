import sqlite3

con = sqlite3.connect('users.db')
cur = con.cursor() 
con.close()

print('helllo')