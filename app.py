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
    is_logged = check_session()
    if not is_logged:
        return redirect('/login')
    if request.method == 'POST':
        # Get info from post request.
        tournament_name = request.form['name'].replace(' ', '_')
        events = request.form.getlist('event')
        token = request.cookies.get('token')
        user = get_session(token)
        error = create_tournament(tournament_name, events, user)
        if error:
            return render_template('new.j2', error=error)
        else:
            return redirect(f'tournaments/{tournament_name}')
    if request.method == 'GET':
        return render_template('new.j2')
    
@app.route('/tournaments/<tournament_name>', methods=('GET', 'PUT'))
def tournament(tournament_name: str):
    if request.method == 'GET':
        tournament_exists = not check_exists(tournament_name)
        if tournament_exists:   
            is_to = False
            is_logged = check_session()
            tournament_results = read_table(tournament_name)
            if is_logged:
                token = request.cookies.get('token')
                user = get_session(token)
                is_to = verify_creator(user, tournament_name)
                joined = user in ([element for row in tournament_results for element in row])
            tournament_events = get_events(tournament_name)
            return render_template('tournament.j2', tournament=tournament_name, events=tournament_events, data=tournament_results, is_to=is_to, is_logged=is_logged, joined=joined)
        else:
            return send_file("static/404.html")
    elif request.method == 'PUT':
        data = request.get_json()
        events = get_events(tournament_name)
        for team_results in data:
            new_data = {}
            team = team_results[0]
            for i in range(len(events)):
                new_data[events[i]] = int(team_results[i + 1])
            if not update_row(tournament_name, team.strip(), new_data):
                return jsonify("fail")
            

        return jsonify("success")
    
@app.route('/tournaments/<tournament_name>', methods=['POST'])
def add_tournament(tournament_name):
    token = request.cookies.get('token')
    add_to_table(tournament_name, get_session(token), {})
    return 'school added'

@app.route('/teams/<team_name>', methods=('GET', 'POST'))
def team(team_name: str):
    data = get_participated_events(team_name)
    # token = request.cookies.get('token')
    # user = get_session(token)
    tournament_events = {}
    for tournament in data:
        tournament_events[tournament] = get_events(tournament)
    placements = get_placements(team_name)
    return render_template('team.j2', participated_events=data, user=team_name, tournament_events=tournament_events, placements=placements)

@app.route('/teams/<team_name>/<participant_name>')
def participant(team_name: str, participant_name: str):
    team_exists = True # FIX THIS.
    participant_exists = True # FIX THIS
    if team_exists and participant_exists:
        return f"[PARTICPANT PAGE FOR {participant_name} ON TEAM {team_name}]"
    else:
        return "[404 PAGE]"

@app.route('/login', methods=('GET', 'POST'))
def login_flask():
    """
    Allows the user to log in or register an account.
    Returns:
        On error: the rendered login template with an error message filled in.
        On success: Redirects to the index page and stores the session data as cookies.
    """
    if request.method == 'POST':
        username = request.form['username'].replace(' ', '_')
        password = request.form['password']
        if not (username and password):
            return redirect('login')
        if request.form['mode'] == 'LOGIN':
            mode = 'LOGIN'
        elif request.form['mode'] == 'REGISTER':
            mode = 'REGISTER'
        else:
            return redirect('login')
        
        if mode == 'REGISTER':
            error = not register(username, password)
            if error:
                return render_template('login.j2', error="Username already exists.")
            token = begin_session(username)
            resp = make_response(redirect(f'/'))
            resp.set_cookie('token', token)
            return resp
        if mode == 'LOGIN':
            error = not login(username, password)
            if error:
                return render_template('login.j2', error="Incorrect username or password.")
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

@app.route('/logout', methods=('GET', 'POST'))
def logout():
    """
    Allows the user to log out.
    Returns:
        Redirects to the login page with cookies removed.

    """
    end_session()
    resp = make_response(redirect('login'))
    resp.set_cookie('token', '', expires=0)
    return resp

@app.route('/add_participant/<team_name>', methods=['POST', 'GET'])
def app_participant(team_name):
    '''
    Allows the user to add participants to their school
    '''
    print(team_name)
    if request.method == 'GET':
        return render_template('add_participant.j2')
    tournament_name = request.form['tournament_name']
    event_name = request.form['event_name']
    participant_name =  request.form['participant_name']
    placement = request.form['placement']
    add_participant(team_name, tournament_name, participant_name, placement, event_name)
    return render_template('add_participant.j2')

app.run(port=8022, debug=True)