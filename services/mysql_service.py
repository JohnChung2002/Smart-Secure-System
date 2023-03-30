import mysql.connector

class MySQLService:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

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

    def get_all(self, table_name):
        cursor = self.connection.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        result = cursor.fetchall()
        cursor.close()
        return result

    def get_by_id(self, table_name, id):
        cursor = self.connection.cursor()
        cursor.execute(f"SELECT * FROM {table_name} WHERE id = {id}")
        result = cursor.fetchone()
        cursor.close()
        return result

    def insert(self, table_name, field_names, identifiers, data):
        cursor = self.connection.cursor()
        cursor.execute(f"INSERT INTO {table_name} ({', '.join(field_names)}) VALUES ({', '.join(identifiers)})", data)
        self.connection.commit()
        cursor.close()

    def update(self, table_name, data):
        cursor = self.connection.cursor()
        cursor.execute(f"UPDATE {table_name} SET name = %s, email = %s, password = %s WHERE id = %s", data)
        self.connection.commit()
        cursor.close()

    def delete(self, table_name, id):
        cursor = self.connection.cursor()
        cursor.execute(f"DELETE FROM {table_name} WHERE id = {id}")
        self.connection.commit()
        cursor.close()