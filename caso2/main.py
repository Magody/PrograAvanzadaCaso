from flask import Flask, render_template, request
import pandas as pd
from models.prestamo import PrestamoManager

app = Flask(__name__)

prestamo_manager = PrestamoManager.get_instance()

# Asegúrate de que las fechas estén en el formato correcto y calcular 'Días de préstamo'
prestamo_manager.dataframe['Fecha de préstamo'] = pd.to_datetime(prestamo_manager.dataframe['Fecha de préstamo'])
prestamo_manager.dataframe['Fecha de devolución'] = pd.to_datetime(prestamo_manager.dataframe['Fecha de devolución'])
prestamo_manager.dataframe['Días de préstamo'] = (prestamo_manager.dataframe['Fecha de devolución'] - prestamo_manager.dataframe['Fecha de préstamo']).dt.days

def get_top_books(dataframe, top_n=10):
    return dataframe['Nombre del libro'].value_counts().head(top_n)

def get_top_themes(dataframe, top_n=5):
    return dataframe['Temática del libro'].value_counts().head(top_n)

@app.route('/', methods=['GET', 'POST'])
def index():
    nombre_del_libro = request.args.get('nombre_del_libro', '').strip()
    search_results = None
    registros = None
    max_dias_prestamo = None
    promedio_dias_prestamo = None

    if nombre_del_libro:
        # Filtrar el DataFrame buscando coincidencias en la columna 'Nombre del libro'
        search_results = prestamo_manager.dataframe[
            prestamo_manager.dataframe['Nombre del libro'].str.contains(nombre_del_libro, case=False, na=False)
        ]

        if not search_results.empty:
            # Calcular los análisis solo para los libros encontrados
            registros = len(search_results)
            max_dias_prestamo = search_results['Días de préstamo'].max()
            promedio_dias_prestamo = search_results['Días de préstamo'].mean()

    # Análisis adicional
    top_books = get_top_books(prestamo_manager.dataframe)
    top_themes = get_top_themes(prestamo_manager.dataframe)

    return render_template(
        "index.html",
        registros=registros,
        max_dias_prestamo=max_dias_prestamo,
        promedio_dias_prestamo=promedio_dias_prestamo,
        search_results=search_results,
        top_books=top_books,
        top_themes=top_themes,
        total_registros=len(prestamo_manager.dataframe),
        mean_dias_prestamo=prestamo_manager.dataframe['Días de préstamo'].mean()
    )

@app.route("/historial")
def show_table():
    return render_template(
        "historial.html", table=prestamo_manager.dataframe.to_html(index=False)
    )

if __name__ == "__main__":
    app.run(debug=True)
