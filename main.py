from gold import final_gold_data
from exchange import get_exchange_rates_for_last_50_days
from gas import final_gas_data
from multiprocessing import Process
from dataframe import output_dataframe,delete_models
import os
import mysql.connector
class Color:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'
def get_data():
    processes = []
    p1 = Process(target=final_gold_data)
    p1.start()
    processes.append(p1)

    p2= Process(target=get_exchange_rates_for_last_50_days)
    p2.start()
    processes.append(p2)
    
    p3= Process(target=final_gas_data)
    p3.start()
    processes.append(p3)

    for p in processes:
        p.join()
def delete_db():
    db = mysql.connector.connect(
        host="localhost",
        port="3306",
        user="root",
        password="123456",
        database="dss"
    )
    cursor = db.cursor()

    cursor.execute("DELETE FROM gold")
    cursor.execute("DELETE FROM exchange")
    cursor.execute("DELETE FROM gas")
    
    
    db.commit()
    cursor.close()
    db.close()
    print("Data deleted successfully.")
def menu():
    
    print(f"1. Get Data from API")
    print(f"2. Output dataframe")
    print(f"3. Delete models")
    print(f"4. Delete Database")
    print(f"5. Exit")

def output():
    while True:
        menu()
        try:
            choice = int(input(f"{Color.GREEN}Enter your choice:"))
            match choice:
                case 1:
                    get_data()
                case 2:
                    output_dataframe()
                case 3:
                    delete_models()
                case 4:
                    delete_db()
                case 5:
                    break
                case _:
                    print(f"{Color.RESET}Invalid choice, please try again.")
        except ValueError:
            print(f"{Color.RESET}Invalid input, please enter a number.")
if __name__ == "__main__":
    output()