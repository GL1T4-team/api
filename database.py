import psycopg2, json

class DB:
    def __init__(self):
        self.conn = psycopg2.connect(
            host="81.19.135.21",
            database="default_db",
            user="gen_user",
            password="OQ;Zt9JFxEXDdT"
        )

        self.cur = self.conn.cursor()

    def close(self):
        self.cur.close()
        self.conn.close()

    def upload_data(self, rows:list):
        
        sql = "INSERT INTO flights (flight_id, uav_type, flight_region, departure_coords, arrival_coords, flight_date, start_time, end_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"

        self.cur.executemany(sql, rows)
        self.conn.commit()

        self.close()