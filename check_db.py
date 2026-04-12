import MySQLdb
try:
    db=MySQLdb.connect(host='localhost', user='root', passwd='123456789', db='user')
    cur=db.cursor()
    cur.execute('DESCRIBE business_record')
    columns = [col[0] for col in cur.fetchall()]
    print(f"COLUMNS: {columns}")
    db.close()
except Exception as e:
    print(f"ERROR: {e}")
