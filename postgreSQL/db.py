import psycopg2
def get_connenction():
    try:
        conn = psycopg2.connect(
            host='localhost',
            database='user_database',
            user='postgres',
            password='user_password',
            port='port_number'
        )
        return conn
    except Exception as e:
        print("database error",e)    

