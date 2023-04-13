from flask import session, redirect, url_for
from functools import wraps

def auth_middleware(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        if 'user_id' not in session and 'user_role' not in session:
            # user is not authenticated, redirect to login page
            return redirect(url_for('auth.login'))
        # user is authenticated, proceed to request handling
        return func(*args, **kwargs)
    return wrapper_func

def admin_auth_middleware(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        if 'user_id' not in session and 'user_role' not in session:
            # user is not authenticated, redirect to login page
            return redirect(url_for('auth.login'))
        if session['user_role'] != 'Admin':
            # user is not admin, redirect to home page
            return redirect("/")
        # user is authenticated, proceed to request handling
        return func(*args, **kwargs)
    return wrapper_func