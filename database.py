import sqlite3

con = sqlite3.connect('users.db')
cur = con.cursor() 
cur.execute('CREATE TABLE IF NOT EXISTS tournaments (name TEXT);')
cur.execute('CREATE TABLE IF NOT EXISTS accounts (id INTEGER PRIMARY KEY AUTOINCREMENT, name STRING, password STRING, salt STRING)')
con.commit()
con.close()

def create_tournament(tournament_name, events):
    con = sqlite3.connect('users.db')
    cur = con.cursor()
    cur.execute(f'CREATE TABLE IF NOT EXISTS {tournament_name} (id INTEGER PRIMARY KEY AUTOINCREMENT, Team String)')
    for event in events:
        cur.execute(f'ALTER TABLE {tournament_name} ADD {event} STRING')
    cur.execute('INSERT INTO tournaments (name) VALUES (?)', (tournament_name, ))
    con.commit()
    con.close()
    return True

def read_table(tournament_name):
    con = sqlite3.connect('users.db')
    cur=con.cursor()
    cur.execute('READ * FROM ?', (tournament_name, ))
    data = cur.fetchall()
    con.close()
    return data

def add_to_table(tournament_name, school_name, data):
    event_names = []
    scores = []
    for event in data:
        event_names.append(event)
        scores.append(data[event])
    con = sqlite3.connect('users.db')
    cur = con.cursor()
    cur.execute('INSERT INTO ? (Team) VALUES (?)', (tournament_name, school_name))
    for i in range(len(scores)):
        cur.execute(f'UPDATE TABLE {tournament_name} SET ? = ? WHERE Team = ?', (event_names[i], scores[i], school_name))
    con.commit()
    con.close()
    return True


create_tournament("test_tournament_2", ['event1', 'event2'])


