import psycopg2

try:
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="123456",
        host="127.0.0.1",
        port="5432"
    )
    conn.set_client_encoding('UTF8')
    print("PostgreSQL работает")
except Exception as e:
    print("PostgreSQL не работает", e)