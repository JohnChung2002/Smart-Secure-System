from flask import Blueprint, render_template, redirect, url_for, request, session
from services.mysql_service import MySQLService
from argon2 import PasswordHasher
from services.auth_middleware import auth_middleware

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET'])
def login():
    if "username" in session:
        return redirect("/")
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
                return redirect("/")
            except:
                pass
    return render_template('login.html', message="Invalid username or password")

@auth_bp.route('/logout')
@auth_middleware
def logout():
    session.pop('username', None)
    return redirect(url_for('auth.login'))