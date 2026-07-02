import requests
import urllib3
from bs4 import BeautifulSoup
import re

urllib3.disable_warnings()


def get_etax_url(invoice_period):
    roc_year = invoice_period[:3]
    end_month = invoice_period[3:5]

    start_month_map = {
        "02": "01",
        "04": "03",
        "06": "05",
        "08": "07",
        "10": "09",
        "12": "11"
    }

    start_month = start_month_map.get(end_month)

    if not start_month:
        return None

    return f"https://www.etax.nat.gov.tw/etw-main/ETW183W2_{roc_year}{start_month}/"


def get_winning_numbers(invoice_period):
    url = get_etax_url(invoice_period)

    if not url:
        return None

    response = requests.get(
        url,
        timeout=2,
        verify=False,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )

    response.encoding = "utf-8"

    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text("\n")

    numbers_8 = re.findall(r"(?<!\d)\d{8}(?!\d)", text)
    numbers_3 = re.findall(r"(?<!\d)\d{3}(?!\d)", text)

    if len(numbers_8) < 5:
        print("抓不到足夠中獎號碼")
        print(text[:500])
        return None

    roc_year = int(invoice_period[:3])

    # 111年起取消增開六獎
    if roc_year >= 111:
        sixth1 = ""
        sixth2 = ""
        sixth3 = ""
    else:
        sixth1 = numbers_3[0] if len(numbers_3) > 0 else ""
        sixth2 = numbers_3[1] if len(numbers_3) > 1 else ""
        sixth3 = numbers_3[2] if len(numbers_3) > 2 else ""

    return {
        "superPrizeNo": numbers_8[0],
        "spcPrizeNo": numbers_8[1],
        "firstPrizeNo1": numbers_8[2],
        "firstPrizeNo2": numbers_8[3],
        "firstPrizeNo3": numbers_8[4],
        "sixthPrizeNo1": sixth1,
        "sixthPrizeNo2": sixth2,
        "sixthPrizeNo3": sixth3,
    }


def check_prize(invoice_number, invoice_period):
    try:
        data = get_winning_numbers(invoice_period)

        if not data:
            return {
                "is_winner": False,
                "prize_type": "查無此期別或尚未開獎",
                "prize_amount": 0
            }

        number = "".join(filter(str.isdigit, invoice_number))[-8:]

    except Exception as e:
        print("查詢錯誤詳細內容：", repr(e))
        return {
            "is_winner": False,
            "prize_type": "查詢失敗",
            "prize_amount": 0
        }

    special_prize_no = data.get("superPrizeNo")
    grand_prize_no = data.get("spcPrizeNo")

    first_prize_numbers = [
        data.get("firstPrizeNo1"),
        data.get("firstPrizeNo2"),
        data.get("firstPrizeNo3")
    ]

    roc_year = int(invoice_period[:3])

    if roc_year >= 111:
        sixth_prize_numbers = []
    else:
        sixth_prize_numbers = [
            data.get("sixthPrizeNo1"),
            data.get("sixthPrizeNo2"),
            data.get("sixthPrizeNo3")
        ]

    if number == special_prize_no:
        return {"is_winner": True, "prize_type": "特別獎", "prize_amount": 10000000}

    if number == grand_prize_no:
        return {"is_winner": True, "prize_type": "特獎", "prize_amount": 2000000}

    for first_no in first_prize_numbers:
        if not first_no:
            continue

        if number == first_no:
            return {"is_winner": True, "prize_type": "頭獎", "prize_amount": 200000}
        if number[-7:] == first_no[-7:]:
            return {"is_winner": True, "prize_type": "二獎", "prize_amount": 40000}
        if number[-6:] == first_no[-6:]:
            return {"is_winner": True, "prize_type": "三獎", "prize_amount": 10000}
        if number[-5:] == first_no[-5:]:
            return {"is_winner": True, "prize_type": "四獎", "prize_amount": 4000}
        if number[-4:] == first_no[-4:]:
            return {"is_winner": True, "prize_type": "五獎", "prize_amount": 1000}
        if number[-3:] == first_no[-3:]:
            return {"is_winner": True, "prize_type": "六獎", "prize_amount": 200}

    for sixth_no in sixth_prize_numbers:
        if sixth_no and number[-3:] == sixth_no:
            return {"is_winner": True, "prize_type": "增開六獎", "prize_amount": 200}

    return {
        "is_winner": False,
        "prize_type": "未中獎",
        "prize_amount": 0
    }