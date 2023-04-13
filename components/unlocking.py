from flask import Blueprint, g
from services.auth_middleware import auth_middleware, admin_auth_middleware

unlock_bp = Blueprint('unlock', __name__)

@unlock_bp.route('/unlock')
@admin_auth_middleware
def unlock():
    g.ser.write(b"Remote Unlock")
    return "Unlock", 200

@unlock_bp.route('/approve/<id>')
@auth_middleware
def approve(id):
    with g.dbconn:
        data = g.dbconn.get_by_id("unlock_logs", ["unlock_id"], [id])
        if data is None:
            return "Invalid unlock id", 400
        if data[3] != "Pending":
            return "Invalid unlock id", 400
        g.dbconn.update("unlock_logs", ["status"], ["unlock_id"], ["Success", id])
    g.ser.write(b"Approved")
    return "Approved", 200

@unlock_bp.route('/reject/<id>')
@auth_middleware
def reject(id):
    with g.dbconn:
        data = g.dbconn.get_by_id("unlock_logs", ["unlock_id"], [id])
        if data is None:
            return "Invalid unlock id", 400
        if data[3] != "Pending":
            return "Invalid unlock id", 400
        g.dbconn.update("unlock_logs", ["status"], ["unlock_id"], ["Failed", id])
    g.ser.write(b"Rejected")
    return "Rejected", 200