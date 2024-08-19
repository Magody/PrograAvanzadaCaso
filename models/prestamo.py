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
            self._df = pd.read_csv("./data/prestamos.csv")
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
