from flask import Flask, render_template, request
from models.menu import Menu
from models.cliente import Cliente
from models.pedido import Pedido
from models.ml_model import MLModel
import psycopg2
import time

app = Flask(__name__)

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

@app.route('/', methods=['GET', 'POST'])
def index():
    mensaje = None
    elapsed_time = None

    if request.method == 'POST':
        start_time = time.time()  # Iniciar medición de tiempo

        try:
            cantidad = int(request.form['cantidad'])
            tipo_datos = request.form['tipo_datos']

            # Establecer conexión
            conexion = get_connection()
            if conexion is None:
                mensaje = "Error al conectar con la base de datos."
                return render_template('index.html', mensaje=mensaje)

            if tipo_datos == 'menu':
                menu = Menu(conexion)
                menu.insertar_platos(cantidad)
                mensaje = f"{cantidad} platos generados e insertados correctamente."
            elif tipo_datos == 'clientes':
                cliente = Cliente(conexion)
                cliente.insertar_clientes(cantidad)
                mensaje = f"{cantidad} clientes generados e insertados correctamente."
            elif tipo_datos == 'pedidos':
                pedido = Pedido(conexion)
                pedido.insertar_pedidos(cantidad)
                mensaje = f"{cantidad} pedidos generados e insertados correctamente."

            conexion.close()
        except (ValueError, psycopg2.DatabaseError) as e:
            mensaje = f"Error al procesar la solicitud: {e}"
        except Exception as e:
            mensaje = f"Ha ocurrido un error inesperado: {e}"

        elapsed_time = time.time() - start_time  # Medir tiempo de ejecución

    return render_template('index.html', mensaje=mensaje, elapsed_time=elapsed_time)

@app.route('/process', methods=['GET'])
def process():
    resultado = None
    elapsed_time = None

    start_time = time.time()  # Iniciar medición de tiempo

    try:
        # Establecer conexión
        conexion = get_connection()
        if conexion is None:
            resultado = {"error": "Error al conectar con la base de datos."}
            return render_template('results.html', resultado=resultado)

        # Verificación de datos en la tabla 'pedidos'
        pedido = Pedido(conexion)
        pedidos_existentes = pedido.obtener_todos_los_pedidos()

        if pedidos_existentes:
            # Si hay datos en 'pedidos', entrenar el modelo
            ml_model = MLModel(conexion)
            resultado = ml_model.entrenar_modelo_y_proyectar()  # Ejecuta el modelo de ML y genera las proyecciones
        else:
            resultado = {"error": "No hay datos suficientes en 'pedidos' para entrenar el modelo de ML."}

        conexion.close()
    except psycopg2.DatabaseError as e:
        resultado = {"error": f"Error en la base de datos: {e}"}
    except Exception as e:
        resultado = {"error": f"Ha ocurrido un error inesperado: {e}"}

    elapsed_time = time.time() - start_time  # Medir tiempo de ejecución

    return render_template('results.html', resultado=resultado, elapsed_time=elapsed_time)

if __name__ == "__main__":
    app.run(debug=True)
