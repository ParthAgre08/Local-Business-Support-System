import MySQLdb
try:
    db=MySQLdb.connect(host='localhost', user='root', passwd='123456789', db='user')
    cur=db.cursor()
    cur.execute('SELECT category, subcategory FROM business_record LIMIT 10')
    rows = cur.fetchall()
    print("DATA:", rows)
    db.close()
except Exception as e:
    print("ERROR:", e)
