import pyodbc

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=InvoiceSystem;"
    "UID=DemoSystem;"      # 改成你的登入帳號
    "PWD=DemoSystem@123;"           # 改成你的密碼
    "TrustServerCertificate=yes;"
)
def invoice_exists(invoice_number):
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    sql = """
    SELECT COUNT(*)
    FROM invoices
    WHERE invoice_number = ?
    """

    cursor.execute(sql, (invoice_number,))
    count = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return count > 0

def save_invoice(
    invoice_number,
    invoice_date,
    invoice_period,
    prize_type,
    prize_amount
):
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    if prize_type in ["查無此期別或尚未開獎", "查詢失敗", "尚未開獎"]:
        final_prize_amount = None
    else:
        final_prize_amount = int(prize_amount)

    sql = """
    INSERT INTO invoices
    (invoice_number, invoice_date, invoice_period, prize_type, prize_amount)
    VALUES (?, ?, ?, ?, ?)
    """

    cursor.execute(sql, (
        invoice_number,
        invoice_date,
        invoice_period,
        prize_type,
        final_prize_amount
    ))

    conn.commit()
    cursor.close()
    conn.close()
    
def get_all_winning_numbers():
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            invoice_period,
            special_prize,
            grand_prize,
            first_prize1,
            first_prize2,
            first_prize3,
            sixth_prize1,
            sixth_prize2,
            sixth_prize3
        FROM winning_numbers
        ORDER BY invoice_period DESC
    """)

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows