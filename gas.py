import mysql.connector
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from time import sleep
from datetime import datetime
config = {
    "host": "localhost",
    "port": "3306",
    "user": "root",
    "password": "123456",
    "database": "dss"
}
def getDateGas(driver,day_left):
    # Lấy giá trị của phần tử dựa trên XPath
    dropdown = driver.find_element(By.XPATH,'//*[@id="ctl00_mainContent_ctl03_ddlDate"]')
    # Tạo đối tượng Select từ dropdown
    select = Select(dropdown)
    # Lấy tất cả các phần tử <option> trong dropdown
    options = select.options
    
    # Tạo danh sách để lưu trữ giá trị của các phần tử <option>
    values = []
    for option in options[:day_left]:
        values.append(option.get_attribute("value"))
    
    return values
def inputDateGas(driver,value):
    # print(value)
    # Tìm phần tử dropdown
    dropdown = driver.find_element(By.XPATH, '//*[@id="ctl00_mainContent_ctl03_ddlDate"]')
    dropdown.click()
    # Tạo đối tượng Select từ dropdown
    select = Select(dropdown)
    # Chọn giá trị từ dropdown bằng cách sử dụng giá trị đã lấy được
    select.select_by_value(value)
def getValueGas(driver):
    gas_list=[]
    gas_val=driver.find_element(By.XPATH,'(//tbody//tr[1]//td[3])[1]')
    gas_list.append(gas_val.text)
    return gas_list
def format_value(val):
    val_list=[]
    val_list.append(val+"0")
    return val_list
def get_latest_date_from_db():
    db = mysql.connector.connect(
        host="localhost",
        port="3306",
        user="root",
        password="123456",
        database="dss"
    )
    cursor = db.cursor()
    
    query = "SELECT MAX(date) FROM gas"
    cursor.execute(query)
    result = cursor.fetchone()
    cursor.close()
    db.close()
    
    if result[0] is not None:
        return result[0]
    else:
        return None
def final_gas_data():
    today_date = datetime.today().date().strftime("%Y-%m-%d")
    last_day=get_latest_date_from_db()
    if last_day is not None and last_day==today_date :
        print("Thu thập dữ liệu xăng dầu đã xong")
        return
    # Tạo một cấu hình cho trình duyệt Chrome
    chrome_options = webdriver.ChromeOptions()
    # Thêm tùy chọn để ngăn thông báo DevTools hiện thị trong terminal
    chrome_options.add_argument('--log-level=3')
    chrome_options.add_argument('--headless')
    # Tạo kết nối đến cơ sở dữ liệu
    config = {
        "host": "localhost",
        "port": "3306",
        "user": "root",
        "password": "123456",
        "database": "dss"
    }
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://www.pvoil.com.vn/truyen-thong/tin-gia-xang-dau")
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    day_left= 50
    day=getDateGas(driver,day_left)
    val_list=[]
    for val in day:
        inputDateGas(driver, val)
        sleep(0.2)
        gas_price = getValueGas(driver)[0]
        val_list.append((val, gas_price))
        query = "alter table gas auto_increment = 1"
        cursor.execute(query)
        # In ra định dạng ngày và giá xăng
        # print(f"Ngày {val} có giá xăng là {gas_price}")
        query = "INSERT INTO gas (date, gas_value) VALUES (%s, %s) ON DUPLICATE KEY UPDATE gas_value=%s"
        cursor.execute(query, (val, gas_price, gas_price))
        connection.commit()

    cursor.close()
    connection.close()
    driver.quit()
    print("Thu thập dữ liệu xăng dầu đã xong")
if __name__ == "__main__":
    final_gas_data()