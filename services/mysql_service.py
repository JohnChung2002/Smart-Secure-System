import mysql.connector

class MySQLService:
    def __init__(self, host: str, user: str, password: str, database: str):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def connect(self):
        self.connection = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )

    def close(self):
        if self.connection is not None:
            self.connection.close()

    def __enter__(self):
        self.connect()
    
    def __exit__(self, type, value, traceback):
        self.close()

    def join_param_string(self, param_list:list):
        return ', '.join([('%s = %%s' %(key)) for key in param_list])

    def get_all(self, table_name: str):
        cursor = self.connection.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        result = cursor.fetchall()
        cursor.close()
        return result

    def get_by_id(self, table_name: str, primary_fields: list, data: list):
        cursor = self.connection.cursor()
        print(f"SELECT * FROM {table_name} WHERE {self.join_param_string(primary_fields)}")
        cursor.execute(f"SELECT * FROM {table_name} WHERE {self.join_param_string(primary_fields)}", data)
        result = cursor.fetchone()
        cursor.close()
        return result

    def insert(self, table_name: str, fields: list, data: list):
        cursor = self.connection.cursor()
        cursor.execute(f"INSERT INTO {table_name} ({', '.join(fields)}) VALUES ({', '.join(['%s'] * len(fields))})", data)
        self.connection.commit()
        cursor.close()

    def update(self, table_name: str, modifying_fields: list, primary_fields: list, data: list):
        cursor = self.connection.cursor()
        cursor.execute(f"UPDATE {table_name} SET {self.join_param_string(modifying_fields)} WHERE {self.join_param_string(primary_fields)}", data)
        self.connection.commit()
        cursor.close()

    def delete_by_id(self, table_name: str, primary_fields: list, data: list):
        cursor = self.connection.cursor()
        cursor.execute(f"DELETE FROM {table_name} WHERE {self.join_param_string(primary_fields)}", data)
        self.connection.commit()
        cursor.close()

    def get_last_entry(self, table_name: str, primary_field: str):
        cursor = self.connection.cursor()
        cursor.execute(f"SELECT * FROM {table_name} ORDER BY {primary_field} DESC LIMIT 1")
        result = cursor.fetchone()
        cursor.close()
        return result
