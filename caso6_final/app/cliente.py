class Cliente:
    def __init__(self, id_cliente, nombre_cliente):
        self.id_cliente = id_cliente
        self.nombre_cliente = nombre_cliente

    def __repr__(self):
        return f"<Cliente {self.nombre_cliente}>"
