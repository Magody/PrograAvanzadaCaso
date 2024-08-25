import pandas as pd  # Importa la biblioteca pandas para manipulación de datos
from flask import Flask, render_template, request  # Importa Flask y herramientas para manejar plantillas y solicitudes
from models.prestamo import PrestamoManager  # Importa la clase PrestamoManager desde el módulo models.prestamo
import time  # Importa el módulo time para medir el tiempo

# Crea una instancia de la aplicación Flask
app = Flask(__name__)

# Obtener una instancia singleton del gestor de préstamos
prestamo_manager = PrestamoManager.get_instance()  # Obtiene la única instancia del gestor de préstamos

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Maneja las solicitudes a la ruta principal ('/').
    Permite tanto solicitudes GET como POST.
    """
    # Obtiene el nombre del libro de los parámetros de la solicitud, o usa una cadena vacía por defecto
    nombre_del_libro = request.args.get('nombre_del_libro', '').strip()

    # Intenta obtener el número de libros principales a mostrar desde los parámetros de la solicitud
    try:
        top_n_books = int(request.args.get('top_n_books', '10'))  # Lee el número de libros desde la solicitud (por defecto 10)
    except ValueError:
        top_n_books = 10  # Usa 10 como valor por defecto en caso de error

    # Intenta obtener el número de temáticas principales a mostrar desde los parámetros de la solicitud
    try:
        top_n_themes = int(request.args.get('top_n_themes', '5'))  # Lee el número de temáticas desde la solicitud (por defecto 5)
    except ValueError:
        top_n_themes = 5  # Usa 5 como valor por defecto en caso de error

    # Inicializa variables para almacenar resultados de búsqueda y tiempos de carga
    registros, max_dias_prestamo, promedio_dias_prestamo, search_results = (None, None, None, None)
    data_load_time_without_concurrency = None
    data_load_time_with_concurrency = None
    search_time = None

    if nombre_del_libro:
        # Medir el tiempo de carga de datos sin concurrencia
        start_time = time.time()  # Registra el tiempo de inicio
        prestamo_manager._procesar_sin_concurrencia()  # Procesa los datos sin concurrencia
        data_load_time_without_concurrency = time.time() - start_time  # Calcula el tiempo transcurrido

        # Medir el tiempo de carga de datos con concurrencia
        start_time = time.time()  # Registra el tiempo de inicio
        prestamo_manager._df = pd.read_csv("./data/prestamos_libros.csv")  # Lee el archivo CSV nuevamente
        prestamo_manager._procesar_concurrentemente()  # Procesa los datos con concurrencia
        data_load_time_with_concurrency = time.time() - start_time  # Calcula el tiempo transcurrido

        # Medir el tiempo de búsqueda del libro
        start_search_time = time.time()  # Registra el tiempo de inicio de la búsqueda
        try:
            # Busca el libro y calcula estadísticas
            registros, max_dias_prestamo, promedio_dias_prestamo, search_results = prestamo_manager.buscar_libro_y_calcular_estadisticas(nombre_del_libro)
            search_time = time.time() - start_search_time  # Calcula el tiempo transcurrido en la búsqueda
        except Exception as e:
            search_time = 'Error en la búsqueda'  # Establece un mensaje de error en caso de excepción
            print(f"Excepción controlada al buscar libro y calcular estadísticas: {e}")  # Muestra el error en la consola

    try:
        # Obtiene los libros más solicitados y las temáticas más solicitadas
        top_books = prestamo_manager.get_top_books(top_n=top_n_books)  # Obtiene los libros más prestados
        top_themes = prestamo_manager.get_top_themes(top_n=top_n_themes)  # Obtiene las temáticas más populares
    except Exception as e:
        print(f"Excepción controlada al obtener libros y temáticas: {e}")  # Muestra el error en la consola
        top_books = top_themes = None  # Establece None en caso de error

    # Renderiza la plantilla con los resultados y tiempos de carga
    return render_template(
        "index.html",  # Archivo de plantilla HTML
        registros=registros,  # Número de registros encontrados
        max_dias_prestamo=max_dias_prestamo,  # Máximo número de días de préstamo
        promedio_dias_prestamo=promedio_dias_prestamo,  # Promedio de días de préstamo
        search_results=search_results,  # Resultados de la búsqueda
        top_books=top_books,  # Libros más prestados
        top_themes=top_themes,  # Temáticas más populares
        total_registros=len(prestamo_manager.dataframe),  # Total de registros en el DataFrame
        mean_dias_prestamo=prestamo_manager.promedio_dias_prestamo(),  # Promedio de días de préstamo en el DataFrame
        data_load_time_without_concurrency=data_load_time_without_concurrency,  # Tiempo de carga sin concurrencia
        data_load_time_with_concurrency=data_load_time_with_concurrency,  # Tiempo de carga con concurrencia
        search_time=search_time,  # Tiempo de búsqueda del libro
        top_n_books=top_n_books,  # Número de libros principales solicitados
        top_n_themes=top_n_themes  # Número de temáticas principales solicitadas
    )

@app.route("/historial")
def show_table():
    """
    Muestra el historial completo de préstamos en una tabla.
    """
    return render_template(
        "historial.html",  # Archivo de plantilla HTML
        table=prestamo_manager.dataframe.to_html(index=False)  # Convierte el DataFrame a HTML para mostrar en la plantilla
    )

if __name__ == "__main__":
    # Si el script se ejecuta directamente, inicia la aplicación Flask en modo de depuración
    app.run(debug=True)