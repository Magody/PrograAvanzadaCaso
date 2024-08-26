from flask import Flask, render_template, request
from models.prestamo import PrestamoManager
from concurrent.futures import ThreadPoolExecutor
import time

app = Flask(__name__)

# Obtener una instancia singleton del gestor de préstamos
prestamo_manager = PrestamoManager.get_instance()

# Crear un ejecutor de hilos para la carga de datos
executor = ThreadPoolExecutor(max_workers=1)  # Solo necesitamos un hilo para la carga de datos

@app.route('/', methods=['GET', 'POST'])
def index():
    # Obtener los parámetros de búsqueda del libro y el número de libros/temáticas más solicitados
    nombre_del_libro = request.args.get('nombre_del_libro', '').strip()
    try:
        top_n_books = int(request.args.get('top_n_books', '10'))
    except ValueError:
        top_n_books = 10  # Valor predeterminado en caso de error

    try:
        top_n_themes = int(request.args.get('top_n_themes', '5'))
    except ValueError:
        top_n_themes = 5  # Valor predeterminado en caso de error

    # Inicializar variables para los resultados de búsqueda y tiempos de carga
    registros, max_dias_prestamo, promedio_dias_prestamo, search_results = (None, None, None, None)
    data_load_time = None
    search_time = None

    if nombre_del_libro:
        # Medir el tiempo de carga de datos usando concurrencia
        future = executor.submit(load_data)
        start_time = time.time()
        
        try:
            future.result()  # Esperar a que la carga de datos termine
            data_load_time = time.time() - start_time  # Calcular el tiempo de carga de datos
        except Exception as e:
            data_load_time = 'Error en la carga de datos'
            print(f"Excepción controlada durante la carga de datos: {e}")

        # Medir el tiempo de búsqueda del libro
        start_search_time = time.time()
        try:
            # Buscar libro y calcular estadísticas
            registros, max_dias_prestamo, promedio_dias_prestamo, search_results = prestamo_manager.buscar_libro_y_calcular_estadisticas(nombre_del_libro)
            search_time = time.time() - start_search_time  # Calcular el tiempo de búsqueda
        except Exception as e:
            search_time = 'Error en la búsqueda'
            print(f"Excepción controlada al buscar libro y calcular estadísticas: {e}")

    try:
        # Obtener los libros más solicitados y las temáticas más solicitadas
        top_books = prestamo_manager.get_top_books(top_n=top_n_books)
        top_themes = prestamo_manager.get_top_themes(top_n=top_n_themes)
    except Exception as e:
        print(f"Excepción controlada al obtener libros y temáticas: {e}")
        top_books = top_themes = None

    # Renderizar la plantilla con los resultados y tiempos de carga
    return render_template(
        "index.html",
        registros=registros,
        max_dias_prestamo=max_dias_prestamo,
        promedio_dias_prestamo=promedio_dias_prestamo,
        search_results=search_results,
        top_books=top_books,
        top_themes=top_themes,
        total_registros=len(prestamo_manager.dataframe),
        mean_dias_prestamo=prestamo_manager.promedio_dias_prestamo(),
        data_load_time=data_load_time,
        search_time=search_time,
        top_n_books=top_n_books,
        top_n_themes=top_n_themes
    )

@app.route("/historial")
def show_table():
    # Mostrar el historial completo de préstamos
    return render_template(
        "historial.html", table=prestamo_manager.dataframe.to_html(index=False)
    )

def load_data():
    try:
        # Cargar los datos en el DataFrame
        prestamo_manager._load_data()
    except Exception as e:
        print(f"Excepción controlada en la carga de datos: {e}")

if __name__ == "__main__":
    app.run(debug=True)
