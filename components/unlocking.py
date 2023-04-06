from flask import Blueprint, g
from services.auth_middleware import auth_middleware

unlock_bp = Blueprint('unlock', __name__)

@unlock_bp.route('/unlock')
@auth_middleware
def unlock():
    g.ser.write(b"Remote Unlock")
    return "Unlock", 200

@unlock_bp.route('/approve/<id>')
@auth_middleware
def approve(id):
    g.dbconn.update("unlock_logs", ["status"], ["unlock_id"], ["Success", id])
    g.ser.write(b"Approved")
    return "Approved", 200