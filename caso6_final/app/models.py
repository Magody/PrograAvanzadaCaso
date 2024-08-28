import pandas as pd
from .cliente import Cliente
from .menu import Menu
from .pedido import Pedido

class DataLoader:
    def __init__(self):
        """
        Inicializa una instancia de DataLoader.
        
        Crea listas vacías para almacenar datos de pedidos, clientes y menú.
        """
        self.pedidos = []  # Lista para almacenar instancias de pedidos
        self.clientes = []  # Lista para almacenar instancias de clientes
        self.menu = []  # Lista para almacenar instancias de menú

    def load_data(self):
        """
        Carga datos desde archivos CSV y convierte cada fila en instancias de las clases correspondientes.
        
        Lee los archivos CSV para pedidos, clientes y menú, y almacena los datos en las listas
        de instancias de Pedido, Cliente y Menu.
        """
        try:
            # Leer los archivos CSV en DataFrames de pandas
            df_pedidos = pd.read_csv('data/pedidos.csv')  # Datos de pedidos
            df_clientes = pd.read_csv('data/clientes.csv')  # Datos de clientes
            df_menu = pd.read_csv('data/menu.csv')  # Datos del menú
            
            # Convertir cada fila del DataFrame de pedidos en una instancia de Pedido
            self.pedidos = [
                Pedido(
                    row['id_pedido'],         # ID del pedido
                    row['codigo_plato'],      # Código del plato
                    row['id_cliente'],        # ID del cliente
                    row['fecha_pedido'],      # Fecha del pedido
                    row['cantidad'],          # Cantidad de platos
                    row['total']              # Total del pedido
                ) for _, row in df_pedidos.iterrows()  # Iterar sobre cada fila del DataFrame
            ]
            
            # Convertir cada fila del DataFrame de clientes en una instancia de Cliente
            self.clientes = [
                Cliente(
                    row['id_cliente'],        # ID del cliente
                    row['nombre_cliente']     # Nombre del cliente
                ) for _, row in df_clientes.iterrows()  # Iterar sobre cada fila del DataFrame
            ]
            
            # Convertir cada fila del DataFrame del menú en una instancia de Menu
            self.menu = [
                Menu(
                    row['codigo_plato'],      # Código del plato
                    row['nombre_plato'],       # Nombre del plato
                    row['categoria'],          # Categoría del plato
                    row['precio']              # Precio del plato
                ) for _, row in df_menu.iterrows()  # Iterar sobre cada fila del DataFrame
            ]
        
        except Exception as e:
            # Captura cualquier excepción que ocurra durante la carga de datos
            # e.g., archivo no encontrado, error de formato
            print("Error al cargar datos:", e)
