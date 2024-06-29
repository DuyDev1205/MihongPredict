import mysql.connector
import pandas as pd
from tabulate import tabulate
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from colorama import Fore, Style, init
import joblib
import json
init(autoreset=True)  # Khởi tạo colorama

def fetch_data_from_db():
    # Kết nối tới cơ sở dữ liệu
    db = mysql.connector.connect(
        host="localhost",
        port="3306",
        user="root",
        password="123456",
        database="dss"
    )
    cursor = db.cursor(dictionary=True)

    # Câu lệnh SQL để truy vấn dữ liệu
    query = """
    SELECT 
        g.date,
        g.gold_price AS gold,
        e.exchange_value AS exchange,
        gs.gas_value AS gas
    FROM 
        gold g
    LEFT JOIN 
        exchange e ON g.date = e.date
    LEFT JOIN 
        gas gs ON g.date = gs.date
    WHERE 
        g.date >= CURDATE() - INTERVAL 50 DAY
    ORDER BY 
        g.date ASC;
    """

    cursor.execute(query)
    results = cursor.fetchall()

    # Đóng kết nối cơ sở dữ liệu
    cursor.close()
    db.close()

    return results

def fill_missing_values(data):
    # Chuyển đổi dữ liệu thành DataFrame
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date']).dt.date  # Chuyển đổi thành chỉ có ngày

    # Tạo một loạt các ngày liên tục trong 30 ngày gần nhất
    date_range = pd.date_range(end=pd.Timestamp.now().date(), periods=50, freq='D')

    # Đặt 'date' làm chỉ số và reindex để đảm bảo có đủ 30 ngày
    df = df.set_index('date').reindex(date_range).reset_index()
    df = df.rename(columns={'index': 'date'})

    # Điền các giá trị bị thiếu bằng giá trị của ngày trước đó và sau đó
    df = df.ffill().bfill()

    # Thêm cột số thứ tự
    df.insert(0, 'Số thứ tự', range(1, len(df) + 1))

    return df

def convert_to_float(df):
    # Chuyển đổi các giá trị thành số thực để thực hiện các phép so sánh
    df['gold'] = df['gold'].replace(',', '', regex=True).astype(float)
    df['exchange'] = df['exchange'].replace(',', '', regex=True).astype(float)
    df['gas'] = df['gas'].replace(',', '', regex=True).astype(float)
    return df

def format_numbers(df):
    # Định dạng các giá trị số để hiển thị đầy đủ
    df['gold'] = df['gold'].apply(lambda x: '{:,}'.format(x) if pd.notnull(x) else '')
    df['exchange'] = df['exchange'].apply(lambda x: '{:,}'.format(x) if pd.notnull(x) else '')
    df['gas'] = df['gas'].apply(lambda x: '{:,}'.format(x) if pd.notnull(x) else '')
    return df

def train_model(df,congold,conexchange,congas):
    # Giả sử bạn có cột 'sell' trong dữ liệu lịch sử để đào tạo mô hình
    # Tạo dữ liệu mẫu cho mục đích demo
    df_train = df.copy()
    df_train['sell'] = ((df_train['gold'] > congold).astype(int) +
                        (df_train['exchange'] > conexchange).astype(int) +
                        (df_train['gas'] < congas).astype(int) >= 2).astype(int)

    features = ['gold', 'exchange', 'gas']
    X = df_train[features]
    y = df_train['sell']

    # Xử lý các giá trị NaN
    X = X.fillna(0)

    # Chuẩn hóa dữ liệu
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Chia dữ liệu thành tập huấn luyện và kiểm tra
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

    # Đào tạo mô hình Random Forest
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Lưu mô hình và scaler
    joblib.dump(model, 'random_forest_model.pkl')
    joblib.dump(scaler, 'scaler.pkl')

    return model, scaler

def add_sell_result(df, model, scaler):
    # Chuẩn bị dữ liệu để dự đoán
    features = ['gold', 'exchange', 'gas']
    X = df[features].fillna(0)
    X_scaled = scaler.transform(X)

    # Dự đoán
    df['sell_result'] = model.predict(X_scaled)

    return df
def train_regression_model(df):
    features = ['exchange', 'gas']
    target = 'gold'
    X = df[features]
    y = df[target]

    # Xử lý các giá trị NaN
    X = X.fillna(0)

    # Chuẩn hóa dữ liệu
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Chia dữ liệu thành tập huấn luyện và kiểm tra
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

    # Đào tạo mô hình Random Forest Regressor
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Lưu mô hình và scaler
    joblib.dump(model, 'random_forest_regressor.pkl')
    joblib.dump(scaler, 'scaler_regressor.pkl')

    return model, scaler
def predict_gold_price(model, scaler, exchange, gas):
    # Chuẩn bị dữ liệu mới cho dự đoán
    new_data = pd.DataFrame({
        'exchange': [exchange],
        'gas': [gas]
    })

    # Chuẩn hóa dữ liệu mới
    new_data_scaled = scaler.transform(new_data)

    # Thực hiện dự đoán
    predicted_gold_price = model.predict(new_data_scaled)

    return predicted_gold_price[0]
def highlight_sell_result(df, congold, conexchange, congas):
    highlighted_data = []
    for _, row in df.iterrows():
        highlighted_row = []
        for col in df.columns:
            if col == 'sell_result' and row['sell_result'] == 1:
                highlighted_row.append(Fore.GREEN + str(row[col]) + Style.RESET_ALL)
            elif col == 'gold' and row['gold'] > congold:
                highlighted_row.append(Fore.GREEN + '{:,}'.format(float(row[col])) + Style.RESET_ALL)
            elif col == 'exchange' and row['exchange'] > conexchange:
                highlighted_row.append(Fore.GREEN + '{:,}'.format(float(row[col])) + Style.RESET_ALL)
            elif col == 'gas' and row['gas'] < congas:
                highlighted_row.append(Fore.GREEN + '{:,}'.format(row[col]) + Style.RESET_ALL)
            else:
                highlighted_row.append('{:,}'.format(float(row[col])) if isinstance(row[col], float) else str(row[col]))
        highlighted_data.append(highlighted_row)
    return highlighted_data
import os

def delete_models():
    try:
        model1_path="random_forest_model.pkl"
        model2_path="scaler.pkl"
        model3_path="random_forest_regressor.pkl"
        model4_path="scaler_regressor.pkl"
        if os.path.exists(model1_path):
            os.remove(model1_path)
            print(f"Deleted: {model1_path}")
        else:
            print(f"File not found: {model1_path}")

        if os.path.exists(model2_path):
            os.remove(model2_path)
            print(f"Deleted: {model2_path}")
        else:
            print(f"File not found: {model2_path}")
        if os.path.exists(model3_path):
            os.remove(model3_path)
            print(f"Deleted: {model3_path}")
        else:
            print(f"File not found: {model3_path}")
        if os.path.exists(model4_path):
            os.remove(model4_path)
            print(f"Deleted: {model4_path}")
        else:
            print(f"File not found: {model4_path}")

    except Exception as e:
        print(f"An error occurred: {e}")
def reggession():
    # Lấy dữ liệu từ cơ sở dữ liệu
    data = fetch_data_from_db()

    # Điền các giá trị bị thiếu
    df = fill_missing_values(data)

    # Chuyển đổi các giá trị thành số thực
    df = convert_to_float(df)
    try:
        regression_model = joblib.load('random_forest_regressor.pkl')
        regression_scaler = joblib.load('scaler_regressor.pkl')
    except FileNotFoundError:
        regression_model, regression_scaler = train_regression_model(df)

    # Lấy giá trị trao đổi và giá gas của ngày mới nhất để dự đoán giá vàng
    latest_exchange = df['exchange'].iloc[-1]
    latest_gas = df['gas'].iloc[-1]

    # Dự đoán giá vàng
    predicted_price = predict_gold_price(regression_model, regression_scaler, latest_exchange, latest_gas)
    print(f"Giá vàng dự đoán: {predicted_price}")
    return predicted_price
def output_dataframe():
    congold= reggession()
    conexchange,congas =24000,21
    # Lấy dữ liệu từ cơ sở dữ liệu
    data = fetch_data_from_db()

    # Điền các giá trị bị thiếu
    df = fill_missing_values(data)

    # Chuyển đổi các giá trị thành số thực
    df = convert_to_float(df)
    # delete_models()

    # Đào tạo mô hình Random Forest
    try:
        model = joblib.load('random_forest_model.pkl')
        scaler = joblib.load('scaler.pkl')
    except FileNotFoundError:
        model, scaler = train_model(df,congold,conexchange,congas)

    # Thêm cột sell_result
    df = add_sell_result(df, model, scaler)

    # Highlight các cột cần thiết
    highlighted_df = highlight_sell_result(df,congold,conexchange,congas)

    # Định dạng các giá trị số
    df = format_numbers(df)
    
    # In kết quả ra dưới dạng bảng
    print(tabulate(highlighted_df, headers=df.columns, tablefmt='fancy_outline', showindex=False))
    print(df['gold'].iloc[-1])

if __name__ == "__main__":
    output_dataframe()
