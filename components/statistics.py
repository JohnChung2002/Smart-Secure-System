from flask import Blueprint, g, session
from services.auth_middleware import auth_middleware, admin_auth_middleware

stats_bp = Blueprint('statistics', __name__)

@stats_bp.route('/health_statistics')
@auth_middleware
def health_statistics():
    with g.dbconn:
        return get_user_health_statistics(g.dbconn, session["user_id"])
    
@stats_bp.route('/health_statistics/<id>')
@admin_auth_middleware
def health_statistics_by_id(id):
    with g.dbconn:
        return get_user_health_statistics(g.dbconn, id)
    
def get_user_health_statistics(conn, id):
    results = conn.get_user_health_statistics(id)
    index = list(map(lambda x: x[1].strftime('%Y-%m-%d'), results))
    weight_value = list(map(lambda x: round(x[2], 2), results))
    height_value = list(map(lambda x: round(x[3], 2), results))
    bmi_value = list(map(lambda x: round(x[4], 2), results))
    return {"index": index, "weight_value": weight_value, "height_value": height_value, "bmi_value": bmi_value}, 200