from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd

app = Flask(__name__)

df = pd.read_csv("./data/prestamos.csv")
# df_records = df.to_dict(orient='records')

@app.route('/')
def index():

    # Limpiando
    df['Fecha de préstamo'] = pd.to_datetime(df['Fecha de préstamo'])
    df['Fecha de devolución'] = pd.to_datetime(df['Fecha de devolución'])

    # Calcular estadísticas descriptivas
    df['Días de préstamo'] = (df['Fecha de devolución'] - df['Fecha de préstamo']).dt.days
    max_dias_prestamo = df['Días de préstamo'].max()
    promedio_dias_prestamo = df['Días de préstamo'].mean()

    return render_template('index.html', 
                            registros=len(df), 
                            max_dias_prestamo=max_dias_prestamo, 
                            promedio_dias_prestamo=promedio_dias_prestamo)

# Ruta para mostrar la tabla completa
@app.route('/historial')
def show_table():
    # Recuperar el DataFrame de la sesión
    return render_template('historial.html', table=df.to_html(index=False))

if __name__ == '__main__':
    app.run(debug=True)