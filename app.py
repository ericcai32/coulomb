from flask import Flask, send_file, request, redirect, render_template, Blueprint, jsonify, make_response
import redis
from uuid import uuid4, UUID
from database import *
from account_tools import *



app = Flask(__name__)


# List of tourneys
# One table for each tournament containing the actual data (obviously)
# List of accounts

@app.route('/')
def index():
    tournaments = get_all_tournaments()
    return render_template('tournament_list.j2', tournaments=tournaments)

@app.route('/new', methods=('GET', 'POST'))
def new():
    is_to = True # database.check_to() figure out if user is a to, or i think we just check if logged in here
    if not is_to:
        return "You do not have access to this page."
    if request.method == 'POST':
        # Get info from post request.
        tournament_name = request.form['name']
        events = request.form.getlist('event')
        print(events)
        if create_tournament(tournament_name, events, "test_user"): # implement tournament creator
            return redirect(f'tournaments/{tournament_name}')
        else:
            return "Tournament with this name already exists." # Probably should make this prettier
    if request.method == 'GET':
        return render_template('new.j2')
    
@app.route('/tournaments/<tournament_name>')
def tournament(tournament_name: str):
    tournament_exists = True #check_exists(tournament_name) # FIX THIS
    if tournament_exists:
        tournament_results = read_table(tournament_name)
        # tournament_results = [["polo ridge", 1, 3, 1], ["metrolina", 2, 1, 3], ["saksham elementary", 3, 2, 2]]
        return render_template('tournament.j2', tournament=tournament_name, data=tournament_results)
    else:
        return send_file("static/404.html")

@app.route('/teams/<team_name>', methods=('GET', 'POST'))
def team(team_name: str):
    team_exists = True # FIX THIS
    if team_exists:
        return f"[TEAM PAGE FOR {team_name}]"
    else:
        return send_file("static/404.html")

@app.route('/teams/<team_name>/<participant_name>')
def participant(team_name: str, participant_name: str):
    team_exists = True # FIX THIS.
    participant_exists = True # FIX THIS
    if team_exists and participant_exists:
        return f"[PARTICPANT PAGE FOR {participant_name} ON TEAM {team_name}]"
    else:
        return "[404 PAGE]"

@app.route('/login', methods=('GET', 'POST'))
def login():
    """
    Allows the user to log in or register an account.
    Returns:
        On error: the rendered login template with an error message filled in.
        On success: Redirects to the index page and stores the session data as cookies.
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not (username and password):
            return redirect('login')
        if request.form['mode'] == 'login':
            mode = 'LOGIN'
        elif request.form['mode'] == 'register':
            mode = 'REGISTER'
        else:
            return redirect('login')
        
        if mode == 'REGISTER':
            error = register_user(username, password)
            if error:
                return render_template('login.j2', error=error)
            token = begin_session(username)
            resp = make_response(redirect(f'/'))
            resp.set_cookie('token', token)
            return resp
        if mode == 'LOGIN':
            error = check_login(username, password)
            if error:
                return render_template('login.j2', error=error)
            token = begin_session(username)
            resp = make_response(redirect(f'/'))
            resp.set_cookie('token', token)
            return resp
    else:
        if check_session():
            token = request.cookies.get('token')
            username = get_session(token)
            return redirect(f'/')
        else:
            return render_template('login.j2')

app.run(port=8022, debug=True)