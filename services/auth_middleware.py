from flask import session, redirect, url_for

def auth_middleware(func):
    def wrapper(*args, **kwargs):
        if 'username' not in session:
            # user is not authenticated, redirect to login page
            return redirect(url_for('login'))
        # user is authenticated, proceed to request handling
        return func(*args, **kwargs)
    return wrapper