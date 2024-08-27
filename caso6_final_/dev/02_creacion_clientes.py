import random
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

# Función para generar un nombre de cliente aleatorio
def generar_nombre_cliente():
    nombres = ["Carlos", "María", "Juan", "Ana", "Luis", "Sofía", "Pedro", "Lucía", "Miguel", "Elena"]
    apellidos = ["García", "Martínez", "Rodríguez", "López", "Pérez", "Gómez", "Sánchez", "Díaz", "Fernández", "Ramírez"]
    return f"{random.choice(nombres)} {random.choice(apellidos)}"

# Función para insertar clientes en la tabla 'clientes'
def insertar_clientes(cantidad, conexion):
    cursor = conexion.cursor()

    for _ in range(cantidad):
        nombre_cliente = generar_nombre_cliente()

        try:
            cursor.execute("""
                INSERT INTO clientes (nombre_cliente)
                VALUES (%s)
            """, (nombre_cliente,))
            conexion.commit()
        except psycopg2.IntegrityError:
            conexion.rollback()
            print(f"El cliente {nombre_cliente} ya existe. Generando un nuevo nombre...")
    
    cursor.close()


cantidad_clientes = input("Escriba el número de clientes a generar: ")
try:
    cantidad_clientes = int(cantidad_clientes)
    conexion = get_connect()
    try:
        insertar_clientes(cantidad_clientes, conexion)
        print(f"{cantidad_clientes} clientes generados e insertados correctamente.")
    except Exception as error:
        print("Ha ocurrido un error: ", error)
    finally:
        conexion.close()
        end_time = time.time()
        elapsed_time = end_time - start_time

        print(f"Tiempo de ejecución: {elapsed_time:.2f} segundos")
except Exception as error_input:
    print("La cantidad debe ser un número!")
