import psycopg2
import streamlit as st
from datetime import datetime

def get_postgres_connection():
    """
    Returns a new PostgreSQL connection using Streamlit secrets.
    """
    return psycopg2.connect(
        host=st.secrets["PG_HOST"],
        port=st.secrets["PG_PORT"],
        dbname=st.secrets["PG_DBNAME"],
        user=st.secrets["PG_USER"],
        password=st.secrets["PG_PASSWORD"]
    )

def log_command_to_postgres(username: str, command: str):
    """
    Logs the command execution to PostgreSQL with username and timestamp.
    Creates the table if it does not exist.
    """
    try:
        with get_postgres_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS deployment_command_logs (
                        id SERIAL PRIMARY KEY,
                        username TEXT NOT NULL,
                        timestamp TIMESTAMP NOT NULL,
                        command TEXT NOT NULL
                    );
                """)
                cur.execute(
                    "INSERT INTO deployment_command_logs (username, timestamp, command) VALUES (%s, %s, %s)",
                    (username, datetime.now(), command)
                )
            conn.commit()
    except Exception as e:
        print(f"Failed to log command to PostgreSQL: {e}")
