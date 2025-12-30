import pymysql

conn = pymysql.connect(host='localhost', user='root', password='', database='cantinatitadb')
cursor = conn.cursor()

print("\n=== ESTRUCTURA REAL DE LA TABLA cargas_saldo ===\n")
cursor.execute("DESCRIBE cargas_saldo")
for row in cursor.fetchall():
    print(f"{row[0]:25} {row[1]:30} {row[2]:10} {row[3]:10} {row[4]:10} {row[5]}")

print("\n=== FIN ===\n")
conn.close()
