import pandas as pd

class Pedido:
    def __init__(self, id_pedido, codigo_plato, id_cliente, fecha_pedido, cantidad, total):
        self.id_pedido = id_pedido
        self.codigo_plato = codigo_plato
        self.id_cliente = id_cliente
        self.fecha_pedido = fecha_pedido
        self.cantidad = cantidad
        self.total = total

class Cliente:
    def __init__(self, id_cliente, nombre_cliente):
        self.id_cliente = id_cliente
        self.nombre_cliente = nombre_cliente

class Plato:
    def __init__(self, codigo_plato, nombre_plato, categoria, precio):
        self.codigo_plato = codigo_plato
        self.nombre_plato = nombre_plato
        self.categoria = categoria
        self.precio = precio

class DataLoader:
    def __init__(self):
        self.pedidos = []
        self.clientes = []
        self.menu = []

    def load_data(self):
        # Cargar datos de CSV
        df_pedidos = pd.read_csv('data/pedidos.csv')
        df_clientes = pd.read_csv('data/clientes.csv')
        df_menu = pd.read_csv('data/menu.csv')
        
        # Crear instancias de las clases
        self.pedidos = [Pedido(**row) for _, row in df_pedidos.iterrows()]
        self.clientes = [Cliente(**row) for _, row in df_clientes.iterrows()]
        self.menu = [Plato(**row) for _, row in df_menu.iterrows()]
