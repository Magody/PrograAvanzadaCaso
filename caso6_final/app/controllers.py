import time
import threading
from flask import Blueprint, request, render_template
from .models import DataLoader
from statistics import mean, mode, StatisticsError
from collections import Counter
import pandas as pd

# Crear un blueprint para la aplicación principal
bp = Blueprint('main', __name__)

# Instanciar el cargador de datos
data_loader = DataLoader()

# Función para buscar un pedido en una parte específica de la lista
def buscar_pedido_en_parte(parte, id_pedido, resultados, lock):
    for pedido in parte:
        if pedido.id_pedido == id_pedido:
            with lock:
                resultados.append(pedido)
            return

# Función para procesar la búsqueda de pedidos de manera concurrente usando múltiples hilos
def procesar_busqueda_concurrente(id_pedido, num_hilos=4):
    # Dividir los datos en partes iguales para cada hilo
    tamaño_parte = len(data_loader.pedidos) // num_hilos
    hilos = []
    resultados = []
    lock = threading.Lock()
    
    for i in range(num_hilos):
        inicio = i * tamaño_parte
        fin = len(data_loader.pedidos) if i == num_hilos - 1 else (i + 1) * tamaño_parte
        parte = data_loader.pedidos[inicio:fin]
        
        # Crear y lanzar un hilo para buscar el pedido en la parte correspondiente
        hilo = threading.Thread(target=buscar_pedido_en_parte, args=(parte, id_pedido, resultados, lock))
        hilos.append(hilo)
        hilo.start()
    
    # Esperar a que todos los hilos terminen
    for hilo in hilos:
        hilo.join()
    
    return resultados

# Ruta principal de la aplicación
@bp.route('/')
def index():
    return render_template('index.html')

# Ruta para realizar la búsqueda de pedidos
@bp.route('/search')
def search():
    # Obtener el ID del pedido de los parámetros de consulta
    id_pedido = request.args.get('id_pedido')
    
    if not id_pedido:
        return "No se proporcionó el id del pedido", 400

    print(f"ID de pedido recibido: {id_pedido}")

    # Medir el tiempo de carga de datos
    start_time = time.time()
    data_loader.load_data()
    data_load_time = time.time() - start_time

    # Calcular estadísticas descriptivas de los pedidos
    all_totals = [pedido.total for pedido in data_loader.pedidos]
    total_sum = sum(all_totals)
    total_mean = mean(all_totals) if all_totals else 0
    total_max = max(all_totals) if all_totals else 0
    total_min = min(all_totals) if all_totals else 0
    try:
        total_mode = mode(all_totals) if all_totals else 0
    except StatisticsError:
        total_mode = 0  # No hay moda en caso de error

    # Crear un diccionario con las estadísticas
    stats = {
        'total_sum': total_sum,
        'total_mean': total_mean,
        'total_max': total_max,
        'total_min': total_min,
        'total_mode': total_mode
    }

    # Calcular la cantidad de pedidos por año usando pandas
    df_pedidos = pd.DataFrame([pedido.__dict__ for pedido in data_loader.pedidos])
    try:
        df_pedidos['fecha_pedido'] = pd.to_datetime(df_pedidos['fecha_pedido'], errors='coerce', infer_datetime_format=True)
    except Exception as e:
        print(f"Error al convertir fechas: {e}")
    
    df_pedidos['anio'] = df_pedidos['fecha_pedido'].dt.year
    pedidos_por_anio = df_pedidos['anio'].value_counts().to_dict()

    # Encontrar los 3 platos más vendidos
    platos_vendidos = [pedido.codigo_plato for pedido in data_loader.pedidos]
    conteo_platos = Counter(platos_vendidos)
    platos_mas_vendidos = conteo_platos.most_common(3)
    top_platos = [{'codigo_plato': plato[0], 'cantidad': plato[1]} for plato in platos_mas_vendidos]

    # Medir el tiempo de búsqueda
    search_start_time = time.time()
    resultados = procesar_busqueda_concurrente(id_pedido)
    search_end_time = time.time()
    search_time = search_end_time - search_start_time

    # Verificar si se encontraron resultados
    if resultados:
        # Suponiendo que hay un solo pedido con ese ID
        pedido_info = resultados[0]  
        cliente_info = next((cliente for cliente in data_loader.clientes if cliente.id_cliente == pedido_info.id_cliente), None)
        plato_info = next((plato for plato in data_loader.menu if plato.codigo_plato == pedido_info.codigo_plato), None)
        
        print(f"Pedido encontrado: {pedido_info}")
        print(f"Información del cliente: {cliente_info}")
        print(f"Información del plato: {plato_info}")
        
        # Renderizar la plantilla de resultados con la información encontrada
        return render_template('results.html', 
                               pedido=pedido_info, 
                               cliente=cliente_info, 
                               plato=plato_info, 
                               search_time=search_time, 
                               data_load_time=data_load_time, 
                               stats=stats,
                               pedidos_por_anio=pedidos_por_anio,
                               top_platos=top_platos)
    else:
        # Si el pedido no se encuentra, mostrar un mensaje de error
        return render_template('results.html', 
                               search_time=search_time, 
                               data_load_time=data_load_time, 
                               stats=stats,  # Pasar stats incluso en caso de error
                               pedidos_por_anio=pedidos_por_anio,
                               top_platos=top_platos,
                               error="Pedido no encontrado"), 404
