from services.mysql_service import MySQLService
import serial

device = '/dev/ttyACM0'
arduino = serial.Serial(device, 9600)

while True:
    db = MySQLService('localhost', 'pi', 'pi', 'sensor_db')

    while (arduino.in_waiting == 0):
        pass
    try:
        line = arduino.readline()
        valueTemp = int(line[0:])
        print(valueTemp)

        with db:
            db.insert("tempLog", ["temperature"], ["%s"], (valueTemp))
    except:
        pass
