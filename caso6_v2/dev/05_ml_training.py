import time

# Iniciar el contador de tiempo
start_time = time.time()

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt

# Cargar los datos desde el archivo CSV
df = pd.read_csv('./data/datos_historicos_pedidos.csv')

# Convertir la fecha de pedido a un número ordinal que represente los días desde una fecha inicial
df['fecha_pedido'] = pd.to_datetime(df['fecha_pedido'])
df['fecha_ordinal'] = df['fecha_pedido'].map(lambda date: date.toordinal())

# Codificar las variables categóricas (plato y cliente) utilizando one-hot encoding
df_encoded = pd.get_dummies(df, columns=['codigo_plato', 'id_cliente'], drop_first=True)

# Seleccionar características (features) y etiqueta (target)
X = df_encoded[['fecha_ordinal', 'cantidad'] + [col for col in df_encoded.columns if 'codigo_plato_' in col or 'id_cliente_' in col]]
y = df_encoded['total']

# Dividir los datos en conjuntos de entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Entrenar el modelo de Random Forest
model = RandomForestRegressor(n_estimators=10, random_state=42)
model.fit(X_train, y_train)

# Predecir en el conjunto de prueba
y_pred = model.predict(X_test)

# Evaluar el modelo
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"Mean Squared Error: {mse}")
print(f"R^2 Score: {r2}")

# Visualizar la comparación entre los valores reales y las predicciones
plt.scatter(y_test, y_pred, alpha=0.3)
plt.plot([min(y_test), max(y_test)], [min(y_test), max(y_test)], '--r')
plt.xlabel('Valores Reales')
plt.ylabel('Predicciones')
plt.title('Real vs Predicción')
plt.show()

# (Opcional) Predecir valores futuros
future_dates = pd.date_range(start='2025-01-01', end='2025-03-31', freq='M')
future_ordinal = np.array([date.toordinal() for date in future_dates]).reshape(-1, 1)

# Crear un DataFrame para futuras predicciones (usando cantidad promedio)
future_df = pd.DataFrame({
    'fecha_ordinal': future_ordinal.flatten(),
    'cantidad': np.mean(df['cantidad'])  # Usar la cantidad promedio
})

# Añadir las columnas de platos y clientes codificados, rellenando con 0 (asumiendo un nuevo cliente/plato)
for col in [col for col in df_encoded.columns if 'codigo_plato_' in col or 'id_cliente_' in col]:
    future_df[col] = 0

future_predictions = model.predict(future_df)

# Mostrar las predicciones futuras
proyeccion = pd.DataFrame({'fecha': future_dates, 'prediccion_total': future_predictions})
print(proyeccion)


end_time = time.time()
elapsed_time = end_time - start_time

print(f"Tiempo de ejecución: {elapsed_time:.2f} segundos")