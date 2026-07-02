import os
import mysql.connector


def get_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQLHOST", "localhost"),
        port=int(os.getenv("MYSQLPORT", 3306)),
        user=os.getenv("MYSQLUSER", "root"),
        password=os.getenv("MYSQLPASSWORD", ""),
        database=os.getenv("MYSQLDATABASE", "invoice_system"),
    )


def save_invoice(invoice_number, invoice_date, invoice_period, prize_type, prize_amount):
    conn = get_connection()
    cursor = conn.cursor()

    sql = """
    INSERT INTO invoices
    (invoice_number, invoice_date, invoice_period, prize_type, prize_amount)
    VALUES (%s, %s, %s, %s, %s)
    """

    cursor.execute(sql, (
        invoice_number,
        invoice_date if invoice_date != "未辨識" else None,
        invoice_period,
        prize_type,
        int(prize_amount)
    ))

    conn.commit()
    cursor.close()
    conn.close()