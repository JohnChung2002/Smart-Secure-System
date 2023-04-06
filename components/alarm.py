from flask import Blueprint, g
from services.auth_middleware import auth_middleware
from services.mysql_service import MySQLService

alarm_bp = Blueprint('alarm', __name__)

@alarm_bp.route('/alarm')
@auth_middleware
def alarm():
    with g.dbconn:
        result = g.dbconn.get_by_id("configs", ["config"], ["Alarm Status"])
        status = "On" if result[1] == "Off" else "Off"
        status_message = f"Alarm {status}"
        g.ser.write(str.encode(status_message))
        g.dbconn.update("configs", ["value"], ["config"], [status, "Alarm Status"])
    return status_message, 200