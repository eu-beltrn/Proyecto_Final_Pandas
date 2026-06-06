import pandas as pd
import logging
import os

# Configuración de logging profesional para auditoría de datos
logging.basicConfig(level=logging.INFO, format='%(asctime)s - DATA QUALITY - %(levelname)s - %(message)s')

class DataQualityEngineer:
    """Clase para ingesta, perfilamiento, auditoría, limpieza y exportación de calidad de datos."""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.df = None

    def cargar_datos(self) -> pd.DataFrame:
        """Carga los datos manejando excepciones de manera segura."""
        if not os.path.exists(self.file_path):
            logging.error(f"Archivo no encontrado en la ruta: {self.file_path}")
            raise FileNotFoundError(f"El archivo {self.file_path} no existe.")
        
        try:
            self.df = pd.read_csv(self.file_path)
            logging.info(f"Dataset cargado exitosamente. Dimensiones: {self.df.shape[0]} filas, {self.df.shape[1]} columnas.")
            return self.df
        except Exception as e:
            logging.error(f"Error al leer el archivo CSV: {e}")
            raise

    def explorar_calidad(self):
        """Genera un reporte proactivo y limpio de calidad de datos (Profiling)."""
        if self.df is None:
            logging.warning("No hay datos cargados para explorar.")
            return

        logging.info("--- INICIANDO PERFILAMIENTO DE DATOS ---")
        
        print("\n" + "="*50)
        print("REPORTE DE EXPLORACIÓN DE DATOS")
        print("="*50)

        print("\n1. VISTA PREVIA DE LOS PRIMEROS REGISTROS:")
        print(self.df.head())

        print("\n2. DIMENSIONES DEL DATASET:")
        print(f"Total de Filas: {self.df.shape[0]} | Total de Columnas: {self.df.shape[1]}")

        print("\n3. LISTADO DE COLUMNAS DISPONIBLES:")
        print(self.df.columns.tolist())

        print("\n4. ESTRUCTURA Y TIPOS DE DATOS POR COLUMNA:")
        print(self.df.dtypes)

        print("\n5. RESUMEN DE COMPOSICIÓN Y USO DE MEMORIA:")
        self.df.info()

        print("\n6. ANÁLISIS ESTADÍSTICO DESCRIPTIVO GENERAL:")
        print(self.df.describe(include='all'))
        
        print("\n" + "="*50)
        print("   FIN DEL REPORTE DE EXPLORACIÓN")
        print("="*50 + "\n")

    @staticmethod
    def _limpiar_texto(serie: pd.Series) -> pd.Series:
        """Función auxiliar para normalizar texto, eliminar espacios y corregir nulos de tipo string."""
        return serie.astype(str).str.strip().str.title().replace('Nan', 'No Especificado')

    def limpiar_datos(self) -> pd.DataFrame:
        """
        7. LIMPIEZA DE DATOS REQUERIDA
        Identifica y corrige valores nulos, duplicados, errores de formato
        e inconsistencias de texto aplicando Method Chaining.
        """
        if self.df is None:
            logging.error("No hay datos en memoria para proceder con la limpieza.")
            return None

        logging.info("--- INICIANDO PROCESO DE LIMPIEZA DE DATOS (METHOD CHAINING) ---")
        
        try:
            df_limpio = (
                self.df
                .drop_duplicates()  # 1. Eliminar duplicados exactos
                .assign(
                    # 2. Conversión segura de fechas (convierte errores a NaT)
                    FechaEncuesta = lambda x: pd.to_datetime(x['FechaEncuesta'], errors='coerce'),
                    
                    # 3. Estandarización tipográfica unificada
                    Genero = lambda x: self._limpiar_texto(x['Genero']),
                    RangoEdad = lambda x: self._limpiar_texto(x['RangoEdad']),
                    Departamento = lambda x: self._limpiar_texto(x['Departamento']),
                    Ocupacion = lambda x: self._limpiar_texto(x['Ocupacion']),
                    FrecuenciaConsumoSnacks = lambda x: self._limpiar_texto(x['FrecuenciaConsumoSnacks']),
                    
                    # 4. Imputación explícita para columnas críticas de Marketing
                    GastoSnacksPartido = lambda x: x['GastoSnacksPartido'].fillna('Sin Presupuesto Definido')
                )
            )
            
            logging.info(f"Limpieza finalizada. Filas originales: {self.df.shape[0]} | Filas limpias: {df_limpio.shape[0]}")
            self.df = df_limpio
            return self.df
            
        except Exception as e:
            logging.error(f"Fallo en la ejecución del Method Chaining de limpieza: {e}")
            raise

    def guardar_datos_limpios(self, output_path: str):
        """Exporta el dataset procesado a la ruta especificada."""
        if self.df is None:
            logging.error("No hay datos cargados para exportar.")
            return
        
        try:
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                logging.info(f"Creado el directorio de destino: {output_dir}")

            self.df.to_csv(output_path, index=False)
            logging.info(f"Archivo limpio generado con éxito en: {output_path}")
        except Exception as e:
            logging.error(f"Error al guardar el archivo limpio: {e}")
            raise


# Bloque de ejecución principal
if __name__ == "__main__":
    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    
    # --- CONFIGURACIÓN DE RUTA DE ENTRADA ---
    NOMBRE_CSV = "encuesta_snacks_mundial_2026_guatemala_2500_respuestas.csv"
    RUTA_CSV_ORIGINAL = os.path.join(directorio_actual, "..", "1_data", "raw", NOMBRE_CSV)
    
    # --- CONFIGURACIÓN DE RUTA DE SALIDA (DATASET LIMPIO) ---
    NOMBRE_CSV_LIMPIO = "dataset_limpio.csv"
    RUTA_CSV_DESTINO = os.path.join(directorio_actual, "..", "1_data", "clean", NOMBRE_CSV_LIMPIO)
    
    # Inicialización del Pipeline
    pipeline = DataQualityEngineer(RUTA_CSV_ORIGINAL)
    
    # 1. Ingesta
    df_raw = pipeline.cargar_datos()
    
    # 2. Perfilamiento Inicial
    pipeline.explorar_calidad()
    
    # 3. Ejecución de Limpieza Requerida
    df_clean = pipeline.limpiar_datos()
    
    # 4. Almacenamiento
    pipeline.guardar_datos_limpios(RUTA_CSV_DESTINO)