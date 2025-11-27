import MySQLdb

conn = MySQLdb.connect(host='localhost', user='root', passwd='L01G05S33Vice.42', db='cantinatitadb')
cursor = conn.cursor()

cursor.execute('DESCRIBE historico_precios')
print('HISTORICO_PRECIOS:')
for row in cursor.fetchall():
    print(f'{row[0]} {row[1]}')

cursor.execute('DESCRIBE medios_pago')
print('\nMEDIOS_PAGO:')
for row in cursor.fetchall():
    print(f'{row[0]} {row[1]}')

conn.close()
