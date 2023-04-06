from flask import Flask, render_template, redirect, url_for, request, session, g
from services.mysql_service import MySQLService
from services.auth_middleware import auth_middleware
from threading import Thread
import serial
from components.authentication import auth_bp
from components.alarm import alarm_bp

sensor_config = {
    "alarm": ""
}

app = Flask(__name__)
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
ser.reset_input_buffer()
app.secret_key = "E2DAD46AF8783EB848129379F1328"

app.register_blueprint(auth_bp)
app.register_blueprint(alarm_bp)

def read_serial_input():
    while True:
        if (ser.in_waiting > 0):
            temp = ser.readline()
            print(temp)
            input = temp.decode('utf-8').rstrip().split("|")
            if (input[0] == "Entry" or input[0] == "Exit"):
                insert_entry_exit(input)
            if (input[0] == "Alarm"):
                update_alarm_status(input)
            if (input[0] == "Unlock"):
                insert_unlock_attempt(input)
            if (input[0] == "Request"):
                check_if_card_exists(input[1])
            if (input[0] == "Approval"):
                print("Yes")

def check_if_card_exists(card_id):
    db = MySQLService('localhost', 'pi', 'pi', 'smart_lock_system')
    with db:
        result = db.get_by_id("user_details", ["card_id"], [card_id])
        if (result is None):
            ser.write(b"Invalid")
        else:
            temp = f"Exists|{result[0]}|{result[1]}|{result[6]}"
            ser.write(str.encode(temp))

def insert_entry_exit(sensor_data):
    db = MySQLService('localhost', 'pi', 'pi', 'smart_lock_system')
    with db:
        last_unlock = db.get_last_entry("unlock_logs", "unlock_id")
        db.insert("in_out_logs", ["unlock_id", "type", "weight", "height", "bmi"], [last_unlock[0]] + sensor_data)

def update_alarm_status(sensor_data):
    db = MySQLService('localhost', 'pi', 'pi', 'smart_lock_system')
    with db:
        db.update("config", ["value", "config"], ["alarm_status"], [sensor_data[1]])

def insert_unlock_attempt(sensor_data):
    db = MySQLService('localhost', 'pi', 'pi', 'smart_lock_system')
    if len(sensor_data) == 3:
        sensor_data.append(None)
    with db:
        db.insert("unlock_logs", ["type", "status", "user_id"], [sensor_data[1], sensor_data[2], sensor_data[3]])

#Dashboard
@app.route('/')
@auth_middleware
def index():
    users = [
        {'username': 'Alice'},
        {'username': 'Bob'},
        {'username': 'Charlie'},
    ]
    return render_template('dashboard.html', users=users)



@app.route('/unlock')
def unlock():
    g.ser.write(b"Remote Unlock")
    return "Unlock", 200

def request_has_connection():
    return (
        hasattr(g, 'dbconn') and g.dbconn is not None
    ) and (
        hasattr(g, 'ser') and g.ser is not None
    )

@app.before_request
def get_request_connection():
    if not request_has_connection():
        g.dbconn = MySQLService('localhost', 'pi', 'pi', 'smart_lock_system')
        g.ser = ser

@app.teardown_request
def close_db_connection(ex):
    if request_has_connection():
        dbconn = g.pop('dbconn', None)
        dbconn.close()
        g.pop("ser", None)

sensor_thread = Thread(target=read_serial_input)
sensor_thread.daemon = True
sensor_thread.start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
