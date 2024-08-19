from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
from models.prestamo import PrestamoManager

app = Flask(__name__)

prestamo_manager = PrestamoManager.get_instance()

df = pd.read_csv("./data/prestamos.csv")
# df_records = df.to_dict(orient='records')


@app.route("/")
def index():
    return render_template(
        "index.html",
        registros=len(prestamo_manager.dataframe),
        max_dias_prestamo=prestamo_manager.max_dias_prestamo(),
        promedio_dias_prestamo=prestamo_manager.promedio_dias_prestamo(),
    )


@app.route("/historial")
def show_table():
    return render_template(
        "historial.html", table=prestamo_manager.dataframe.to_html(index=False)
    )


if __name__ == "__main__":
    app.run(debug=True)
