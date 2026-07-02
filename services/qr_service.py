import cv2
import re
import zxingcpp


def read_qrcode(image_path):
    image = cv2.imread(image_path)

    if image is None:
        return []

    h, w = image.shape[:2]

    areas = [
        image,
        image[int(h * 0.15):int(h * 0.65), int(w * 0.05):int(w * 0.95)],
        image[int(h * 0.30):int(h * 0.90), int(w * 0.05):int(w * 0.95)]
    ]

    results = []

    for area in areas:
        if area is None or area.size == 0:
            continue

        big = cv2.resize(area, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        decoded = zxingcpp.read_barcodes(big)

        for code in decoded:
            if code.text and code.text not in results:
                results.append(code.text)

    return results


def extract_invoice_from_qr(qr_texts):
    text = "\n".join(qr_texts).upper()

    match = re.search(r"[A-Z]{2}\d{8}", text)
    if match:
        return match.group()

    return "未讀取到發票號碼"


def extract_invoice_date_from_qr(qr_texts):
    text = "\n".join(qr_texts).upper()

    # 台灣電子發票 QR Code 格式：
    # 發票號碼 10 碼 + 民國日期 7 碼
    # 例如 GH288466021030322
    match = re.search(r"([A-Z]{2}\d{8})(\d{7})", text)

    if match:
        roc_date = match.group(2)   # 1030322
        roc_year = int(roc_date[0:3])
        month = int(roc_date[3:5])
        day = int(roc_date[5:7])
        western_year = roc_year + 1911

        return f"{western_year}/{month:02d}/{day:02d}"

    # 西元格式：20260701
    match = re.search(r"20\d{6}", text)
    if match:
        raw = match.group()
        return f"{raw[0:4]}/{raw[4:6]}/{raw[6:8]}"

    # 西元格式：2026/07/01
    match = re.search(r"20\d{2}[-/]\d{2}[-/]\d{2}", text)
    if match:
        return match.group().replace("-", "/")

    return "未辨識"


def convert_date_to_period(invoice_date):
    if not invoice_date or invoice_date == "未辨識":
        return "未辨識到期別"

    try:
        year, month, day = invoice_date.split("/")
        year = int(year)
        month = int(month)

        if year > 1911:
            roc_year = year - 1911
        else:
            roc_year = year

        if month in [1, 2]:
            end_month = 2
        elif month in [3, 4]:
            end_month = 4
        elif month in [5, 6]:
            end_month = 6
        elif month in [7, 8]:
            end_month = 8
        elif month in [9, 10]:
            end_month = 10
        elif month in [11, 12]:
            end_month = 12
        else:
            return "未辨識到期別"

        return f"{roc_year}{end_month:02d}"

    except:
        return "未辨識到期別"