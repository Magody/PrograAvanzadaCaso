from models.dtos import PedidoDTO
import pandas as pd
import threading
import random
from datetime import datetime, timedelta
import psycopg2
import matplotlib.pyplot as plt
import io
import base64

class Pedido:
    def __init__(self, conexion, archivo_csv="./data/datos_historicos_pedidos.csv", num_hilos=30):
        self.conexion = conexion
        self.archivo_csv = archivo_csv
        self.num_hilos = num_hilos
        self.df_pedidos = pd.DataFrame()
        self.loading = False

        
        self.lock = threading.Lock()

        # Cargar y procesar el archivo CSV de manera concurrente
        try:
            self.df_read = pd.read_csv(self.archivo_csv)
            self._procesar_concurrentemente()
        except Exception as error:
            print(f"Error al cargar los pedidos desde el archivo CSV: {error}")
            self.df_read = pd.DataFrame()

    def get_descriptive(self):
        return self.df_pedidos.describe()

    def obtener_todos_los_pedidos(self):
        try:
            return self.df_pedidos.values.tolist()
        except Exception as e:
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

    def _apply_processing(self, df_part):
        df_part['fecha_pedido'] = pd.to_datetime(df_part['fecha_pedido'])
        df_part['cantidad_por_total'] = df_part['cantidad'] * df_part['total']

    def _procesar_parte(self, df_part):
        """
        Procesa una parte del DataFrame y la concatena al DataFrame principal.
        """
        df_part = df_part.copy()
        self._apply_processing(df_part)
        with self.lock:
            self.df_pedidos = pd.concat([self.df_pedidos, df_part])

    def _procesar_concurrentemente(self):
        """
        Procesa el DataFrame en partes usando múltiples hilos.
        """
        if len(self.df_pedidos) > 0:
            print("Already filled")
            return
        if len(self.df_read) < self.num_hilos:
            self.num_hilos = len(self.df_read)

        self.loading = True
        tamaño_parte = len(self.df_read) // self.num_hilos
        hilos = []

        for i in range(self.num_hilos):
            inicio = i * tamaño_parte
            fin = len(self.df_read) if i == self.num_hilos - 1 else (i + 1) * tamaño_parte
            # print("DEBUG: ", inicio, fin, len(self.df_pedidos))
            df_part = self.df_read.iloc[inicio:fin]

            hilo = threading.Thread(target=self._procesar_parte, args=(df_part,))
            hilos.append(hilo)
            hilo.start()

        for hilo in hilos:
            hilo.join()

        print("DEBUG2: ", inicio, fin, len(self.df_pedidos))
        self.loading = False

    def calcular_estadisticas(self):
        try:
            estadisticas = {}
            hilos = []

            def calcular_operacion(operacion):
                try:
                    if operacion == 'mean':
                        print(f"Calculando {operacion}")
                        estadisticas['mean'] = self.df_pedidos["cantidad_por_total"].mean()
                    elif operacion == 'sum':
                        print(f"Calculando {operacion}")
                        estadisticas['sum'] = self.df_pedidos["cantidad_por_total"].sum()
                    elif operacion == 'min':
                        print(f"Calculando {operacion}")
                        estadisticas['min'] = self.df_pedidos["cantidad_por_total"].min()
                    elif operacion == 'max':
                        print(f"Calculando {operacion}")
                        estadisticas['max'] = self.df_pedidos["cantidad_por_total"].max()
                    elif operacion == 'mode':
                        print(f"Calculando {operacion}")
                        estadisticas['mode'] = self.df_pedidos["codigo_plato"].mode()
                except Exception as e:
                    print(f"Error al calcular {operacion}: {e}")

            operaciones = ['mean', 'sum', 'min', 'max', 'mode']
            for operacion in operaciones:
                hilo = threading.Thread(target=calcular_operacion, args=(operacion,))
                hilos.append(hilo)
                hilo.start()

            for hilo in hilos:
                hilo.join()

            print("Por mes")
            # Agrupación por variable temporal (por ejemplo, por mes)
            self.df_pedidos['mes'] = self.df_pedidos['fecha_pedido'].dt.to_period('M')
            ventas_por_mes = self.df_pedidos.groupby('mes')['cantidad'].sum()

            print("figure start")
            # Generar gráfico de ventas por mes
            plt.figure()
            ventas_por_mes.plot(kind='bar')
            plt.xlabel('Mes')
            plt.ylabel('Cantidad de Ventas')
            plt.title('Ventas por Mes')

            print("figure end")
            # Convertir la gráfica a una imagen en base64
            img = io.BytesIO()
            plt.savefig(img, format='png')
            img.seek(0)
            plot_url = base64.b64encode(img.getvalue()).decode()
            print("figure save")

            # Devolver estadísticas y el gráfico en base64
            return {
                'estadisticas': estadisticas,
                'plot_url': plot_url,
                'sample_data': self.df_pedidos.head().to_dict(orient='records')
            }
        except Exception as e:
            print(f"Error al calcular las estadísticas descriptivas: {e}")
            return {"error": str(e)}

if __name__ == "__main__":
    # Supongamos que tienes una conexión de base de datos ya establecida
    def get_connection():
        """Establece la conexión a la base de datos PostgreSQL."""
        try:
            return psycopg2.connect(
                host="localhost",
                database="postgres",
                user="postgres",
                password="root1234",
                port="5433",
                options='-c client_encoding=UTF8'
            )
        except psycopg2.DatabaseError as e:
            print(f"Error al conectar con la base de datos: {e}")
            return None
    conexion = get_connection()

    # Crea una instancia de Pedido y carga los datos concurrentemente desde el archivo CSV
    pedido_manager = Pedido(conexion)

    # Obtén todos los pedidos cargados desde el archivo CSV y muéstralos
    pedidos = pedido_manager.obtener_todos_los_pedidos()
    print("Pedidos", len(pedidos))
    print(pedido_manager.df_pedidos.head())


