from flask import Flask, send_file, request, redirect, render_template, Blueprint, jsonify, make_response
import redis
from uuid import uuid4, UUID
import database

app = Flask(__name__)

@app.route('/')
def index():
    return "[LIST OF TOURNAMENTS]"

@app.route('/new', methods=('GET', 'POST'))
def new():
    return "[TOURNAMENT CREATION]"

@app.route('/tournaments/<tournament_name>')
def tournament(tournament_name: str):
    tournament_exists = True # FIX THIS
    if tournament_exists:
        return f"[TOURNAMENT PAGE FOR {tournament_name}]"
    else:
        return "[404 PAGE]"

@app.route('/teams/<team_name>', methods=('GET', 'POST'))
def team(team_name: str):
    team_exists = True # FIX THIS
    if team_exists:
        return f"[TEAM PAGE FOR {team_name}]"
    else:
        return "[404 PAGE]"

@app.route('/teams/<team_name>/<participant_name>')
def participant(team_name: str, participant_name: str):
    team_exists = True # FIX THIS
    participant_exists = True # FIX THIS
    if team_exists and participant_exists:
        return f"[PARTICPANT PAGE FOR {participant_name} ON TEAM {team_name}]"
    else:
        return "[404 PAGE]"

@app.route('/login', methods=('GET', 'POST'))
def login():
    return "[LOGIN PAGE]"

app.run(port=8022)