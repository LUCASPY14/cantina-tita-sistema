import MySQLdb

conn = MySQLdb.connect(host='localhost', user='root', passwd='L01G05S33Vice.42', db='cantinatitadb')
cursor = conn.cursor()

cursor.execute('DESCRIBE pagos_venta')
print('PAGOS_VENTA:')
for row in cursor.fetchall():
    print(f'{row[0]} {row[1]}')

cursor.execute('SHOW TABLES LIKE "%precio%"')
print('\nTABLAS CON PRECIO:')
for row in cursor.fetchall():
    print(row[0])

conn.close()
