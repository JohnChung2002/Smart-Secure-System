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
        if health_data is not None:
            health_data = {
                "weight": round(health_data[0], 2),
                "height": round(health_data[1], 2),
                "bmi": round(health_data[2], 2)
            }
        approval = g.dbconn.get_last_entry_by_id("unlock_logs", ["status"], "timestamp", ["Pending"])
    return render_template(
        'dashboard.html', 
        name=user[1], 
        role=session["user_role"], 
        alarm_status=alarm_status[1],
        health_data=health_data,
        approval=approval
    ), 200

@dashboard_bp.route('/configs')
@admin_auth_middleware
def configs():
    with g.dbconn:
        configs = g.dbconn.get_all("configs")
    return render_template('configs.html', configs=configs), 200