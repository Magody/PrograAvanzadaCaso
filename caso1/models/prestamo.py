import pandas as pd
from datetime import datetime

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
            self._df = pd.read_csv("./data/prestamos_libros.csv")
            self._clean_data()
            self._calculate_statistics()

    def _clean_data(self):
        self._df['Fecha de préstamo'] = pd.to_datetime(self._df['Fecha de préstamo'])
        self._df['Fecha de devolución'] = pd.to_datetime(self._df['Fecha de devolución'])

    def _calculate_statistics(self):
        self._df['Días de préstamo'] = (self._df['Fecha de devolución'] - self._df['Fecha de préstamo']).dt.days

    @property
    def dataframe(self):
        return self._df

    def max_dias_prestamo(self):
        return self._df['Días de préstamo'].max()

    def promedio_dias_prestamo(self):
        return self._df['Días de préstamo'].mean()

    def filter_by_book_name(self, nombre_del_libro):
        search_results = self._df[self._df['Nombre del libro'].str.contains(nombre_del_libro, case=False, na=False)]
        return search_results

    def get_top_books(self, top_n=10):
        return self._df['Nombre del libro'].value_counts().head(top_n)

    def get_top_themes(self, top_n=5):
        return self._df['Temática del libro'].value_counts().head(top_n)

    def buscar_libro_y_calcular_estadisticas(self, nombre_del_libro):
        search_results = self.filter_by_book_name(nombre_del_libro)
        if not search_results.empty:
            registros = len(search_results)
            max_dias_prestamo = search_results['Días de préstamo'].max()
            promedio_dias_prestamo = search_results['Días de préstamo'].mean()
            return registros, max_dias_prestamo, promedio_dias_prestamo, search_results
        return None, None, None, None
