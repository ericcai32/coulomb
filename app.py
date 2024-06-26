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
    """
    Allows the user to see a list of tournaments.
    Returns:
        The rendered tournament_list.j2 template.
    """
    tournaments = get_all_tournaments()
    is_logged = check_session()
    return render_template('tournament_list.j2', tournaments=tournaments, is_logged=is_logged)

@app.route('/new', methods=('GET', 'POST'))
def new():
    '''
    Create new tournament
    Returns:
        Redirecs to tournament page if creatoin was successful.
        Displays error if not
    '''
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
    '''
    Get the tournament page
    Params:
        tournament_name: Name of tournament

    Returns:
        tournament.j2 if tournament exists, 404.html if not
    '''
    if request.method == 'GET':
        tournament_exists = not check_exists(tournament_name)
        if tournament_exists:   
            is_to = False
            is_logged = check_session()
            joined = False
            tournament_results = read_table(tournament_name)
            if is_logged:
                token = request.cookies.get('token')
                user = get_session(token)
                is_to = verify_creator(user, tournament_name)
                joined = user in ([element for row in tournament_results for element in row])
            tournament_events = get_events(tournament_name)
            results = read_table(tournament_name)
            if len(results) > 0:
                joined = joined or results[0][1] != None
            return render_template('tournament.j2', tournament=tournament_name, events=tournament_events, data=tournament_results, is_to=is_to, is_logged=is_logged, joined=joined)
        else:
            return send_file("static/404.html")
    elif request.method == 'PUT':
        data = request.get_json()
        events = get_events(tournament_name)
        for team_results in data:
            new_data = {}
            team = team_results[0].replace(' ', '_')
            for i in range(len(events)):
                new_data[events[i]] = int(team_results[i + 1])
            if not update_row(tournament_name, team.strip(), new_data):
                return jsonify("fail")
            

        return jsonify("success")
    
@app.route('/tournaments/<tournament_name>', methods=['POST'])
def add_tournament(tournament_name):
    '''
    Add data to a pre-existing tournament
    Params:
        tournament_name: name of tournament
    '''
    token = request.cookies.get('token')
    add_to_table(tournament_name, get_session(token), {})
    return 'school added'

@app.route('/teams/<team_name>/', methods=('GET', 'POST'))
def team(team_name: str):
    '''
    The team page
    Params: 
        team_name: name of team

    Returns: 
        team.j2
    '''
    data = get_participated_events(team_name)
    is_logged = check_session()
    tournament_events = {}
    for tournament in data:
        tournament_events[tournament] = get_events(tournament)
    placements = get_placements(team_name)
    return render_template('team.j2', participated_events=data, user=team_name, tournament_events=tournament_events, placements=placements, is_logged=is_logged)

@app.route('/teams/<team_name>/<participant_name>')
def participant(team_name: str, participant_name: str):
    '''
    Gives the user the participant page
    Params:
        team_name: name of team
        participant_name: name of participant

    Returns:
        partcicpant.j2
    '''
    tournaments = [tournament_item[0] for tournament_item in get_participant_tournaments(team_name, participant_name)]
    placements = {}
    for tournament in tournaments:
        placements[tournament] = get_participant_data(team_name, tournament, participant_name)
    print(placements)
    return render_template('participants.j2', School=team_name, participated_events=tournaments, user=participant_name, dictionary=placements)

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

@app.route('/add_participant/', methods=['POST', 'GET'])
def app_participant():
    '''
    Allows the user to add participants to their school
    '''
    if request.method == 'GET':
        if not check_session():
            return redirect('/login')
        return render_template('add_participant.j2')
    events = request.form.getlist('event')
    token = request.cookies.get('token')
    user = get_session(token)
    tournament_name = request.form['tournament_name']
    event_name = request.form['event_name']
    participant_name =  request.form['participant_name']
    placement = request.form['placement']
    if not add_participant(user, tournament_name, participant_name, placement, event_name):
        return render_template('add_participant.j2', error="That result did not occur.")
    return render_template('add_participant.j2')

@app.route('/participant_list/<team_name>')
def get_participant_list(team_name):
    print(team_name)
    data = get_all_participants(team_name)
    return render_template('participant_list.j2', participant=data,team_name=team_name)

#Provides a 404 Error if sent a request that doesn't exist, or is invalid
@app.errorhandler(404)
def not_found(e):
    return send_file("static/404.html")

app.run(port=8022, debug=True)