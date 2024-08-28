class Pedido:
    def __init__(self, id_pedido, codigo_plato, id_cliente, fecha_pedido, cantidad, total):
        self.id_pedido = str(id_pedido)  # Asegúrate de convertir a cadena si es necesario
        self.codigo_plato = codigo_plato
        self.id_cliente = id_cliente
        self.fecha_pedido = fecha_pedido
        self.cantidad = cantidad
        self.total = total

    def __repr__(self):
        return f"<Pedido {self.id_pedido}>"
