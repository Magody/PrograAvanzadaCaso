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

# Función para generar un código de plato aleatorio
def generar_codigo_plato():
    letras = ''.join(random.choices(string.ascii_uppercase, k=3))
    numeros = ''.join(random.choices(string.digits, k=3))
    return letras + numeros

# Función para generar un nombre de plato aleatorio
def generar_nombre_plato():
    nombres = ["Pasta", "Pizza", "Tacos", "Sushi", "Hamburguesa", "Ensalada", "Sopa", "Pollo", "Carne", "Pescado"]
    return random.choice(nombres)

# Función para generar una categoría aleatoria
def generar_categoria():
    categorias = ["Italiana", "Mexicana", "Japonesa", "Americana", "Saludable", "Rápida"]
    return random.choice(categorias)

# Función para generar un precio aleatorio
def generar_precio():
    return round(random.uniform(5.00, 20.00), 2)

# Función para insertar platos en la tabla 'menu'
def insertar_platos(cantidad, conexion):
    cursor = conexion.cursor()

    for _ in range(cantidad):
        codigo_plato = generar_codigo_plato()
        nombre_plato = generar_nombre_plato()
        categoria = generar_categoria()
        precio = generar_precio()

        try:
            cursor.execute("""
                INSERT INTO menu (codigo_plato, nombre_plato, categoria, precio)
                VALUES (%s, %s, %s, %s)
            """, (codigo_plato, nombre_plato, categoria, precio))
            conexion.commit()
        except psycopg2.IntegrityError:
            conexion.rollback()
            print(f"El código de plato {codigo_plato} ya existe. Generando un nuevo código...")
    
    cursor.close()


cantidad = input("Escriba el número de platos en el menú a generar: ")
try:
    cantidad = int(cantidad)
    conexion = get_connect()
    try:
        insertar_platos(cantidad, conexion)
        print(f"{cantidad} platos generados para el menú e insertados correctamente.")
    except Exception as error:
        print("Ha ocurrido un error: ", error)
    finally:
        conexion.close()
        end_time = time.time()
        elapsed_time = end_time - start_time

        print(f"Tiempo de ejecución: {elapsed_time:.2f} segundos")
except Exception as error_input:
    print("La cantidad debe ser un número!")
