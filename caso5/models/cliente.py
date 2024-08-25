from models.dtos import ClienteDTO
import random
import psycopg2

class Cliente:
    def __init__(self, conexion):
        self.conexion = conexion

    def generar_nombre_cliente(self):
        nombres = ["Carlos", "María", "Juan", "Ana", "Luis", "Sofía", "Pedro", "Lucía", "Miguel", "Elena"]
        apellidos = ["García", "Martínez", "Rodríguez", "López", "Pérez", "Gómez", "Sánchez", "Díaz", "Fernández", "Ramírez"]
        return f"{random.choice(nombres)} {random.choice(apellidos)}"

    def insertar_clientes(self, cantidad):
        cursor = self.conexion.cursor()

        for _ in range(cantidad):
            dto = ClienteDTO(
                id_cliente=None,  # El id_cliente será generado por la base de datos
                nombre_cliente=self.generar_nombre_cliente()
            )

            try:
                cursor.execute("""
                    INSERT INTO clientes (nombre_cliente)
                    VALUES (%s)
                """, (dto.nombre_cliente,))
                self.conexion.commit()
            except psycopg2.IntegrityError:
                self.conexion.rollback()
                print(f"El cliente {dto.nombre_cliente} ya existe. Generando un nuevo nombre...")
        
        cursor.close()
