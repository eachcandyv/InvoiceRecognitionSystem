import os
import mysql.connector
from mysql.connector import Error
from urllib.parse import urlparse


def get_connection():
    mysql_url = os.environ.get("MYSQL_URL") or os.environ.get("DATABASE_URL")

    if mysql_url:
        url = urlparse(mysql_url)

        return mysql.connector.connect(
            host=url.hostname,
            port=url.port or 3306,
            user=url.username,
            password=url.password,
            database=url.path.lstrip("/"),
            charset="utf8mb4"
        )

    return mysql.connector.connect(
        host=os.environ.get("MYSQLHOST"),
        port=int(os.environ.get("MYSQLPORT", 3306)),
        user=os.environ.get("MYSQLUSER"),
        password=os.environ.get("MYSQLPASSWORD"),
        database=os.environ.get("MYSQLDATABASE"),
        charset="utf8mb4"
    )


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id INT AUTO_INCREMENT PRIMARY KEY,
            invoice_number VARCHAR(20) NOT NULL UNIQUE,
            invoice_date VARCHAR(20),
            invoice_period VARCHAR(20),
            prize_type VARCHAR(50),
            prize_amount INT DEFAULT 0,
            invoice_type VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
    """)

    conn.commit()
    cursor.close()
    conn.close()


def invoice_exists(invoice_number):
    if not invoice_number:
        return False

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM invoices WHERE invoice_number = %s",
        (invoice_number,)
    )

    count = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return count > 0


def save_invoice(
    invoice_number,
    invoice_date,
    invoice_period,
    prize_type,
    prize_amount,
    invoice_type=""
):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO invoices (
                invoice_number,
                invoice_date,
                invoice_period,
                prize_type,
                prize_amount,
                invoice_type
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            invoice_number,
            invoice_date,
            invoice_period,
            prize_type,
            int(prize_amount) if str(prize_amount).isdigit() else 0,
            invoice_type
        ))

        conn.commit()

    except Error as e:
        conn.rollback()
        print("MySQL 儲存錯誤：", e)
        raise e

    finally:
        cursor.close()
        conn.close()