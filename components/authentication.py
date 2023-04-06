from flask import Blueprint, render_template, redirect, url_for, request, session
from services.mysql_service import MySQLService
from argon2 import PasswordHasher

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET'])
def login():
    if "username" in session:
        return redirect(url_for('index'))
    return render_template('login.html', message="")

@auth_bp.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')

    db = MySQLService('localhost', 'pi', 'pi', 'smart_lock_system')
    with db:
        ph = PasswordHasher()
        result = db.get_by_id("user_accounts", ["username"], [username])
        if result is not None:
            try:
                if ph.verify(result[2], password):
                    session["username"] = username
                return redirect(url_for('index'))
            except:
                pass
    return render_template('login.html', message="Invalid username or password")