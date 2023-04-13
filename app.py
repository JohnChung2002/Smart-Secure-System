from flask import Flask, render_template, redirect, url_for, request, session, g
from services.mysql_service import MySQLService
from services.auth_middleware import auth_middleware
from threading import Thread
import serial
from components.authentication import auth_bp
from components.alarm import alarm_bp
from components.unlocking import unlock_bp
from components.statistics import stats_bp
from components.configs import configs_bp
from components.dashboard import dashboard_bp
from components.backend_processing import insert_entry_exit, update_alarm_status, insert_unlock_attempt, update_unlock_attempt, check_if_card_exists

app = Flask(__name__)
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
ser.reset_input_buffer()
app.secret_key = "E2DAD46AF8783EB848129379F1328"

app.register_blueprint(auth_bp)
app.register_blueprint(alarm_bp)
app.register_blueprint(unlock_bp)
app.register_blueprint(stats_bp)
app.register_blueprint(configs_bp)
app.register_blueprint(dashboard_bp)

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
                insert_unlock_attempt(input, ser)
            if (input[0] == "Request"):
                check_if_card_exists(input[1], ser)
            if (input[0] == "Update"):
                update_unlock_attempt(input, ser)

sensor_thread = Thread(target=read_serial_input)
sensor_thread.daemon = True
sensor_thread.start()

@app.errorhandler(404)
def page_not_found(e):
    return ('''
    <body><h1>Not Found</h1>
    <p>The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.</p>
    </body>
    '''), 404

def request_has_connection():
    return (
        ("dbconn" in g) and (g.dbconn is not None)
    ) and (
        ("ser" in g) and (g.ser is not None)
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
        if (dbconn is not None):
            dbconn.close()
        g.pop("ser", None)

@app.template_filter('config_name_to_id')
def config_name_to_id(config_name):
    return config_name.lower().replace(" ", "-").replace("(", "9").replace(")", "0")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
