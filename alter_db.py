import mysql.connector

# Connect to the database
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="123456789",
    database="user"
)

cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE business_record ADD COLUMN latitude FLOAT")
    cursor.execute("ALTER TABLE business_record ADD COLUMN longitude FLOAT")
    conn.commit()
    print("Successfully added latitude and longitude columns to business_record.")
except mysql.connector.Error as err:
    print(f"Error: {err}")

cursor.close()
conn.close()
