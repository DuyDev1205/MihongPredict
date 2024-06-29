import mysql.connector
import requests
import json
from datetime import datetime, timedelta

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

def get_existing_dates():
    db = mysql.connector.connect(
        host="localhost",
        port="3306",
        user="root",
        password="123456",
        database="dss"
    )
    cursor = db.cursor()

    # Lấy tất cả các ngày đã có trong bảng gold
    cursor.execute("SELECT date FROM gold ORDER BY date ASC")
    result = cursor.fetchall()
    db.close()

    return [row[0].strftime("%Y-%m-%d") for row in result]

def insert_gold_data(date, gold_price):
    db = mysql.connector.connect(
        host="localhost",
        port="3306",
        user="root",
        password="123456",
        database="dss"
    )
    cursor = db.cursor()

    # Chuyển đổi định dạng ngày từ DD/MM/YYYY HH:MM:SS sang YYYY-MM-DD HH:MM:SS
    date_obj = datetime.strptime(date, "%d/%m/%Y %H:%M:%S")
    formatted_date = date_obj.strftime("%Y-%m-%d %H:%M:%S")
    query ="alter table gold auto_increment = 1"
    cursor.execute(query)
    query = "INSERT INTO gold (date, gold_price) VALUES (%s, %s) ON DUPLICATE KEY UPDATE gold_price=%s"
    cursor.execute(query, (formatted_date, gold_price, gold_price))
    db.commit()
    cursor.close()
    db.close()
def final_gold_data():
    existing_dates = get_existing_dates()
    end_date = datetime.now().date()

    if existing_dates:
        latest_date = datetime.strptime(existing_dates[0], "%Y-%m-%d").date()
    else:
        latest_date = end_date - timedelta(days=50)

    while len(existing_dates) <= 50:
        start_date = latest_date - timedelta(days=50 - len(existing_dates))
        start_date_str = start_date.strftime("%d/%m/%Y 00:00:00")
        end_date_str = end_date.strftime("%d/%m/%Y 23:59:59")
        print(f"Lấy dữ liệu từ {start_date_str} đến {end_date_str}")

        response = get_gold_API(start_date_str, end_date_str)
        if response and response['success']:
            data = response['data']
            latest_data = get_latest_data(data)
            for val in latest_data:
                json_data = {
                    'sell': val['sell'],
                    'date': datetime.strptime(val['date'], "%Y/%m/%d %H:%M:%S").strftime("%d/%m/%Y %H:%M:%S")
                }
                formatted_json = json.dumps(json_data, indent=4, ensure_ascii=False)
                # print(formatted_json)

                # Chèn dữ liệu vào cơ sở dữ liệu
                insert_gold_data(json_data['date'], json_data['sell'])
                formatted_date = datetime.strptime(json_data['date'], "%d/%m/%Y %H:%M:%S").strftime("%Y-%m-%d")
                if formatted_date not in existing_dates:
                    existing_dates.append(formatted_date)

            # Cập nhật latest_date cho lần lặp tiếp theo
            if latest_data:
                latest_date = datetime.strptime(latest_data[-1]['date'], "%Y/%m/%d %H:%M:%S").date()
        else:
            print("Không có dữ liệu hoặc yêu cầu không thành công.")
            break
    print("Thu thập dữ liệu vàng đã xong")

if __name__ == "__main__":
    final_gold_data()
    # print(json.dumps(get_gold_API('1/6/2024 00:00:00', '25/6/2024 23:59:59'),indent=4,ensure_ascii=False))
