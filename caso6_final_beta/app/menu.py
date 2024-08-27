import pandas as pd

class Plato:
    def __init__(self, codigo_plato, nombre_plato, categoria, precio):
        self.codigo_plato = codigo_plato
        self.nombre_plato = nombre_plato
        self.categoria = categoria
        self.precio = precio

    @staticmethod
    def load_menu(filepath):
        df = pd.read_csv(filepath)
        return [Plato(row['codigo_plato'], row['nombre_plato'], row['categoria'], row['precio']) for _, row in df.iterrows()]
