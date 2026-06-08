"""
Nicole Amaya
"""

import logging
import os
from typing import Dict
import numpy as np
import pandas as pd

# Configuración del sistema de alertas para auditoría de transformación
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - FEATURE ENGINEERING - %(levelname)s - %(message)s",
)


class AnalyticsEngineerPipeline:
    """Clase encargada de transformar el dataset limpio en Analytical Base Tables (ABT)."""

    def __init__(self, input_path: str, output_dir: str):
        self.input_path = input_path
        self.output_dir = output_dir
        self.df = None

    def cargar_dataset_previo(self):
        """Garantiza la continuidad del pipeline cargando el output de Eu."""
        if not os.path.exists(self.input_path):
            logging.error(f"Falta el insumo analítico en la ruta: {self.input_path}")
            raise FileNotFoundError(
                f"El archivo {self.input_path} no existe. Ejecuta el paso de Eu primero."
            )

        try:
            self.df = pd.read_csv(self.input_path)
            logging.info(
                f"Dataset de Eu cargado exitosamente. Dimensiones: {self.df.shape[0]} filas."
            )
            return self.df
        except Exception as e:
            logging.error(f"Error al leer el archivo intermedio: {e}")
            raise

    def refinar_strings_analiticos(self):
        """Remueve espacios fantasmas en variables que alteran las agregaciones."""
        if self.df is None:
            raise ValueError("No hay datos cargados en memoria para refinar.")

        logging.info(
            "-> [CLEAN] Corrigiendo espacios residuales en variables categóricas..."
        )

        columnas_a_limpiar = [
            "SaborPreferido",
            "PresentacionPreferida",
            "PrecioAdecuado",
            "GastoSnacksPartido",
            "CampaniaMasProbableCompra",
            "CampañaMasProbableCompra",
        ]

        for col in columnas_a_limpiar:
            if col in self.df.columns:
                self.df[col] = (
                    self.df[col].astype(str).str.strip().str.title()
                )
                logging.info(f"   [✓] Columna corregida con éxito: {col}")
            else:
                logging.warning(
                    f"   [!] Columna opcional saltada (no presente): {col}"
                )

        return self.df

    def construir_abt_snacks(self) -> pd.DataFrame:
        """Desanida la columna de selección múltiple de snacks usando .explode()."""
        logging.info("-> [ABT SNACKS] Creando estructura granular para Snacks...")

        df_snacks = self.df[
            [
                "EncuestaID",
                "RangoEdad",
                "Genero",
                "Departamento",
                "FrecuenciaConsumoSnacks",
                "SaborPreferido",
                "SnacksSeleccionados",
            ]
        ].copy()

        df_snacks["Snack"] = (
            df_snacks["SnacksSeleccionados"].astype(str).str.split(";")
        )
        df_snacks = df_snacks.explode("Snack")

        df_snacks["Snack"] = df_snacks["Snack"].str.strip().str.title()
        df_snacks = df_snacks.drop(columns=["SnacksSeleccionados"])

        df_snacks = df_snacks[
            (df_snacks["Snack"] != "") & (df_snacks["Snack"] != "Nan")
        ]

        return df_snacks

    def construir_abt_jugadores(self) -> pd.DataFrame:
        """Desanida la columna de líderes de opinión de fútbol (JugadoresInfluyentes)."""
        logging.info(
            "-> [ABT JUGADORES] Creando estructura granular para Jugadores..."
        )

        df_jugadores = self.df[
            [
                "EncuestaID",
                "RangoEdad",
                "Genero",
                "Departamento",
                "SeleccionApoya",
                "JugadoresInfluyentes",
            ]
        ].copy()

        df_jugadores["Jugador"] = (
            df_jugadores["JugadoresInfluyentes"].astype(str).str.split(";")
        )
        df_jugadores = df_jugadores.explode("Jugador")

        df_jugadores["Jugador"] = df_jugadores["Jugador"].str.strip().str.title()
        df_jugadores = df_jugadores.drop(columns=["JugadoresInfluyentes"])

        df_jugadores = df_jugadores[
            (df_jugadores["Jugador"] != "") & (df_jugadores["Jugador"] != "Nan")
        ]

        return df_jugadores

    def ejecutar_feature_engineering(self) -> pd.DataFrame:
        """Calcula los indicadores compuestos evitando errores de dimensiones en np.select."""
        logging.info(
            "-> [FEATURES] Extrayendo nuevas variables condicionales..."
        )
        abt_df = self.df.copy()

        # --- CORRECCIÓN DE LA VARIABLE 1: DISPOSICIÓN DE GASTO PREMIUM ---
        # 2 condiciones emparejadas con exactamente 2 opciones. El resto va al default.
        condiciones_gasto = [
            (
                abt_df["GastoSnacksPartido"].isin(
                    ["Q51 - Q100", "Más De Q100", "Mas De Q100"]
                )
            )
            & (abt_df["PagaMasEdicionMundial"] == "Sí"),
            (
                abt_df["GastoSnacksPartido"].isin(
                    ["Q25 - Q50", "Q51 - Q100", "Más De Q100", "Mas De Q100"]
                )
            )
            | (abt_df["PagaMasEdicionMundial"] == "Sí"),
        ]
        opciones_gasto = ["Premium Alta", "Moderada"]

        abt_df["Disposicion_Gasto_Premium"] = np.select(
            condiciones_gasto, opciones_gasto, default="Sensible Al Precio"
        )

        # --- VARIABLE 2: SEGMENTO DE LEALTAD / ENGAGEMENT MUNDIALISTA ---
        condiciones_lealtad = [
            (abt_df["PlaneaVerMundial2026"] == "Sí")
            & (abt_df["CompraDisenoSeleccion"].isin(["Sí", "Probablemente sí"]))
            & (abt_df["CompraTarjetasColeccionables"] == "Sí"),
            (abt_df["PlaneaVerMundial2026"] == "Sí")
            & (
                (
                    abt_df["CompraDisenoSeleccion"].isin(
                        ["Sí", "Probablemente sí"]
                    )
                )
                | (abt_df["CompraTarjetasColeccionables"] == "Sí")
            ),
        ]
        opciones_lealtad = ["Fanático Target (Alto)", "Casual"]

        abt_df["Segmento_Lealtad_Mundial"] = np.select(
            condiciones_lealtad, opciones_lealtad, default="Espectador Pasivo"
        )

        # --- VARIABLE 3: GRUPO DEMOGRÁFICO SIMPLIFICADO ---
        mapeo_edades: Dict[str, str] = {
            "Menos De 18 Años": "Jóvenes (<25)",
            "18 - 24 Años": "Jóvenes (<25)",
            "25 - 34 Años": "Adulto Joven (25-34)",
            "35 - 44 Años": "Adulto Maduro (35-54)",
            "45 - 54 Años": "Adulto Maduro (35-54)",
            "55 Años O Más": "Adulto Mayor (55+)",
        }
        abt_df["Segmento_Edad_Analitico"] = abt_df["RangoEdad"].map(
            mapeo_edades
        )

        return abt_df

    def exportar_tablas_analiticas(
        self, abt_m: pd.DataFrame, abt_s: pd.DataFrame, abt_j: pd.DataFrame
    ):
        """Escribe los archivos CSV en la ubicación real de Windows."""
        try:
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir, exist_ok=True)

            abt_m.to_csv(
                os.path.join(self.output_dir, "ABT_Mundial.csv"), index=False
            )
            abt_s.to_csv(
                os.path.join(self.output_dir, "ABT_Snacks.csv"), index=False
            )
            abt_j.to_csv(
                os.path.join(self.output_dir, "ABT_Jugadores.csv"), index=False
            )

            logging.info(
                f"[✓] Archivos analíticos generados exitosamente en: {self.output_dir}"
            )
        except Exception as e:
            logging.error(f"Error en la exportación de archivos: {e}")
            raise


# --- CONTROLADOR DE EJECUCIÓN DEL MÓDULO ---
if __name__ == "__main__":
    # Esta es tu ruta física real que vimos en tu explorador de archivos de Windows
    CARPETA_SALIDA_ABT = (
        r"C:\Users\nicoe\OneDrive\Escritorio\Proyecto_Final_Pandas\1_data\clean"
    )
    RUTA_INTRALIMPIA = os.path.join(CARPETA_SALIDA_ABT, "dataset_limpio.csv")

    print("\n" + "=" * 65)
    print(" INICIANDO ORQUESTACIÓN DE CAPA: FEATURE ENGINEERING (NICOLE) ")
    print("=" * 65 + "\n")

    try:
        pipeline = AnalyticsEngineerPipeline(RUTA_INTRALIMPIA, CARPETA_SALIDA_ABT)
        pipeline.cargar_dataset_previo()
        pipeline.refinar_strings_analiticos()

        df_m = pipeline.ejecutar_feature_engineering()
        df_s = pipeline.construir_abt_snacks()
        df_j = pipeline.construir_abt_jugadores()

        pipeline.exportar_tablas_analiticas(df_m, df_s, df_j)
        print("\n" + "=" * 65)
        print(" PIPELINE ANALÍTICO COMPLETADO - REPOSITORIO LISTO PARA BI ")
        print("=" * 65 + "\n")

    except Exception as error:
        print(f"\n[X] FALLO GLOBAL EN EL PIPELINE ANALÍTICO: {error}\n")