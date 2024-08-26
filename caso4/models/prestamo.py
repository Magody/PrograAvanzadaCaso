import pandas as pd
from datetime import datetime
import concurrent.futures
import time
import threading

class PrestamoManager:
    _instance = None

    @staticmethod
    def get_instance():
        if PrestamoManager._instance is None:
            PrestamoManager()
        return PrestamoManager._instance

    def __init__(self):
        if PrestamoManager._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            PrestamoManager._instance = self
            self._df = pd.DataFrame()
            self._data_load_time = None
            self._data_lock = threading.Lock()
            self._load_data()

    def _load_data(self):
        start_time = time.time()
        try:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                # Cargar datos, limpiar datos y calcular estadísticas en hilos separados
                future_df = executor.submit(self._read_csv)
                self._df = future_df.result()
                future_clean_data = executor.submit(self._clean_data)
                future_clean_data.result()
                future_calculate_stats = executor.submit(self._calculate_statistics)
                future_calculate_stats.result()
        except Exception as e:
            print(f"Error en la carga de datos concurrente: {e}")
        finally:
            end_time = time.time()
            self._data_load_time = end_time - start_time  # Guardar el tiempo total de carga de datos
            if self._df.empty:
                print("DataFrame vacío generado debido a un error en la lectura o procesamiento de los datos.")

    def _read_csv(self):
        try:
            return pd.read_csv("./data/prestamos_libros.csv")
        except Exception as e:
            print(f"Error al leer el archivo CSV: {e}")
            return pd.DataFrame()

    def _clean_data(self):
        try:
            self._df['Fecha de préstamo'] = pd.to_datetime(self._df['Fecha de préstamo'])
            self._df['Fecha de devolución'] = pd.to_datetime(self._df['Fecha de devolución'])
        except Exception as e:
            print(f"Excepción controlada durante la limpieza de datos: {e}")

    def _calculate_statistics(self):
        try:
            self._df['Días de préstamo'] = (self._df['Fecha de devolución'] - self._df['Fecha de préstamo']).dt.days
        except Exception as e:
            print(f"Excepción controlada al calcular estadísticas: {e}")

    @property
    def dataframe(self):
        with self._data_lock:
            return self._df

    @property
    def data_load_time(self):
        return self._data_load_time

    def get_top_books(self, top_n=10):
        try:
            return self._df['Nombre del libro'].value_counts().head(top_n)
        except Exception as error:
            print(f"Excepción controlada al obtener los libros más prestados: {error}.")
            return pd.Series()

    def get_top_themes(self, top_n=5):
        try:
            return self._df['Temática del libro'].value_counts().head(top_n)
        except Exception as error:
            print(f"Excepción controlada al obtener las temáticas más populares: {error}.")
            return pd.Series()

    def promedio_dias_prestamo(self):
        try:
            return self._df['Días de préstamo'].mean()
        except Exception as error:
            print(f"Excepción controlada al obtener el promedio de días de préstamo: {error}.")
            return None

    def buscar_libro_y_calcular_estadisticas(self, nombre_del_libro):
        try:
            search_results = self.filter_by_book_name(nombre_del_libro)
            if not search_results.empty:
                registros = len(search_results)
                max_dias_prestamo = search_results['Días de préstamo'].max()
                promedio_dias_prestamo = search_results['Días de préstamo'].mean()
                return registros, max_dias_prestamo, promedio_dias_prestamo, search_results
            return None, None, None, None
        except Exception as error:
            print(f"Excepción controlada al buscar libro y calcular estadísticas: {error}.")
            return None, None, None, None

    def filter_by_book_name(self, nombre_del_libro):
        try:
            search_results = self._df[self._df['Nombre del libro'].str.contains(nombre_del_libro, case=False, na=False)]
            return search_results
        except Exception as error:
            print(f"Excepción controlada al filtrar por nombre del libro: {error}.")
            return pd.DataFrame()
