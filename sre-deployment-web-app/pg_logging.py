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
        conn = get_postgres_connection()
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
            conn.commit()
        except Exception as insert_err:
            if 'st' in locals() and st is not None:
                st.error(f"Error inserting log: {insert_err}")
            else:
                print(f"Error inserting log: {insert_err}")
            raise
        cur.close()
        conn.close()
    except Exception as e:
        if 'st' in locals() and st is not None:
            st.error(f"Failed to log command to PostgreSQL: {e}")
        else:
            print(f"Failed to log command to PostgreSQL: {e}")
