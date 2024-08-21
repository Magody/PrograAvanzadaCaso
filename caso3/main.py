from flask import Flask, render_template, request
from models.prestamo import PrestamoManager

app = Flask(__name__)

prestamo_manager = PrestamoManager.get_instance()

@app.route('/', methods=['GET', 'POST'])
def index():
    nombre_del_libro = request.args.get('nombre_del_libro', '').strip()
    top_n_books = int(request.args.get('top_n_books', 10))
    top_n_themes = int(request.args.get('top_n_themes', 5))

    registros, max_dias_prestamo, promedio_dias_prestamo, search_results = (None, None, None, None)

    if nombre_del_libro:
        registros, max_dias_prestamo, promedio_dias_prestamo, search_results = prestamo_manager.buscar_libro_y_calcular_estadisticas(nombre_del_libro)

    top_books = prestamo_manager.get_top_books(top_n=top_n_books)
    top_themes = prestamo_manager.get_top_themes(top_n=top_n_themes)

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
        top_n_books=top_n_books,
        top_n_themes=top_n_themes
    )

@app.route("/historial")
def show_table():
    return render_template(
        "historial.html", table=prestamo_manager.dataframe.to_html(index=False)
    )

if __name__ == "__main__":
    app.run(debug=True)
