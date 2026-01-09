import pymysql

db_host = "localhost"
db_user = "root"
db_password = "yourpassword"  # Replace with your MySQL password
db_name = "course_reviews"  # Replace with your database name

try:
    connection = pymysql.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name,
        cursorclass=pymysql.cursors.DictCursor
    )
    print("✅ Successfully connected to MySQL!")
    connection.close()
except Exception as e:
    print("❌ Failed to connect to MySQL:", e)