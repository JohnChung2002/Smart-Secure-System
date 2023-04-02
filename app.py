from flask import Flask, render_template, session, g
from services.mysql_service import MySQLService
import serial

app = Flask(__name__)
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
ser.reset_input_buffer()
app.secret_key = "E2DAD46AF8783EB848129379F1328"

#Dashboard
@app.route('/')
def index():
    users = [
        {'username': 'Alice'},
        {'username': 'Bob'},
        {'username': 'Charlie'}
    ]
    return render_template('dashboard.html', users=users)

@app.route('/alarm-mode-on')
def alarm_mode_on():
    ser.write(b"Alarm On")
    return "Alarm On", 200

@app.route('/alarm-mode-off')
def alarm_mode_off():
    ser.write(b"Alarm Off")
    return "Alarm Off", 200

def request_has_connection():
    return hasattr(g, 'dbconn')

@app.before_request
def get_request_connection():
    if not request_has_connection():
        g.dbconn = MySQLService('localhost', 'pi', 'pi', 'sensor_db')

@app.teardown_request
def close_db_connection(ex):
    if request_has_connection():
        g.dbconn.close()


if __name__ == "__main__":
    app.run()