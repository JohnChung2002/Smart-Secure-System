from flask import Blueprint, g, session, request
from services.auth_middleware import auth_middleware, admin_auth_middleware
from string import capwords

configs_bp = Blueprint('configs', __name__)

@configs_bp.route('/configs', methods=["POST"])
@admin_auth_middleware
def configs_post():
    data = request.get_json()
    if data is None:
        return "Invalid data", 400
    if "config" not in data or "value" not in data:
        return "Invalid data", 400
    with g.dbconn:
        data["config"] = capwords(data["config"].replace("-", " ").replace("9", "(").replace("0", ")"))
        count = g.dbconn.update_config(data["config"], data["value"])
        if count == 0:
            return "Invalid config", 400
        if data["config"] == "Door Height (cm)":
            g.ser.write(str.encode(f"DoorHeightUpdate|{data['value']}"))
        elif data["config"] == "Weight Threshold (kg)":
            g.ser.write(str.encode(f"WeightThresholdUpdate|{data['value']}"))
    return "Success", 200

@configs_bp.route('/profile', methods=["POST"])
@auth_middleware
def profile_post():
    data = request.get_json()
    if data is None:
        return "Invalid data", 400
    if "field" not in data or "value" not in data:
        return "Invalid data", 400
    if data["field"] not in ["name", "date_of_birth", "weight", "height", "card_id"]:
        return "Invalid data", 400
    with g.dbconn:
        count = g.dbconn.update_profile(session["user_id"], data["field"], data["value"])
        if count == 0:
            return "Invalid data", 400
    return "Success", 200