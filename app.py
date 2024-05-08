from flask import Flask, send_file, request, redirect, render_template, Blueprint, jsonify, make_response
import redis
import sqlite3
from uuid import uuid4, UUID
import database

app = Flask(__name__)

@app.route('/', methods=('GET', 'POST'))
def index():
    return "[HOME PAGE]"

app.run(port=8022)