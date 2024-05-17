import sqlite3
import random
import string
import hashlib

con = sqlite3.connect('users.db')
cur = con.cursor() 
cur.execute('CREATE TABLE IF NOT EXISTS tournaments (name TEXT, creator TEXT, schools TEXT);')
cur.execute('CREATE TABLE IF NOT EXISTS accounts (id INTEGER PRIMARY KEY AUTOINCREMENT, name STRING, password STRING, salt STRING)')    
con.commit()
con.close()

con = sqlite3.connect('School.db')
cur = con.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS teams (team_name TEXT, tournament_name TEXT, event_name TEXT, participant_name TEXT, placement TEXT)')
con.commit()
con.close()

def create_tournament(tournament_name, events, creator):
    if check_exists(tournament_name) == False:
        return False
    con = sqlite3.connect('users.db')
    cur = con.cursor()
    cur.execute(f'CREATE TABLE IF NOT EXISTS {tournament_name} (Team String)')
    for event in events:
        event = event.replace(' ', '_')
        cur.execute(f'ALTER TABLE {tournament_name} ADD {event} TEXT')
    cur.execute('INSERT INTO tournaments (name, creator) VALUES (?, ?)', (tournament_name, creator))
    con.commit()
    con.close()
    return True

def read_table(tournament_name):
    if check_exists(tournament_name):
        return False
    con = sqlite3.connect('users.db')
    cur=con.cursor()
    cur.execute(f'SELECT * FROM {tournament_name}')
    data = cur.fetchall()
    con.close()
    return data

def add_to_table(tournament_name, school_name, data):
    if check_exists(tournament_name):
        print('uhhhh')
        return False
    event_names = []
    scores = []
    for event in data:
        event_names.append(event)
        scores.append(data[event])
    con = sqlite3.connect('users.db')
    cur = con.cursor()
    cur.execute(f'INSERT INTO {tournament_name} (Team) VALUES (?)', (school_name, ))
    cur.execute(f'SELECT schools FROM tournaments WHERE name=?', (tournament_name, ))
    schools = str(cur.fetchall()[0][0]).split()
    if schools[0] == 'None':
        schools = []
    if school_name not in schools:
        schools.append(school_name)

    schools = ' '.join(map(str, schools))
    cur.execute(f'UPDATE tournaments SET schools=? WHERE name=?', (schools, tournament_name))
    for i in range(len(scores)):
        cur.execute(f'UPDATE {tournament_name} SET {event_names[i]} = {scores[i]} WHERE Team = ?', (school_name, ))
    con.commit()
    con.close()
    print('adding')
    return True

def register(username, password):
    con = sqlite3.connect('users.db')
    cur = con.cursor()
    cur.execute("SELECT name FROM accounts where name=?", (username,))
    if not cur.fetchall():
        hash = hashlib.sha256()
        source = string.ascii_letters + string.digits
        salt = ''.join((random.choice(source) for i in range(8)))
        password += salt
        hash.update(password.encode())
        passwordHash = hash.hexdigest()
        cur.execute('INSERT INTO accounts (name, password, salt) VALUES (?, ?, ?)', (username, passwordHash, salt))
        con.commit()
        con.close()
        return True
    con.close()
    return False

def login(username, password):
    con = sqlite3.connect('users.db')
    cur = con.cursor()
    cur.execute("SELECT name FROM accounts where name=?", (username,))
    if not cur.fetchall():
        return False
    cur.execute('SELECT password FROM accounts WHERE name=?', (username, ))
    hashed_password = cur.fetchall()[0][0]
    cur.execute('SELECT salt FROM accounts WHERE name=?', (username, ))
    salt = cur.fetchall()[0][0]
    password += salt
    hash = hashlib.sha256()
    hash.update(password.encode())
    passwordHash = hash.hexdigest()
    con.close()
    if passwordHash == hashed_password:
        return True
    else:
        return False

def verify_creator(name, tourny_name):
    con = sqlite3.connect('users.db')
    cur = con.cursor()
    cur.execute('SELECT creator FROM tournaments WHERE name=?', (tourny_name, ))
    data = cur.fetchall()
    con.close()
    try:
        data[0][0]
    except:
        return False
    data = data[0][0]
    return data == name

def update_row(tourny_name, team, data):
    con = sqlite3.connect('users.db')
    cur = con.cursor()
    cur.execute('SELECT name FROM tournaments WHERE name=?', (tourny_name, ))
    if not cur.fetchall():
        return False
    event_names = []
    scores = []
    for event in data:
        event_names.append(event)
        scores.append(data[event])
    for i in range(len(scores)):
        cur.execute(f'UPDATE {tourny_name} SET {event_names[i]} = {scores[i]} WHERE Team = ?', (team, ))
        con.commit()
    con.close()
    return True

def check_exists(tournament_name):
    con = sqlite3.connect('users.db')
    cur = con.cursor()
    cur.execute('SELECT * FROM tournaments WHERE name = ?', (tournament_name, ))
    data = cur.fetchall()
    con.close()
    return len(data) == 0

def get_all_tournaments():
    rtn = []
    con = sqlite3.connect('users.db')
    cur = con.cursor()
    cur.execute('SELECT name FROM tournaments')
    data = cur.fetchall()
    con.close()
    for name in data:
        rtn.append(name[0])
    return rtn

def get_participated_events(school_name):
    rtn = []
    con = sqlite3.connect('users.db')
    cur = con.cursor()
    cur.execute('SELECT name FROM tournaments')
    tourny_names = []
    data = cur.fetchall()
    for name in data:
        tourny_names.append(name[0])
    for tourny in tourny_names:
        cur.execute('SELECT schools FROM tournaments WHERE name=?', (tourny, ))
        tournys = str(cur.fetchall()[0][0]).split()
        if school_name in tournys:
            rtn.append(tourny)
    con.close()
    return rtn

def get_events(tourny_name):
    rtn = []
    con = sqlite3.connect('users.db')
    cur = con.cursor()
    cur.execute(f'PRAGMA table_info({tourny_name})')
    data = cur.fetchall()
    for i in range(1, len(data)):
        rtn.append(data[i][1])
    con.close()
    return rtn

def get_placements(team_name):
    rtn = {}
    con = sqlite3.connect('users.db')
    cur = con.cursor()
    data = get_participated_events(team_name)
    for event in data:
        temp_list = []
        cur.execute(f'SELECT * FROM {event} WHERE Team=?', (team_name, ))
        data = cur.fetchall()[0]
        for i in range(1, len(data)):
            temp_list.append(data[i])
        rtn[event] = temp_list
    con.close()
    print(rtn)
    return rtn

def add_participant(team_name, tournament_name, participant_name, placement, event_name):
    con = sqlite3.connect('School.db')
    cur = con.cursor()
    cur.execute('SELECT placement FROM teams WHERE team_name=? AND tournament_name=? AND participant_name=? AND event_name=?', (team_name, tournament_name, participant_name, event_name))
    data = cur.fetchall()
    if not data:
        cur.execute('INSERT INTO teams (team_name, tournament_name, participant_name, event_name, placement) VALUES (?, ?, ?, ?, ?)', (team_name, tournament_name, participant_name, event_name, placement))
        con.commit()
        con.close()
        return True
    con.close()
    return False

def get_participant_data(team_name, tournament_name, participant_name):
    con = sqlite3.connect('School.db')
    cur = con.cursor()
    cur.execute('SELECT event_name, placement FROM teams WHERE team_name=? AND tournament_name=? AND participant_name=?', (team_name, tournament_name, participant_name))
    data = cur.fetchall()
    con.close()
    return data

