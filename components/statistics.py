from flask import Blueprint, g, session, jsonify
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
    index = list(map(lambda x: x["date"].strftime('%Y-%m-%d'), results))
    weight_value = list(map(lambda x: round(x["avg_weight"], 2), results))
    height_value = list(map(lambda x: round(x["avg_height"], 2), results))
    bmi_value = list(map(lambda x: round(x["avg_bmi"], 2), results))
    return {"index": index, "weight_value": weight_value, "height_value": height_value, "bmi_value": bmi_value}, 200

@stats_bp.route('/access_logs')
def get_user_access_logs():
    with g.dbconn:
        return jsonify(g.dbconn.get_user_access_logs())