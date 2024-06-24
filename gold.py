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
def print_data():
    start_date = datetime(2024, 4, 2, 0, 0, 0).strftime("%d/%m/%Y %H:%M:%S")
    end_date = datetime(2024, 4, 10, 23, 59, 59).strftime("%d/%m/%Y %H:%M:%S")
    response = get_gold_API(start_date, end_date)
    if response and response['success']:
        data = response['data']
        latest_data = get_latest_data(data)
        for val in latest_data:
            json_data = {
                'sell': val['sell'],
                'date': datetime.strptime(val['date'], "%Y/%m/%d %H:%M:%S").strftime("%d/%m/%Y %H:%M:%S")
            }
            formatted_json = json.dumps(json_data, indent=4, ensure_ascii=False)
            print(formatted_json)
    else:
        print("Không có dữ liệu hoặc yêu cầu không thành công.")
