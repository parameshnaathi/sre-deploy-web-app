import psycopg2
import streamlit as st
from datetime import datetime

def get_postgres_connection():
    """
    Returns a new PostgreSQL connection using Streamlit secrets.
    """
    return psycopg2.connect(
        host=st.secrets["PG_HOST"],
        port=int(st.secrets["PG_PORT"]),
        dbname=st.secrets["PG_DBNAME"],
        user=st.secrets["PG_USER"],
        password=st.secrets["PG_PASSWORD"]
    )

def log_command_to_postgres(username: str, command: str):
        try:
            conn = psycopg2.connect(
                host=st.secrets["PG_HOST"],
                port=int(st.secrets["PG_PORT"]),
                dbname=st.secrets["PG_DBNAME"],
                user=st.secrets["PG_USER"],
                password=st.secrets["PG_PASSWORD"]
            )
            return conn
        except Exception as e:
            st.error(f"[DB Connection Error] {e}")
            print(f"[DB Connection Error] {e}")
            raise
        # Always attempt to create the table (idempotent)
        try:
            cur.execute('''
CREATE TABLE IF NOT EXISTS deployment_command_logs (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    command TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL
)
''')
        except Exception as table_err:
            if 'st' in locals() and st is not None:
                st.error(f"Error creating table: {table_err}")
            else:
                print(f"Error creating table: {table_err}")
            raise
        # Insert log
        try:
            cur.execute(
                """
INSERT INTO deployment_command_logs (username, command, timestamp)
VALUES (%s, %s, %s)
""",
                (username, command, datetime.now())
            )
            try:
                st.write("[DEBUG] log_command_to_postgres called")
                conn = get_postgres_connection()
                st.write("[DEBUG] Connected to DB")
                cur = conn.cursor()
                # Always attempt to create the table (idempotent)
                try:
                    cur.execute('''
        CREATE TABLE IF NOT EXISTS deployment_command_logs (
            id SERIAL PRIMARY KEY,
            username TEXT NOT NULL,
            command TEXT NOT NULL,
            timestamp TIMESTAMP NOT NULL
        )
        ''')
                    st.write("[DEBUG] Table creation checked/executed")
                except Exception as table_err:
                    st.error(f"[Table Creation Error] {table_err}")
                    print(f"[Table Creation Error] {table_err}")
                    raise
                # Insert log
                try:
                    cur.execute(
                        """
        INSERT INTO deployment_command_logs (username, command, timestamp)
        VALUES (%s, %s, %s)
        """,
                        (username, command, datetime.now())
                    )
                    conn.commit()
                    st.write("[DEBUG] Log inserted")
                except Exception as insert_err:
                    st.error(f"[Insert Error] {insert_err}")
                    print(f"[Insert Error] {insert_err}")
                    raise
                cur.close()
                conn.close()
                st.write("[DEBUG] DB connection closed")
            except Exception as e:
                st.error(f"[Log Command Error] {e}")
                print(f"[Log Command Error] {e}")
