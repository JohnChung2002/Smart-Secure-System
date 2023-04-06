from flask import Blueprint, render_template, redirect, url_for, request, session
from flask import g
from argon2 import PasswordHasher
from services.auth_middleware import auth_middleware

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET'])
def login():
    if "user_id" in session and "user_role" in session:
        return redirect("/")
    return render_template('login.html', message=""), 200

@auth_bp.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    
    print(g.dbconn)
    with g.dbconn:
        ph = PasswordHasher()
        result = g.dbconn.get_by_id("user_accounts", ["username"], [username])
        if result is not None:
            try:
                if ph.verify(result[2], password):
                    session["user_id"] = result[0]
                    session["user_role"] = result[3]
                return redirect("/"), 200
            except:
                pass
    return render_template('login.html', message="Invalid username or password"), 401

@auth_bp.route('/logout')
@auth_middleware
def logout():
    session.pop('user_id', None)
    session.pop('user_role', None)
    return redirect(url_for('auth.login')), 200