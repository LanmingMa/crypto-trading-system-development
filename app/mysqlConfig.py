import mysql.connector as mc

def mysql_connection():
    conn = mc.connect(host='db',
                      user='root',
                      password='password',
                      port='3306',
                      database='TradingSystem')
    cursor = conn.cursor()
    return cursor, conn
