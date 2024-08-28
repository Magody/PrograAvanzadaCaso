import pandas as pd  # Importa la biblioteca pandas para manipulación de datos
import threading  # Importa el módulo threading para trabajar con hilos
import time  # Importa el módulo time para medir el tiempo

class PrestamoManager:
    # Variable de clase para mantener la única instancia (Singleton)
    _instance = None

    @staticmethod
    def get_instance():
        """
        Método estático para obtener la única instancia de PrestamoManager.
        Si la instancia no existe, se crea una nueva.
        """
        if PrestamoManager._instance is None:
            PrestamoManager()  # Crea una nueva instancia si no existe
        return PrestamoManager._instance  # Retorna la instancia única

    def __init__(self):
        """
        Inicializa una instancia de PrestamoManager.
        Asegura que solo haya una instancia (Singleton). 
        Carga el DataFrame desde un archivo CSV y procesa los datos.
        """
        if PrestamoManager._instance is not None:
            raise Exception("This class is a singleton!")  # Lanza excepción si ya existe una instancia
        else:
            PrestamoManager._instance = self  # Establece la instancia actual como la única instancia
            self._df = pd.DataFrame()  # Inicializa el DataFrame vacío
            self.lock = threading.Lock()  # Inicializa el lock para manejo de concurrencia
            try:
                self.df_read = pd.read_csv("./data/prestamos_libros.csv")
                self._procesar_concurrentemente()  # Procesa los datos concurrentemente
            except Exception as error:
                # Captura cualquier error en la lectura del archivo y muestra un mensaje
                print(f"Excepción controlada: {error}. Se generará un DataFrame vacío.")
            finally:
                # Mensaje si el DataFrame queda vacío tras el procesamiento
                if self._df.empty:
                    print("DataFrame vacío generado de inicio")

    def _clean_data(self, df_part):
        """
        Limpia y convierte las columnas de fechas en el DataFrame parcial.
        """
        try:
            df_part['Fecha de préstamo'] = pd.to_datetime(df_part['Fecha de préstamo'])  # Convierte la columna a tipo datetime
            df_part['Fecha de devolución'] = pd.to_datetime(df_part['Fecha de devolución'])  # Convierte la columna a tipo datetime
        except Exception as error:
            # Captura cualquier error en la limpieza de datos y muestra un mensaje
            print(f"Excepción controlada durante la limpieza de datos: {error}. No se limpiará el DataFrame.")

    def _calculate_statistics(self, df_part):
        """
        Calcula el número de días de préstamo en el DataFrame parcial.
        """
        try:
            df_part['Días de préstamo'] = (df_part['Fecha de devolución'] - df_part['Fecha de préstamo']).dt.days  # Calcula días de préstamo
        except Exception as error:
            # Captura cualquier error en el cálculo de estadísticas y muestra un mensaje
            print(f"Excepción controlada al calcular estadísticas: {error}. Las estadísticas no se calcularán.")

    def _procesar_parte(self, df_part):
        """
        Procesa una parte del DataFrame aplicando limpieza y cálculo de estadísticas.
        Luego concatena la parte procesada al DataFrame principal.
        """
        self._clean_data(df_part)  # Limpia los datos en la parte del DataFrame
        self._calculate_statistics(df_part)  # Calcula las estadísticas en la parte del DataFrame

        with self.lock:
            # Asegura que la operación de concatenación sea segura para hilos
            self._df = pd.concat([self._df, df_part])  # Concatena la parte procesada al DataFrame principal

    def _procesar_concurrentemente(self, num_hilos=1):
        """
        Procesa el DataFrame en partes usando múltiples hilos.
        """
        if len(self.df_read) < num_hilos:
            # Ajusta el número de hilos si hay menos filas que hilos
            num_hilos = len(self.df_read)
        
        tamaño_parte = len(self.df_read) // num_hilos  # Calcula el tamaño de cada parte del DataFrame
        hilos = []  # Lista para almacenar los hilos

        for i in range(num_hilos):
            inicio = i * tamaño_parte  # Índice de inicio para la parte del DataFrame
            fin = len(self.df_read) if i == num_hilos - 1 else (i + 1) * tamaño_parte  # Índice final para la parte del DataFrame
            print("DEBUG: ", inicio, fin, len(self._df))
            df_part = self.df_read.iloc[inicio:fin]  # Extrae la parte del DataFrame

            # Crea y empieza un nuevo hilo para procesar una parte del DataFrame
            hilo = threading.Thread(target=self._procesar_parte, args=(df_part,))
            hilos.append(hilo)  # Añade el hilo a la lista
            hilo.start()  # Inicia el hilo

        for hilo in hilos:
            # Espera a que todos los hilos terminen
            hilo.join()

    def _procesar_sin_concurrencia(self):
        """
        Procesa el DataFrame sin utilizar concurrencia y mide el tiempo de procesamiento.
        """
        start_time = time.perf_counter()  # Registra el tiempo de inicio
        self._clean_data(self._df)  # Limpia los datos en el DataFrame
        self._calculate_statistics(self._df)  # Calcula las estadísticas en el DataFrame
        elapsed_time = time.perf_counter() - start_time  # Calcula el tiempo transcurrido
        print(f"Tiempo de procesamiento sin concurrencia: {elapsed_time:.4f} segundos")  # Imprime el tiempo de procesamiento

    @property
    def dataframe(self):
        """
        Propiedad para obtener el DataFrame principal.
        """
        return self._df

    def get_top_books(self, top_n=10):
        """
        Devuelve los libros más prestados, limitados a los primeros `top_n` libros.
        """
        try:
            return self._df['Nombre del libro'].value_counts().head(top_n)  # Cuenta los libros y devuelve los más prestados
        except Exception as error:
            # Captura cualquier error al obtener los libros más prestados y muestra un mensaje
            print(f"Excepción controlada al obtener los libros más prestados: {error}.")
            return pd.Series()  # Retorna una Serie vacía en caso de error

    def get_top_themes(self, top_n=5):
        """
        Devuelve las temáticas de libros más populares, limitadas a las primeras `top_n` temáticas.
        """
        try:
            return self._df['Temática del libro'].value_counts().head(top_n)  # Cuenta las temáticas y devuelve las más populares
        except Exception as error:
            # Captura cualquier error al obtener las temáticas más populares y muestra un mensaje
            print(f"Excepción controlada al obtener las temáticas más populares: {error}.")
            return pd.Series()  # Retorna una Serie vacía en caso de error

    def promedio_dias_prestamo(self):
        """
        Devuelve el promedio de días de préstamo.
        """
        try:
            return self._df['Días de préstamo'].mean()  # Calcula y devuelve el promedio de días de préstamo
        except Exception as error:
            # Captura cualquier error al calcular el promedio de días de préstamo y muestra un mensaje
            print(f"Excepción controlada al obtener el promedio de días de préstamo: {error}.")
            return None  # Retorna None en caso de error

    def buscar_libro_y_calcular_estadisticas(self, nombre_del_libro):
        """
        Busca un libro por nombre y calcula estadísticas sobre el mismo.
        """
        try:
            start_time = time.perf_counter()  # Registra el tiempo de inicio
            search_results = self.filter_by_book_name(nombre_del_libro)  # Busca el libro en el DataFrame

            # Agrega un pequeño retraso artificial para simular procesamiento
            time.sleep(0.1)  # Retraso de 100 milisegundos

            elapsed_time = time.perf_counter() - start_time  # Calcula el tiempo transcurrido
            print(f"Tiempo de búsqueda del libro: {elapsed_time:.4f} segundos")  # Imprime el tiempo de búsqueda

            if not search_results.empty:
                # Si se encuentran resultados, calcula estadísticas adicionales
                registros = len(search_results)  # Número de registros encontrados
                max_dias_prestamo = search_results['Días de préstamo'].max()  # Máximo número de días de préstamo
                promedio_dias_prestamo = search_results['Días de préstamo'].mean()  # Promedio de días de préstamo
                return registros, max_dias_prestamo, promedio_dias_prestamo, search_results
            return None, None, None, None  # Retorna None si no se encuentran resultados
        except Exception as error:
            # Captura cualquier error durante la búsqueda y cálculo de estadísticas y muestra un mensaje
            print(f"Excepción controlada al buscar libro y calcular estadísticas: {error}.")
            return None, None, None, None  # Retorna None en caso de error

    def filter_by_book_name(self, nombre_del_libro):
        """
        Filtra el DataFrame para encontrar libros que contengan el nombre dado.
        """
        try:
            search_results = self._df[self._df['Nombre del libro'].str.contains(nombre_del_libro, case=False, na=False)]
            # Filtra el DataFrame para buscar libros que contengan el nombre dado, ignorando mayúsculas/minúsculas
            return search_results
        except Exception as error:
            # Captura cualquier error al filtrar por nombre del libro y muestra un mensaje
            print(f"Excepción controlada al filtrar por nombre del libro: {error}.")
            return pd.DataFrame()  # Retorna un DataFrame vacío en caso de error

if __name__ == "__main__":
    # Si se ejecuta el script directamente, crea una instancia de PrestamoManager y muestra el DataFrame
    prestamo_manager = PrestamoManager.get_instance()  # Obtiene la instancia única de PrestamoManager
    print(prestamo_manager.dataframe)  # Imprime el DataFrame
