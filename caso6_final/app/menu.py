class Menu:
    def __init__(self, codigo_plato, nombre_plato, categoria, precio):
        self.codigo_plato = codigo_plato
        self.nombre_plato = nombre_plato
        self.categoria = categoria
        self.precio = precio

    def __repr__(self):
        return f"<Menu {self.codigo_plato}>"
