import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
import io
import base64
import lightgbm as lgb  # Importar LightGBM
import psycopg2

class MLModel:
    def __init__(self, conexion):
        self.conexion = conexion

    def cargar_datos(self):
        try:
            query = "SELECT * FROM pedidos"
            df = pd.read_sql_query(query, self.conexion)

            # Convertir la fecha de pedido a un número ordinal
            df['fecha_pedido'] = pd.to_datetime(df['fecha_pedido'])
            df['fecha_ordinal'] = df['fecha_pedido'].map(lambda date: date.toordinal())

            # Codificar las variables categóricas (plato y cliente) utilizando one-hot encoding
            df_encoded = pd.get_dummies(df, columns=['codigo_plato', 'id_cliente'], drop_first=True)
            return df, df_encoded
        except (psycopg2.DatabaseError, pd.io.sql.DatabaseError) as e:
            print(f"Error al cargar los datos: {e}")
            return None, None

    def entrenar_modelo_y_proyectar(self):
        df, df_encoded = self.cargar_datos()
        if df is None or df_encoded is None:
            return None  # Terminar si hubo un error al cargar los datos

        try:
            # Seleccionar características (features) y etiqueta (target)
            X = df_encoded[['fecha_ordinal', 'cantidad'] + [col for col in df_encoded.columns if 'codigo_plato_' in col or 'id_cliente_' in col]]
            y = df_encoded['total']

            # Dividir los datos en conjuntos de entrenamiento y prueba
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            # Entrenar el modelo usando LightGBM en lugar de Random Forest
            model = lgb.LGBMRegressor(n_estimators=100, n_jobs=-1, random_state=42)
            model.fit(X_train, y_train)

            # Predecir en el conjunto de prueba
            y_pred = model.predict(X_test)

            # Evaluar el modelo
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            print("MSE y R2:", mse, r2)

            # Visualizar la comparación entre los valores reales y las predicciones como una imagen
            plt.figure()
            plt.scatter(y_test, y_pred, alpha=0.3)
            plt.plot([min(y_test), max(y_test)], [min(y_test), max(y_test)], '--r')
            plt.xlabel('Valores Reales')
            plt.ylabel('Predicciones')
            plt.title('Real vs Predicción')

            # Convertir la gráfica a una imagen en base64
            img = io.BytesIO()
            plt.savefig(img, format='png')
            img.seek(0)
            plot_url = base64.b64encode(img.getvalue()).decode()

            # Predecir valores futuros
            future_dates = pd.date_range(start='2024-01-01', end='2025-12-31', freq='M')
            future_ordinal = np.array([date.toordinal() for date in future_dates]).reshape(-1, 1)

            # Crear un DataFrame para futuras predicciones (usando cantidad promedio)
            future_df = pd.DataFrame({
                'fecha_ordinal': future_ordinal.flatten(),
                'cantidad': np.linspace(np.mean(df['cantidad']), np.mean(df['cantidad']) * 1.5, len(future_ordinal))  # Simular un crecimiento en cantidad
            })

            # Añadir las columnas de platos y clientes codificados, podrías probar rellenando con diferentes valores en lugar de ceros
            for col in [col for col in df_encoded.columns if 'codigo_plato_' in col or 'id_cliente_' in col]:
                future_df[col] = 0  # Aquí podrías también variar los valores en lugar de usar solo ceros

            # Generar predicciones con el nuevo DataFrame
            future_predictions = model.predict(future_df)

            # Mostrar las predicciones futuras
            proyeccion = pd.DataFrame({'fecha': future_dates, 'prediccion_total': future_predictions})
            print(proyeccion)

            # Devolver métricas y proyecciones junto con la imagen
            return {
                'mse': mse,
                'r2': r2,
                'proyeccion': proyeccion.to_dict(orient='records'),
                'plot_url': plot_url  # Devolver la imagen en base64 para ser usada en la vista
            }
        except Exception as e:
            print(f"Error durante el entrenamiento o la proyección: {e}")
            return None
