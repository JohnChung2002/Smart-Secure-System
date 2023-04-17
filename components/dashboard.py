from flask import Blueprint, g, session, render_template
from services.auth_middleware import auth_middleware, admin_auth_middleware

dashboard_bp = Blueprint('dashboard', __name__)

#Dashboard
@dashboard_bp.route('/')
@auth_middleware
def index():
    with g.dbconn:
        user = g.dbconn.get_by_id("user_details", ["user_id"], [session["user_id"]])
        recorded_data = {
            "weight":  user["weight"],
            "height":  user["height"],
        }
        alarm_status = g.dbconn.get_by_id("configs", ["config"], ["Alarm Status"])["value"]
        health_data = g.dbconn.get_user_average(session["user_id"])
        num_people = g.dbconn.get_by_id("configs", ["config"], ["People in Room"])["value"]
        if health_data["weight"] is not None and health_data["height"] is not None and health_data["bmi"] is not None:
            for key in health_data:
                health_data[key] = round(health_data[key], 2)
        else:
            health_data = None
        approval = g.dbconn.get_last_entry_by_id("unlock_logs", ["status"], "timestamp", ["Pending"])
    return render_template(
        'dashboard.html', 
        name=user["name"], 
        role=session["user_role"], 
        num_people=num_people,
        alarm_status=alarm_status,
        recorded_data=recorded_data,
        health_data=health_data,
        approval=approval
    ), 200

@dashboard_bp.route('/configs', methods=["GET"])
@admin_auth_middleware
def configs():
    with g.dbconn:
        name = g.dbconn.get_by_id("user_details", ["user_id"], [session["user_id"]])["name"]
        configs = g.dbconn.get_all("configs")
    return render_template(
        'configs.html', 
        name=name, 
        role=session["user_role"], 
        configs=configs
    ), 200

@dashboard_bp.route('/logs', methods=["GET"])
@admin_auth_middleware
def logs():
    with g.dbconn:
        name = g.dbconn.get_by_id("user_details", ["user_id"], [session["user_id"]])["name"]
    return render_template(
        'access_logs.html', 
        name=name, 
        role=session["user_role"], 
    ), 200

@dashboard_bp.route('/profile', methods=["GET"])
@auth_middleware
def profile():
    with g.dbconn:
        user = g.dbconn.get_by_id("user_details", ["user_id"], [session["user_id"]])
    return render_template(
        'profile.html', 
        name=user["name"], 
        role=session["user_role"], 
        user=user
    ), 200