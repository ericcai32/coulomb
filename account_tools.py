import hashlib
import os
import redis
import random
import string
import sqlite3
from uuid import uuid4

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def begin_session(username: str) -> str:
    """
    Begins the user session by storing the token in the Redis database.
    Args:
        username: The user's username.
    Returns:
        The session token.
    """
    session_token = str(uuid4())
    r.set('token', session_token)
    r.set(session_token, username)
    return session_token

def check_session() -> int:
    """
    Checks if there is a currently active session.
    Returns:
        0 if the key does not exist or 1 if it does.
    """
    print(r.get('token'))
    return r.exists('token')

def get_session(token: str) -> str:
    """
    Gets the currently logged in user's username.
    Args:
        token: the token.
    Returns:
        The user's username.
    """
    username = r.get(token)
    return username

def end_session():
    """
    Logs the user out of the current session.
    """
    token = r.get('token')
    if r.exists('token'):
        r.delete(token)
        r.delete('token')

# connection = sqlite3.connect('users.db', check_same_thread=False)

# cursor = connection.cursor()
# cursor.execute("CREATE TABLE IF NOT EXISTS accounts(rowid INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL, password TEXT, salt TEXT)")
# cursor.execute("CREATE TABLE IF NOT EXISTS profiles(rowid INTEGER PRIMARY KEY AUTOINCREMENT, userid INTEGER NOT NULL, fname TEXT, lname TEXT, avatar TEXT)")
# connection.commit()

# def protect_password(password: str) -> str:
#     """
#     Hashes the password with the salt.
#     Args:
#         password: the password in plaintext.
#     Returns:
#         The hashed password and the salt.
#     """
#     salt = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
#     salted_password = password + salt
#     hash = hashlib.sha256()
#     hash.update(salted_password.encode())
#     password_hash = hash.hexdigest()
#     return password_hash, salt

# def register_user(username: str, password:str) -> str:
#     """
#     Registers a new account by adding them to the databases.
#     Args:
#         username: the new user's username.
#         password: the new user's password in plaintext.
#     Returns:
#         An error message on error or an empty string on success.
#     """
#     username_exists = cursor.execute(f"SELECT EXISTS(SELECT username FROM accounts WHERE username = '{username}')").fetchone()[0]
#     if username_exists:
#         return ("Account already exists. The username must be unique.")
#     else:
#         new_password, salt = protect_password(password)
#         cursor.execute(f"INSERT INTO accounts (username, password, salt) VALUES('{username}', '{new_password}', '{salt}')")
#         userid = cursor.execute("SELECT rowid FROM accounts ORDER BY rowid DESC LIMIT 1").fetchone()[0]
#         print(userid)
#         cursor.execute(f"INSERT INTO profiles (userid) VALUES({userid})")
#         print(cursor.execute("SELECT * from accounts").fetchall())
#         print(cursor.execute("SELECT * from profiles").fetchall())
#         connection.commit()
#         return ''

# def repeat_hash(password: str, salt:str) -> str:
#     """
#     Hashes a password and salt.
#     Args:
#         password: the password in plaintext.
#         salt: the salt to be used.
#     Returns:
#         The hashed password.
#     """
#     salted_password = password + salt
#     hash = hashlib.sha256()
#     hash.update(salted_password.encode())
#     password_hash = hash.hexdigest()
#     return password_hash

# def check_login(username: str, password: str) -> str:
#     """
#     Checks to see if a password is correct on login.
#     Args:
#         username: the username of the user trying to log in.
#         password: the password the user is logging in with.
#     Returns:
#         An error message on error or an empty string on success.
#     """
#     username_exists = cursor.execute(f"SELECT EXISTS(SELECT username FROM accounts WHERE username = '{username}')").fetchone()[0]
#     if username_exists:
#         password_hash, salt = cursor.execute(f"SELECT password, salt FROM accounts WHERE username = '{username}'").fetchone()
#         try_hash = repeat_hash(password, salt)
#         if password_hash == try_hash:
#             return ''
#     return("Username or password was incorrect.")

# def list_profiles():
#     """
#     Gets a list of accounts from the accounts table.
#     Returns:
#         The output of a SQLite operation that displays all existing usernames.

#     """
#     users = cursor.execute("SELECT username FROM accounts").fetchall()
#     return users

# def get_profile(username: str):
#     """
#     Gets the profile information about a certain user.
#     Args:
#         username: the user whoose information is needed.
#     Returns:
#         the user's first name, last name, and avatar file path.
#     """
#     userid = cursor.execute(f"SELECT rowid FROM accounts WHERE username = '{username}'").fetchone()[0]
#     fname, lname, avatar = cursor.execute(f"SELECT fname, lname, avatar FROM profiles WHERE userid = {userid}").fetchone()
#     return fname, lname, avatar

# def update_profile(username: str, data: dict):
#     """
#     Updates a user's profile data.
#     Args:
#         username: the username of the user being updated.
#         data: the values that the user wishes to update their profile with.
#     Returns:
#         an error message on error or nothing on success.
#     """
#     password_incorrect = check_login(username, data['oldPassword'])
#     if not password_incorrect:
#         userid = cursor.execute(f"SELECT rowid FROM accounts WHERE username = '{username}'").fetchone()[0]
#         if data['firstName']:
#             cursor.execute(f"UPDATE profiles SET fname = '{data['firstName']}' WHERE userid = {userid}")
#         if data['lastName']:
#             cursor.execute(f"UPDATE profiles SET lname = '{data['lastName']}' WHERE userid = {userid}")
#         if data['avatar']:
#             filename = os.path.basename(data['avatar'])
#             cursor.execute(f"UPDATE profiles SET avatar = '/static/avatars/{username}_avatar.png' WHERE userid = {userid}")
#         if data['newPassword']:
#             hashed_password, salt = protect_password(data['newPassword'])
#             cursor.execute(f"UPDATE accounts SET password = '{hashed_password}', salt = '{salt}' WHERE username = '{username}'")
#         print(cursor.execute("SELECT * from accounts").fetchall())
#         print(cursor.execute("SELECT * from profiles").fetchall())
#         connection.commit()
#     else:
#         return password_incorrect

# def delete_profile(username: str, data: str):
#     """
#     Deletes the user's profile.
#     Args:
#         username: the username of the user being deleted.
#         data: data including the confirmation password for deletion.
#     Returns
#         an error message on error or nothing on success.
#     """
#     password_incorrect = check_login(username, data['oldPassword'])
#     if not password_incorrect:
#         userid = cursor.execute(f"SELECT rowid FROM accounts WHERE username = '{username}'").fetchone()[0]
#         cursor.execute(f"DELETE FROM accounts WHERE rowid = {userid}")
#         cursor.execute(f"DELETE FROM profiles WHERE userid = {userid}")
#         print(cursor.execute("SELECT * from accounts").fetchall())
#         print(cursor.execute("SELECT * from profiles").fetchall())
#         connection.commit()
#         end_session()
#     else:
#         return password_incorrect