from rapidocr_onnxruntime import RapidOCR
import re

ocr = RapidOCR()


def recognize_text_rapidocr(image_path):
    result, _ = ocr(image_path)

    if not result:
        return ""

    texts = []

    for item in result:
        texts.append(item[1])

    return "\n".join(texts)


def extract_invoice_number(text):
    lines = [line.strip().upper() for line in text.splitlines() if line.strip()]

    clean_text = text.upper()
    clean_text = clean_text.replace(" ", "")
    clean_text = clean_text.replace("-", "")
    clean_text = clean_text.replace("：", "")
    clean_text = clean_text.replace(":", "")

    match = re.search(r"[A-Z]{2}\d{8}", clean_text)
    if match:
        return match.group()

    for i in range(len(lines) - 1):
        letters = re.sub(r"[^A-Z]", "", lines[i])
        numbers = re.sub(r"[^0-9]", "", lines[i + 1])

        if len(letters) == 2 and len(numbers) == 8:
            return letters + numbers

    number_match = re.search(r"\d{8}", clean_text)
    if number_match:
        return "請補英文碼：" + number_match.group()

    return "未辨識到發票號碼"


def extract_invoice_date(text):
    clean_text = text.replace(" ", "")

    match = re.search(r"(20\d{2})[-/](\d{1,2})[-/](\d{1,2})", clean_text)
    if match:
        return f"{match.group(1)}/{int(match.group(2)):02d}/{int(match.group(3)):02d}"

    match = re.search(r"(\d{2,3})[-/](\d{1,2})[-/](\d{1,2})", clean_text)
    if match:
        roc_year = int(match.group(1))
        month = int(match.group(2))
        day = int(match.group(3))
        return f"{roc_year}/{month:02d}/{day:02d}"

    return "未辨識"


def extract_invoice_period(text):
    clean_text = text.replace(" ", "")
    clean_text = clean_text.replace("月份", "月")
    clean_text = clean_text.replace("－", "-")
    clean_text = clean_text.replace("~", "-")
    clean_text = clean_text.replace("至", "-")

    # 例如：103年3-4月
    match = re.search(r"(\d{2,3})年0?(\d{1,2})-0?(\d{1,2})月", clean_text)
    if match:
        roc_year = int(match.group(1))
        end_month = int(match.group(3))
        return f"{roc_year}{end_month:02d}"

    invoice_date = extract_invoice_date(text)

    if invoice_date != "未辨識":
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
            pass

    return "未辨識到期別"