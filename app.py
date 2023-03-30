from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, g
from services.mysql_service import MySQLService

app = Flask(__name__)

#Dashboard
@app.route('/')
def index():
    users = [
        {'username': 'Alice'},
        {'username': 'Bob'},
        {'username': 'Charlie'}
    ]
    return render_template('dashboard.html', users=users)

def request_has_connection():
    return hasattr(g, 'dbconn')

@app.before_request
def get_request_connection():
    if not request_has_connection():
        g.dbconn = MySQLService('localhost', 'pi', 'pi', 'sensor_db').connect()

@app.teardown_request
def close_db_connection(ex):
    if request_has_connection():
        g.dbconn.close()


if __name__ == "__main__":
    app.run()