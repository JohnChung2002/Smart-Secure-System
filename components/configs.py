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

@configs_bp.route('/approval', methods=["GET"])
@auth_middleware
def approval_get():
    with g.dbconn:
        approval = g.dbconn.get_last_entry_by_id("unlock_logs", ["status"], "timestamp", ["Pending"])
    if approval is None:
        return {
            "status": False,
            "message": "No pending approvals"
        }, 200
    unlock_id = approval["unlock_id"]
    return {
        "status": True,
        "message": "Pending approval",
        "unlock_id": unlock_id,
        "script": '''
            $(function () {
                $('#alarmButton').click(function () {
                    $.get('/alarm', function (data) {
                        $('#alarm_status').text(data);
                    });
                });
                $('#approveButton').click(function () {
                    $.get('/approve/{unlock_id}', function (data) {
                        $('#approvalAlert').addClass("d-none");
                        $("#approveButton").off('click');  
                    });
                });
                $('#rejectButton').click(function () {
                    $.get('/reject/{unlock_id}', function (data) {
                        $('#approvalAlert').addClass("d-none");
                        $("#rejectButton").off('click'); 
                    });
                });
            });
        '''
    }, 200
