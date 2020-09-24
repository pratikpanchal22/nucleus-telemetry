import mysql.connector
from mysql.connector import Error
import requests

try:
    conn = mysql.connector.connect(host='localhost', database='appDbSandbox', user='user', password='password')
    if conn.is_connected():
        cursor = conn.cursor()
        cursor.execute("select database();")
        record = cursor.fetchall()
        print("You're connected to - ", record)

    r=requests.get('http://192.168.1.83/get/sysstat')
    print(r.status_code)
    print(r.text)
except Error as e:
    print ("Print your error msg", e)
finally:
    if(conn.is_connected()):
        cursor.close()
        conn.close()
