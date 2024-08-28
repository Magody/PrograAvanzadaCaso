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

def obtener_platos(conexion):
    cursor = conexion.cursor()
    cursor.execute("SELECT codigo_plato, precio FROM menu")
    platos = cursor.fetchall()
    cursor.close()
    return platos

def obtener_clientes(conexion):
    cursor = conexion.cursor()
    cursor.execute("SELECT id_cliente FROM clientes")
    clientes = cursor.fetchall()
    cursor.close()
    return [cliente[0] for cliente in clientes]

def generar_fecha_pedido():
    now = datetime.now()
    dias_atras = random.randint(0, 365)  # Generar una fecha en el último año
    return now - timedelta(days=dias_atras)

def insertar_pedidos(cantidad, conexion):
    platos = obtener_platos(conexion)
    clientes = obtener_clientes(conexion)

    cursor = conexion.cursor()

    for _ in range(cantidad):
        codigo_plato, precio_plato = random.choice(platos)
        id_cliente = random.choice(clientes)
        fecha_pedido = generar_fecha_pedido()
        cantidad = random.randint(1, 5)
        total = round(precio_plato * cantidad, 2)

        cursor.execute("""
            INSERT INTO pedidos (codigo_plato, id_cliente, fecha_pedido, cantidad, total)
            VALUES (%s, %s, %s, %s, %s)
        """, (codigo_plato, id_cliente, fecha_pedido, cantidad, total))

    conexion.commit()
    cursor.close()


cantidad = input("Escriba el número de pedidos a generar: ")
try:
    cantidad = int(cantidad)
    conexion = get_connect()
    
    try:
        insertar_pedidos(cantidad, conexion)
        print(f"{cantidad} pedidos generados e insertados correctamente.")
    except Exception as error:
        print("Ha ocurrido un error: ", error)
    finally:
        conexion.close()
        end_time = time.time()
        elapsed_time = end_time - start_time

        print(f"Tiempo de ejecución: {elapsed_time:.2f} segundos")
except Exception as error_input:
    print("La cantidad debe ser un número!")
