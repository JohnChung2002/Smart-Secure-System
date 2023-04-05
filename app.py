from flask import Flask, render_template, session, g
from services.mysql_service import MySQLService
from threading import Thread
import serial

latest_sensor_data = []

app = Flask(__name__)
# ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
# ser.reset_input_buffer()
app.secret_key = "E2DAD46AF8783EB848129379F1328"

def read_serial_input():
    while True:
        #read serial input from arduino if not null
        if (ser.in_waiting > 0):
            input = ser.readline().decode('utf-8').rstrip().split("|")
            if (input[0] == "Entry" or input[0] == "Exit"):
                update_entry_exit(input)
            if (input[0] == "Alarm"):
                update_alarm_status(input)

def update_entry_exit(sensor_data):
    #update entry exit in db
    db = MySQLService('localhost', 'pi', 'pi', 'sensor_db')
    with db:
        db.insert()

def update_alarm_status(sensor_data):
    #update alarm status in db
    db = MySQLService('localhost', 'pi', 'pi', 'sensor_db')

#Dashboard
@app.route('/')
def index():
    users = [
        {'username': 'Alice'},
        {'username': 'Bob'},
        {'username': 'Charlie'},
    ]
    print(len(latest_sensor_data))
    return render_template('dashboard.html', users=users)

@app.route('/alarm-mode-on')
def alarm_mode_on():
    #ser.write(b"Alarm On")
    return "Alarm On", 200

@app.route('/alarm-mode-off')
def alarm_mode_off():
    #ser.write(b"Alarm Off")
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

sensor_thread = Thread(target=read_serial_input)
sensor_thread.daemon = True
sensor_thread.start()

if __name__ == "__main__":
    app.run()