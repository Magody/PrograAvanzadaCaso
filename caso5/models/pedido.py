# models/pedido.py
from models.dtos import PedidoDTO
import random
from datetime import datetime, timedelta

class Pedido:
    def __init__(self, conexion):
        self.conexion = conexion

    def obtener_todos_los_pedidos(self):
        cursor = self.conexion.cursor()
        cursor.execute("SELECT * FROM pedidos")
        pedidos = cursor.fetchall()
        cursor.close()
        return pedidos

    def obtener_platos(self):
        cursor = self.conexion.cursor()
        cursor.execute("SELECT codigo_plato, precio FROM menu")
        platos = cursor.fetchall()
        cursor.close()
        return platos

    def obtener_clientes(self):
        cursor = self.conexion.cursor()
        cursor.execute("SELECT id_cliente FROM clientes")
        clientes = cursor.fetchall()
        cursor.close()
        return [cliente[0] for cliente in clientes]

    def generar_fecha_pedido(self):
        now = datetime.now()
        dias_atras = random.randint(0, 365)  # Generar una fecha en el último año
        return now - timedelta(days=dias_atras)

    def insertar_pedidos(self, cantidad):
        platos = self.obtener_platos()
        clientes = self.obtener_clientes()

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

            cursor.execute("""
                INSERT INTO pedidos (codigo_plato, id_cliente, fecha_pedido, cantidad, total)
                VALUES (%s, %s, %s, %s, %s)
            """, (dto.codigo_plato, dto.id_cliente, dto.fecha_pedido, dto.cantidad, dto.total))

        self.conexion.commit()
        cursor.close()
