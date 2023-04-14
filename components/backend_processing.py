from services.mysql_service import MySQLService

def check_if_card_exists(card_id, ser):
    db = MySQLService('localhost', 'pi', 'pi', 'smart_lock_system')
    with db:
        result = db.get_by_id("user_details", ["card_id"], [card_id])
        if (result is None):
            ser.write(b"Invalid")
        else:
            temp = f"Exists|{result['user_id']}|{result['name']}|{result['weight']}|{result['card_id']}"
            ser.write(str.encode(temp))

def insert_entry_exit(sensor_data):
    db = MySQLService('localhost', 'pi', 'pi', 'smart_lock_system')
    with db:
        last_unlock = db.get_last_entry("unlock_logs", "unlock_id")
        db.insert("in_out_logs", ["unlock_id", "type", "weight", "height", "bmi"], [last_unlock["unlock_id"]] + sensor_data)

def update_alarm_status(sensor_data):
    db = MySQLService('localhost', 'pi', 'pi', 'smart_lock_system')
    with db:
        db.update("configs", ["value", "config"], ["alarm_status"], [sensor_data[1]])

def insert_unlock_attempt(sensor_data, ser):
    db = MySQLService('localhost', 'pi', 'pi', 'smart_lock_system')
    if len(sensor_data) == 3:
        sensor_data.append(None)
        sensor_data.append(None)
    with db:
        db.insert("unlock_logs", ["type", "status", "user_id", "key_type"], [sensor_data[1], sensor_data[2], sensor_data[3], sensor_data[4]])
        unlock_id = db.get_last_entry("unlock_logs", "unlock_id")["unlock_id"]
        ser.write(str.encode(str(unlock_id)))

def update_unlock_attempt(sensor_data):
    db = MySQLService('localhost', 'pi', 'pi', 'smart_lock_system')
    with db:
        db.update("unlock_logs", ["status"], ["unlock_id"], [sensor_data[1], sensor_data[2]])

def update_person_in_room(sensor_data):
    db = MySQLService('localhost', 'pi', 'pi', 'smart_lock_system')
    with db:
        result = db.get_by_id("configs", ["config"], ["People in Room"])
        count = int(sensor_data) + int(result["value"])
        if count < 0:
            count = 0
        db.update("configs", ["value"], ["config"], [count, "People in Room"])

def intialise_data(ser):
    db = MySQLService('localhost', 'pi', 'pi', 'smart_lock_system')
    with db:
        result = db.get_all("configs")
    for config in result:
        if config["config"] == "Door Height (cm)":
            ser.write(str.encode(f"DoorHeightUpdate|{result['value']}"))
        elif config["config"] == "Weight Threshold (kg)":
            ser.write(str.encode(f"WeightThresholdUpdate|{result['value']}"))