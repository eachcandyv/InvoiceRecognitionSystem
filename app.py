from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os
from datetime import datetime

from services.sqlserver_service import (
    save_invoice,
    invoice_exists
)

from services.lottery_service import (
    check_prize,
    get_winning_numbers
)

from services.pdf_service import pdf_to_image

from services.qr_service import (
    read_qrcode,
    extract_invoice_from_qr,
    extract_invoice_date_from_qr,
    convert_date_to_period
)

from services.rapidocr_service import (
    recognize_text_rapidocr,
    extract_invoice_number,
    extract_invoice_date,
    extract_invoice_period
)

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "pdf"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    current_year = datetime.now().year - 1911

    years = [str(year) for year in range(current_year, 100, -1)]

    return render_template(
        "index.html",
        years=years,
        default_year=str(current_year),
        default_month="04"
    )


@app.route("/api/winning")
def api_winning():
    period = request.args.get("period")

    if not period:
        return {"success": False, "message": "沒有指定期別"}

    try:
        data = get_winning_numbers(period)

        if not data:
            return {"success": False, "message": "查無此期別或尚未開獎"}

        return {
            "success": True,
            "invoice_period": period,
            "special_prize": data.get("superPrizeNo", ""),
            "grand_prize": data.get("spcPrizeNo", ""),
            "first_prize1": data.get("firstPrizeNo1", ""),
            "first_prize2": data.get("firstPrizeNo2", ""),
            "first_prize3": data.get("firstPrizeNo3", ""),
            "sixth_prize1": data.get("sixthPrizeNo1", ""),
            "sixth_prize2": data.get("sixthPrizeNo2", ""),
            "sixth_prize3": data.get("sixthPrizeNo3", "")
        }

    except Exception as e:
        print("API 查詢錯誤：", repr(e))
        return {"success": False, "message": "查詢失敗"}


@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return "沒有收到檔案"

    file = request.files["file"]
    invoice_choice = request.form.get("invoice_type")

    if file.filename == "":
        return "沒有選擇檔案"

    if not allowed_file(file.filename):
        return "不支援的檔案格式"

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    ext = filename.rsplit(".", 1)[1].lower() if "." in filename else ""

    if ext == "pdf" or file.mimetype == "application/pdf":
        filepath = pdf_to_image(filepath)

    if invoice_choice == "electronic_qr":
        qr_texts = read_qrcode(filepath)

        invoice_number = extract_invoice_from_qr(qr_texts)
        invoice_date = extract_invoice_date_from_qr(qr_texts)
        invoice_period = convert_date_to_period(invoice_date)

        prize_result = check_prize(invoice_number, invoice_period)

        return render_template(
            "result.html",
            invoice_type="台灣電子發票 / QR Code",
            invoice_number=invoice_number,
            invoice_date=invoice_date,
            invoice_period=invoice_period,
            prize_result=prize_result,
            result_text="\n".join(qr_texts) if qr_texts else "未讀取到 QR Code"
        )

    elif invoice_choice == "ocr":
        ocr_text = recognize_text_rapidocr(filepath)

        invoice_number = extract_invoice_number(ocr_text)
        invoice_date = extract_invoice_date(ocr_text)
        invoice_period = extract_invoice_period(ocr_text)

        prize_result = check_prize(invoice_number, invoice_period)

        return render_template(
            "result.html",
            invoice_type="影像辨識 OCR（電子 / 傳統發票）",
            invoice_number=invoice_number,
            invoice_date=invoice_date,
            invoice_period=invoice_period,
            prize_result=prize_result,
            result_text=ocr_text
        )

    return "請選擇辨識方式"


@app.route("/save", methods=["POST"])
def save():
    invoice_type = request.form["invoice_type"]
    invoice_number = request.form["invoice_number"]
    invoice_date = request.form["invoice_date"]
    invoice_period = request.form["invoice_period"]
    prize_type = request.form["prize_type"]
    prize_amount = request.form["prize_amount"]

    if invoice_exists(invoice_number):
        return """
        <script>
            alert("此發票已存在，未重複存入！");
            window.location.href = "/";
        </script>
        """
    if prize_type in ["查無此期別或尚未開獎", "查詢失敗", "尚未開獎"]:
        display_prize_amount = "尚未開獎"
    elif prize_type == "未中獎":
        display_prize_amount = "—"
    else:
        display_prize_amount = f"{prize_amount} 元"
    save_invoice(
        invoice_number,
        invoice_date,
        invoice_period,
        prize_type,
        prize_amount
    )
    if invoice_exists(invoice_number):
        return f"""
        <!DOCTYPE html>
        <html lang="zh-Hant">
        <head>
            <meta charset="UTF-8">
            <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
        </head>
        <body>

        <script>
        Swal.fire({{
            icon: 'success',
            title: '存入成功！',
            html: `
                <b>發票號碼：</b>{invoice_number}<br><br>
                <b>發票日期：</b>{invoice_date}<br><br>
                <b>發票期別：</b>{invoice_period}<br><br>
                <b>獎項：</b>{prize_type}<br><br>
                <b>獎金：</b>{display_prize_amount}
            `,
            confirmButtonText: '返回首頁'
        }}).then(() => {{
            window.location.href = "/";
        }});
        </script>

        </body>
        </html>
        """


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)