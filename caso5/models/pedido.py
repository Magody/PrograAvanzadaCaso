# models/pedido.py
from models.dtos import PedidoDTO
import random
from datetime import datetime, timedelta
import psycopg2

class Pedido:
    def __init__(self, conexion):
        self.conexion = conexion

    def obtener_todos_los_pedidos(self):
        try:
            cursor = self.conexion.cursor()
            cursor.execute("SELECT * FROM pedidos")
            pedidos = cursor.fetchall()
            cursor.close()
            return pedidos
        except psycopg2.DatabaseError as e:
            print(f"Error al obtener todos los pedidos: {e}")
            return []

    def obtener_platos(self):
        try:
            cursor = self.conexion.cursor()
            cursor.execute("SELECT codigo_plato, precio FROM menu")
            platos = cursor.fetchall()
            cursor.close()
            return platos
        except psycopg2.DatabaseError as e:
            print(f"Error al obtener los platos: {e}")
            return []

    def obtener_clientes(self):
        try:
            cursor = self.conexion.cursor()
            cursor.execute("SELECT id_cliente FROM clientes")
            clientes = cursor.fetchall()
            cursor.close()
            return [cliente[0] for cliente in clientes]
        except psycopg2.DatabaseError as e:
            print(f"Error al obtener los clientes: {e}")
            return []

    def generar_fecha_pedido(self):
        now = datetime.now()
        dias_atras = random.randint(0, 365)  # Generar una fecha en el último año
        return now - timedelta(days=dias_atras)

    def insertar_pedidos(self, cantidad):
        try:
            platos = self.obtener_platos()
            clientes = self.obtener_clientes()

            if not platos or not clientes:
                print("Error: No se pudo obtener la lista de platos o clientes.")
                return

            cursor = self.conexion.cursor()

            for _ in range(cantidad):
                codigo_plato, precio_plato = random.choice(platos)
                id_cliente = random.choice(clientes)
                fecha_pedido = self.generar_fecha_pedido()
                cantidad_pedido = random.randint(1, 5)
                total = round(precio_plato * cantidad_pedido, 2)

                dto = PedidoDTO(
                    codigo_plato=codigo_plato,
                    id_cliente=id_cliente,
                    fecha_pedido=fecha_pedido,
                    cantidad=cantidad_pedido,
                    total=total
                )

                try:
                    cursor.execute("""
                        INSERT INTO pedidos (codigo_plato, id_cliente, fecha_pedido, cantidad, total)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (dto.codigo_plato, dto.id_cliente, dto.fecha_pedido, dto.cantidad, dto.total))
                except psycopg2.IntegrityError as e:
                    print(f"Error al insertar el pedido: {e}")
                    self.conexion.rollback()
                except psycopg2.DatabaseError as e:
                    print(f"Error de base de datos al insertar el pedido: {e}")
                    self.conexion.rollback()

            self.conexion.commit()
            cursor.close()
        except Exception as e:
            print(f"Error general al insertar pedidos: {e}")
