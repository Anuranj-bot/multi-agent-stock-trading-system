import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv


# LOAD ENV VARIABLES

load_dotenv()
# DATABASE CONNECTION

def get_connection():
    """
    Establish and return a PostgreSQL database connection.
    """
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT", 5432),
            sslmode="require"
        )
        return conn
    except Exception as e:
        print(" Database connection failed:")
        print(str(e))
        raise
# FETCH PENDING REQUEST


def fetch_pending_request():
    """
    Fetch the first pending request from trade_requests table.
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT id, stock_symbol, trade_date
            FROM trade_requests
            WHERE status = 'pending'
            ORDER BY id ASC
            LIMIT 1
        """)

        row = cursor.fetchone()

        cursor.close()

        if not row:
            return None

        return {
            "id": row["id"],
            "stock_symbol": row["stock_symbol"],
            "trade_date": str(row["trade_date"]),
        }

    except Exception as e:
        print(" Error fetching pending request:")
        print(str(e))
        return None

    finally:
        if conn:
            conn.close()
# SAVE AGENT OUTPUT (REAL-TIME STREAMING)

def save_agent_output(company_name, report_date, agent_name, report):

    if not report or report.strip() == "":
        return

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO agent_reports
        (company_name, report_date, agent_name, report)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (company_name, report_date, agent_name)
        DO UPDATE SET report = EXCLUDED.report
    """, (company_name, report_date, agent_name, report))

    conn.commit()
    cursor.close()
    conn.close()
# MARK REQUEST AS COMPLETED

def mark_request_completed(request_id):
    """
    Update trade_requests status to 'completed'
    after successful execution.
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE trade_requests
            SET status = 'completed'
            WHERE id = %s
        """, (request_id,))

        conn.commit()
        cursor.close()

    except Exception as e:
        print(" Error updating request status:")
        print(str(e))

    finally:
        if conn:
            conn.close()