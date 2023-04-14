from flask import Blueprint, g, session, render_template
from services.auth_middleware import auth_middleware, admin_auth_middleware

dashboard_bp = Blueprint('dashboard', __name__)

#Dashboard
@dashboard_bp.route('/')
@auth_middleware
def index():
    with g.dbconn:
        user = g.dbconn.get_by_id("user_details", ["user_id"], [session["user_id"]])
        alarm_status = g.dbconn.get_by_id("configs", ["config"], ["Alarm Status"])
        health_data = g.dbconn.get_user_average(session["user_id"])
        num_people = g.dbconn.get_by_id("configs", ["config"], ["People in Room"])[1]
        if health_data[0] is not None and health_data[1] is not None and health_data[2] is not None:
            health_data = {
                "weight": round(health_data[0], 2),
                "height": round(health_data[1], 2),
                "bmi": round(health_data[2], 2)
            }
        else:
            health_data = None
        approval = g.dbconn.get_last_entry_by_id("unlock_logs", ["status"], "timestamp", ["Pending"])
    return render_template(
        'dashboard.html', 
        name=user[1], 
        role=session["user_role"], 
        num_people=num_people,
        alarm_status=alarm_status[1],
        health_data=health_data,
        approval=approval
    ), 200

@dashboard_bp.route('/configs', methods=["GET"])
@admin_auth_middleware
def configs():
    with g.dbconn:
        user = g.dbconn.get_by_id("user_details", ["user_id"], [session["user_id"]])
        configs = g.dbconn.get_all("configs")
    return render_template(
        'configs.html', 
        name=user[1], 
        role=session["user_role"], 
        configs=configs
    ), 200

@dashboard_bp.route('/logs', methods=["GET"])
@admin_auth_middleware
def logs():
    with g.dbconn:
        user = g.dbconn.get_by_id("user_details", ["user_id"], [session["user_id"]])
    return render_template(
        'access_logs.html', 
        name=user[1], 
        role=session["user_role"], 
    ), 200