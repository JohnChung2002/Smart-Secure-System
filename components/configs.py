from flask import Blueprint, g, session
from services.auth_middleware import auth_middleware, admin_auth_middleware

configs_bp = Blueprint('configs', __name__)

@configs_bp.route('/profile')
@auth_middleware
def profile():
    with g.dbconn:
        result = g.dbconn.get_by_id("user_accounts", ["user_id"], [session["user_id"]])
        return {"username": result[1], "email": result[4], "role": result[3]}, 200