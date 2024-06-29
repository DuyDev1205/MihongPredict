import requests
import json
import mysql.connector
from datetime import datetime, timedelta

def get_exchange_API(date):
    url = f"https://www.vietcombank.com.vn/api/exchangerates?date={date}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Yêu cầu không thành công. Mã trạng thái: {response.status_code}")
        return None

def insert_exchange_data(date, exchange_value):
    db = mysql.connector.connect(
        host="localhost",
        port="3306",
        user="root",
        password="123456",
        database="dss"
    )
    cursor = db.cursor()
    query="alter table exchange auto_increment = 1"
    cursor.execute(query)
    query = "INSERT INTO exchange (date, exchange_value) VALUES (%s, %s) ON DUPLICATE KEY UPDATE exchange_value=%s"
    cursor.execute(query, (date, exchange_value, exchange_value))
    
    db.commit()
    cursor.close()
    db.close()

def get_latest_date_from_db():
    db = mysql.connector.connect(
        host="localhost",
        port="3306",
        user="root",
        password="123456",
        database="dss"
    )
    cursor = db.cursor()
    
    query = "SELECT MAX(date) FROM exchange"
    cursor.execute(query)
    result = cursor.fetchone()
    cursor.close()
    db.close()
    
    if result[0] is not None:
        return result[0]
    else:
        return None
def get_existing_dates():
    db = mysql.connector.connect(
        host="localhost",
        port="3306",
        user="root",
        password="123456",
        database="dss"
    )
    cursor = db.cursor()
    
    query = "SELECT date FROM exchange"
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    db.close()
    
    existing_dates = set(result[0].strftime("%Y-%m-%d") for result in results)
    return existing_dates
def get_exchange_rates_for_last_50_days():
    end_date = datetime.now()
    start_date = end_date - timedelta(days=50)
    
    existing_dates = get_existing_dates()
    
    print("Bắt đầu lấy dữ liệu mới của Exchange.")

    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        if date_str not in existing_dates:
            api_data = get_exchange_API(date_str)
            if api_data:
                latest_value = None
                for val in api_data['Data']:
                    if val['currencyCode'] == 'USD':
                        latest_value = val['sell']
                
                if latest_value is not None:
                    json_data = {
                        'Code': 'USD',
                        'price': latest_value
                    }
                    formatted_json = json.dumps(json_data, indent=4, ensure_ascii=False)
                    # print(f"Ngày: {date_str}")
                    # print(formatted_json)
                    insert_exchange_data(date_str, latest_value)
        current_date += timedelta(days=1)
    print("Thu Thập dữ liệu ngoại tệ đã xong.")

if __name__ == "__main__":
    # get_exchange_rates_for_last_50_days()
    print(json.dumps(get_exchange_API('1/6/2024 00:00:00'),indent=4,ensure_ascii=False))