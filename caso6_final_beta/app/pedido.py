import pandas as pd

class Pedido:
    def __init__(self, id_pedido, codigo_plato, id_cliente, fecha_pedido, cantidad, total):
        self.id_pedido = id_pedido
        self.codigo_plato = codigo_plato
        self.id_cliente = id_cliente
        self.fecha_pedido = fecha_pedido
        self.cantidad = cantidad
        self.total = total

    @staticmethod
    def load_pedidos(filepath):
        df = pd.read_csv(filepath)
        return [Pedido(row['id_pedido'], row['codigo_plato'], row['id_cliente'], row['fecha_pedido'], row['cantidad'], row['total']) for _, row in df.iterrows()]
