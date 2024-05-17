import sqlite3
import random
import string
import hashlib

#Creates database and tables for initialization
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

def create_tournament(tournament_name: str, events: list, creator: str) -> str:
    '''
    Creates a new table for a tournament
    Params:
        tournament_name: name of tournament
        events: list of all events
        creator: user who created the event
    '''
    if check_exists(tournament_name) == False:
        return "A tournament with that name already exists."
    if len(events) != len(set(events)): # Check if the event list has any duplicates.
        return "Event names must be unique."
    con = sqlite3.connect('users.db')
    cur = con.cursor()
    cur.execute(f'CREATE TABLE IF NOT EXISTS {tournament_name} (Team String)')
    for event in events:
        event = event.replace(' ', '_')
        cur.execute(f'ALTER TABLE {tournament_name} ADD {event} TEXT')
    cur.execute('INSERT INTO tournaments (name, creator) VALUES (?, ?)', (tournament_name, creator))
    con.commit()
    con.close()
    return ""

def read_table(tournament_name: str) -> list:
    '''
    Returns a table
    Params:
        tournament_name: Name of tournamet
    
    Returns:
        List of tuples which is the table of the tournament
    '''
    if check_exists(tournament_name):
        return False
    con = sqlite3.connect('users.db')
    cur=con.cursor()
    cur.execute(f'SELECT * FROM {tournament_name}')
    data = cur.fetchall()
    con.close()
    return data

def add_to_table(tournament_name: str, school_name: str, data: dict) -> bool:
    '''
    Add data to table
    Params:
        tournament_name: Name of tournament
        school_name: name of school of team
        data: Dictionary where key is the event name, and the value is the placement/score for that event
    
    Returns:
        Boolean if the addition to the table was a success
    '''
    if check_exists(tournament_name):
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

def register(username: str, password: str) -> bool:
    '''
    Register a new account
    Params:
        username: username of user
        password: password of user
    
    Returns: 
        Boolean if registering account was successful
    '''
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

def login(username: str, password: str) -> bool:
    '''
    Logins user
    Params: 
        username: username of user
        password: password of user
    
    Returns:
        Boolean if the login was successful
    '''
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

def verify_creator(name:str, tourny_name: str) -> bool:
    '''
    Verify that the person trying to access the tournament is the creator or not
    Params:
        name: name of the user
        tourny_name: name of the tournament

    Return:
        boolean of if the user is the creator of the tournament or not
    '''
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

def update_row(tourny_name: str, team: str, data: dict) -> bool:
    '''
    Allows the user to change tournament data if initial entry was incorrect
    Params: 
        tourny_name: name of tournament
        team: name of team
        data: dictionary where key is the event name, and value is the new placement for that event
    Return:
        Boolean on the change was succesful
    '''
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

def check_exists(tournament_name: str) -> bool:
    '''
    Check to see if the tournament exists
    Param:
        tournament_name: name of tournament

    Return:
        boolean if the tournament exists or not
    '''
    con = sqlite3.connect('users.db')
    cur = con.cursor()
    cur.execute('SELECT * FROM tournaments WHERE name = ?', (tournament_name, ))
    data = cur.fetchall()
    con.close()
    return len(data) == 0

def get_all_tournaments() -> list:
    '''
    Get all the tournaments
    Returns:
        Returns a list of all tournaments
    '''
    rtn = []
    con = sqlite3.connect('users.db')
    cur = con.cursor()
    cur.execute('SELECT name FROM tournaments')
    data = cur.fetchall()
    con.close()
    for name in data:
        rtn.append(name[0])
    return rtn

def get_participated_events(school_name: str) -> list:
    '''
    Gets all the tournaments that the team/school participated in
    Params:
        school_name: name of team/school

    Return:
        List of all participated tournaments
    '''
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

def get_events(tourny_name: str) -> list:
    '''
    Get all the events in a tournament
    Params:
        tourny_name: name of tournament

    Return: 
        List of all events in tournament
    '''
    rtn = []
    con = sqlite3.connect('users.db')
    cur = con.cursor()
    cur.execute(f'PRAGMA table_info({tourny_name})')
    data = cur.fetchall()
    for i in range(1, len(data)):
        rtn.append(data[i][1])
    con.close()
    return rtn

def get_placements(team_name: str) -> dict:
    '''
    Get the placements for a team for every tournament
    Params:
        team_name: name of team

    Return:
        dictionary where key is the tournament name, and the value is a list of placements for that tournament
    '''
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

def add_participant(team_name: str, tournament_name: str, participant_name: str, placement: str, event_name: str) -> bool:
    '''
    Add a participant to a team
    Params:
        team_name: name of team
        tournamet_name: name of tournament
        participant_name: name of participant
        placement: placement of participant
        event_name: name of event
    
    Return:
        boolean if adding the participant was successful or not
    '''
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

def get_participant_data(team_name: str, tournament_name: str, participant_name: str) -> list:
    '''
    Get data for a participant
    Params:
        team_name:name of team
        tournament_name: name of tournament
        participant_name: name of participant

    Return:
        List of lists where there is event name and placement for every list inside
    '''
    con = sqlite3.connect('School.db')
    cur = con.cursor()
    cur.execute('SELECT event_name, placement FROM teams WHERE team_name=? AND tournament_name=? AND participant_name=?', (team_name, tournament_name, participant_name))
    data = cur.fetchall()
    con.close()
    return data

def get_all_participants(team_name: str) -> list:
    '''
    Gets all participants in a team
    Params:
        team_name: name of team

    Return:
        List of all participant on team
    '''
    rtn = []
    con = sqlite3.connect('School.db')
    cur = con.cursor()
    cur.execute('SELECT participant FROM teams WHERE team_name=?', (team_name, ))
    data = cur.fetchall()
    for participant in data:
        if participant[0] not in rtn:
            rtn.append(participant[0])
    con.close()
    return rtn
