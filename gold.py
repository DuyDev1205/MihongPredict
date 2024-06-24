import requests
import json
from datetime import datetime

# Hàm để lấy dữ liệu từ API
def get_gold_API(start_date, end_date):
    url = f"https://www.mihong.vn/api/v1/gold/prices/codes?code=SJC&startDate={start_date}&endDate={end_date}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Yêu cầu không thành công. Mã trạng thái: {response.status_code}")
        return None

# Hàm để lấy giá trị cuối cùng cho mỗi ngày
def get_latest_data(data):
    latest_data = {}
    for entry in data:
        date_str = entry['date'].split()[0]  # Lấy phần ngày từ chuỗi 'date'
        latest_data[date_str] = entry  # Ghi đè giá trị, chỉ giữ lại giá trị cuối cùng
    return list(latest_data.values())
