from models.dtos import MenuDTO
import random
import string
import psycopg2

class Menu:
    def __init__(self, conexion):
        self.conexion = conexion

    def generar_codigo_plato(self):
        letras = ''.join(random.choices(string.ascii_uppercase, k=3))
        numeros = ''.join(random.choices(string.digits, k=3))
        return letras + numeros

    def generar_nombre_plato(self):
        nombres = ["Pasta", "Pizza", "Tacos", "Sushi", "Hamburguesa", "Ensalada", "Sopa", "Pollo", "Carne", "Pescado"]
        return random.choice(nombres)

    def generar_categoria(self):
        categorias = ["Italiana", "Mexicana", "Japonesa", "Americana", "Saludable", "Rápida"]
        return random.choice(categorias)

    def generar_precio(self):
        return round(random.uniform(5.00, 20.00), 2)

    def insertar_platos(self, cantidad):
        try:
            cursor = self.conexion.cursor()
        except psycopg2.DatabaseError as e:
            print(f"Error al crear el cursor: {e}")
            return

        for _ in range(cantidad):
            dto = MenuDTO(
                codigo_plato=self.generar_codigo_plato(),
                nombre_plato=self.generar_nombre_plato(),
                categoria=self.generar_categoria(),
                precio=self.generar_precio()
            )

            try:
                cursor.execute("""
                    INSERT INTO menu (codigo_plato, nombre_plato, categoria, precio)
                    VALUES (%s, %s, %s, %s)
                """, (dto.codigo_plato, dto.nombre_plato, dto.categoria, dto.precio))
                self.conexion.commit()
            except psycopg2.IntegrityError:
                self.conexion.rollback()
                print(f"El código de plato {dto.codigo_plato} ya existe. Generando un nuevo código...")
            except psycopg2.DatabaseError as e:
                self.conexion.rollback()
                print(f"Error al insertar el plato {dto.codigo_plato}: {e}")

        try:
            cursor.close()
        except psycopg2.DatabaseError as e:
            print(f"Error al cerrar el cursor: {e}")
