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

