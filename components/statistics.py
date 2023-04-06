from flask import Blueprint, g, session
from services.auth_middleware import auth_middleware, admin_auth_middleware

stats_bp = Blueprint('statistics', __name__)

@stats_bp.route('/health_statistics')
@auth_middleware
def health_statistics():
    with g.dbconn as db:
        results = db.get_user_health_statistics(session["user_id"])
        index = list(map(lambda x: x[1], results))
        weight_value = list(map(lambda x: x[2], results))
        height_value = list(map(lambda x: x[3], results))
        bmi_value = list(map(lambda x: x[4], results))
        return {"index": index, "weight_value": weight_value, "height_value": height_value, "bmi_value": bmi_value}, 200
    
@stats_bp.route('/health_statistics/<id>')
@admin_auth_middleware
def health_statistics_by_id(id):
    with g.dbconn as db:
        results = db.get_user_health_statistics(id)
        index = list(map(lambda x: x[1], results))
        weight_value = list(map(lambda x: x[2], results))
        height_value = list(map(lambda x: x[3], results))
        bmi_value = list(map(lambda x: x[4], results))
        return {"index": index, "weight_value": weight_value, "height_value": height_value, "bmi_value": bmi_value}, 200