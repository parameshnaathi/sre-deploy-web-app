import psycopg2
from datetime import datetime

# Hard-code your DB credentials for local testing
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "postgres"

def log_command_to_postgres(username, command):
    print("log_command_to_postgres called")
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cur = conn.cursor()
        print("Connected to DB")
        cur.execute('''
        CREATE TABLE IF NOT EXISTS deployment_command_logs (
            id SERIAL PRIMARY KEY,
            username TEXT NOT NULL,
            command TEXT NOT NULL,
            timestamp TIMESTAMP NOT NULL
        )
        ''')
        print("Table creation checked/executed")
        cur.execute(
            """
            INSERT INTO deployment_command_logs (username, command, timestamp)
            VALUES (%s, %s, %s)
            """,
            (username, command, datetime.now())
        )
        print("Log inserted")
        conn.commit()
        cur.close()
        conn.close()
        print("DB connection closed")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Test values
    log_command_to_postgres("testuser", "dradis freeze nhp production_a")
    print("Done.")
