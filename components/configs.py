from flask import Blueprint, g, session, request
from services.auth_middleware import auth_middleware, admin_auth_middleware
from string import capwords

configs_bp = Blueprint('configs', __name__)

@configs_bp.route('/configs', methods=["POST"])
@admin_auth_middleware
def configs_post():
    data= request.get_json()
    if request.data is None:
        return "Invalid data", 400
    if "config" not in request.data or "value" not in request.data:
        return "Invalid data", 400
    with g.dbconn:
        data["config"] = data["config"].replace("-", " ").replace("9", "(").replace("0", ")").capwords()
        count = g.dbconn.update_config(request.data["config"], request.data["value"])
        if count == 0:
            return "Invalid config", 400
    return "Success", 200



@configs_bp.route('/profile')
@auth_middleware
def profile():
    with g.dbconn:
        result = g.dbconn.get_by_id("user_accounts", ["user_id"], [session["user_id"]])
        return {"username": result[1], "email": result[4], "role": result[3]}, 200