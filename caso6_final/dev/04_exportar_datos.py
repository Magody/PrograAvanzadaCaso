"""
COPY (SELECT * FROM pedidos)
TO 'C:\\Users\\usuario\\Downloads\\datos_historicos_pedidos.csv'
WITH (FORMAT CSV, HEADER TRUE, DELIMITER ',');

ó
"""
import csv
import random
from datetime import datetime, timedelta
import string
import psycopg2
import time

# Iniciar el contador de tiempo
start_time = time.time()

# Conexión a la base de datos PostgreSQL
def get_connect():
    conexion = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="root1234",
        port="5433",
        options='-c client_encoding=UTF8'
    )
    return conexion

# Conexión a la base de datos PostgreSQL
conexion = get_connect()

cursor = conexion.cursor()

# Ejecutar la consulta y guardar el resultado en un archivo CSV
cursor.execute("SELECT * FROM pedidos")
rows = cursor.fetchall()

with open("./data/datos_historicos_pedidos.csv", mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow([desc[0] for desc in cursor.description])  # Escribir encabezados
    writer.writerows(rows)

cursor.close()
conexion.close()
end_time = time.time()
elapsed_time = end_time - start_time

print(f"Tiempo de ejecución: {elapsed_time:.2f} segundos")