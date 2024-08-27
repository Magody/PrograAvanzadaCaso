import pandas as pd

class Cliente:
    def __init__(self, id_cliente, nombre_cliente):
        self.id_cliente = id_cliente
        self.nombre_cliente = nombre_cliente

    @staticmethod
    def load_clientes(filepath):
        df = pd.read_csv(filepath)
        return [Cliente(row['id_cliente'], row['nombre_cliente']) for _, row in df.iterrows()]
