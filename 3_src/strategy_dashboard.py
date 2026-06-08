import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys  # <-- AGREGAR ESTO

class StrategyDashboard:
    """
    Clase encargada de generar visualizaciones ejecutivas para responder
    las 5 preguntas clave de negocio planteadas por la gerencia.
    """
    
    def __init__(self, abt_path: str, output_dir: str, reports_dir: str): # <-- NUEVO PARÁMETRO
        self.abt_path = abt_path
        self.output_dir = output_dir
        self.reports_dir = reports_dir # <-- SE ASIGNA LA RUTA DE REPORTES
        self.df_abt = None
        self.df_jugadores = None
        self.df_snacks = None
        
        # Configuración de estilo corporativo minimalista
        sns.set_theme(style="whitegrid", rc={
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.edgecolor": "#cccccc",
            "grid.color": "#ebebeb",
            "font.family": "sans-serif",
            "axes.titlesize": 16,
            "axes.labelsize": 12,
            "xtick.labelsize": 11,
            "ytick.labelsize": 11
        })
        # Paleta de colores corporativa (Resalta el valor principal)
        self.corporate_palette = ["#1A5276", "#2980B9", "#7FB3D5", "#D4E6F1", "#EBF5FB"]
        self.highlight_palette = ["#E74C3C"] + ["#BDC3C7"] * 9
        
    def load_data(self):
        """Carga la ABT principal y las tablas desanidadas con manejo de errores."""
        try:
            self.df_abt = pd.read_csv(self.abt_path)
            self.df_jugadores = pd.read_csv(self.abt_path.replace('ABT_Mundial.csv', 'ABT_Jugadores.csv'))
            self.df_snacks = pd.read_csv(self.abt_path.replace('ABT_Mundial.csv', 'ABT_Snacks.csv'))
            os.makedirs(self.output_dir, exist_ok=True)
            os.makedirs(self.reports_dir, exist_ok=True) 
        except FileNotFoundError as e:
            print(f"❌ Error Crítico: No se encontraron los archivos ABT. Detalle: {e}")
            sys.exit(1) # <-- USAR sys.exit(1) EN LUGAR DE exit(1)

    def q1_snack_a_promocionar(self):
        """¿Qué snack debe promocionarse?"""
        plt.figure(figsize=(10, 6))
        top_snacks = self.df_snacks['Snack'].value_counts().head(5)
        # CORRECCIÓN: hue=top_snacks.index, legend=False y slice de la paleta
        ax = sns.barplot(x=top_snacks.values, y=top_snacks.index, hue=top_snacks.index, 
                         palette=self.highlight_palette[:len(top_snacks)], legend=False)
        plt.title('3. Ranking de Snacks: Market Share Base', pad=20, fontweight='bold', color='#2C3E50')
        plt.xlabel('Cantidad de Menciones (Incluye selecciones múltiples)', color='#7F8C8D')
        plt.ylabel('')
        for i, v in enumerate(top_snacks.values):
            ax.text(v + 10, i, f" {v}", color='#2C3E50', va='center', fontweight='bold')
        plt.savefig(os.path.join(self.output_dir, "q1_snack.png"), bbox_inches='tight', dpi=300)
        plt.close()

    def q2_jugador_a_utilizar(self):
        """¿Qué jugador debe utilizarse?"""
        plt.figure(figsize=(10, 6))
        top_jugadores = self.df_jugadores['Jugador'].value_counts().head(5)
        # CORRECCIÓN
        ax = sns.barplot(x=top_jugadores.values, y=top_jugadores.index, hue=top_jugadores.index, 
                         palette=self.highlight_palette[:len(top_jugadores)], legend=False)
        plt.title('6. Jugadores con Mayor Influencia', pad=20, fontweight='bold', color='#2C3E50')
        plt.xlabel('Frecuencia de mención como motivador de compra', color='#7F8C8D')
        plt.ylabel('')
        for i, v in enumerate(top_jugadores.values):
            ax.text(v + 10, i, f" {v}", color='#2C3E50', va='center', fontweight='bold')
        plt.savefig(os.path.join(self.output_dir, "q2_jugador.png"), bbox_inches='tight', dpi=300)
        plt.close()

    def q3_seleccion_mayor_influencia(self):
        """¿Qué selección genera mayor influencia?"""
        plt.figure(figsize=(10, 6))
        df_premium = self.df_abt[self.df_abt['Target_Premium'] == 1]
        top_selecciones = df_premium['SeleccionApoya'].value_counts().head(5)
        # CORRECCIÓN
        ax = sns.barplot(x=top_selecciones.index, y=top_selecciones.values, hue=top_selecciones.index, 
                         palette=self.corporate_palette[:len(top_selecciones)], legend=False)
        plt.title('5. Equipos con Mayor Influencia en Gasto Premium', pad=20, fontweight='bold', color='#2C3E50')
        plt.xlabel('Selección Nacional', color='#7F8C8D')
        plt.ylabel('Usuarios dispuestos a pagar sobreprecio', color='#7F8C8D')
        plt.savefig(os.path.join(self.output_dir, "q3_seleccion.png"), bbox_inches='tight', dpi=300)
        plt.close()

    def q4_promocion_efectiva(self):
        """¿Qué promoción es más efectiva?"""
        plt.figure(figsize=(8, 8))
        
        promociones = self.df_abt['PromocionPreferida'].value_counts()
        
        # Gráfico de Dona para estilo ejecutivo
        plt.pie(promociones.values, labels=promociones.index, autopct='%1.1f%%', 
                startangle=90, colors=self.corporate_palette, 
                wedgeprops=dict(width=0.4, edgecolor='w'))
        
        plt.title('8. Promociones Preferidas: Eficacia Esperada', pad=20, fontweight='bold', color='#2C3E50')
        
        plt.savefig(os.path.join(self.output_dir, "q4_promocion.png"), bbox_inches='tight', dpi=300)
        plt.close()

    def q5_rango_precio_ideal(self):
        """¿Cuál es el rango de precio ideal?"""
        plt.figure(figsize=(10, 6))
        
        
        # Histograma con estimación de densidad (KDE)
        # Filtramos valores mayores a 0 para no distorsionar la media
        df_precio_valido = self.df_abt[self.df_abt['Presupuesto_Numerico'] > 0]
        
        ax = sns.histplot(data=df_precio_valido, x='Presupuesto_Numerico', bins=10, 
                          kde=True, color='#2980B9', edgecolor="white", alpha=0.7)
        
        # Línea vertical para la media usando el dataframe filtrado
        mean_price = df_precio_valido['Presupuesto_Numerico'].mean()
        plt.axvline(mean_price, color='#E74C3C', linestyle='dashed', linewidth=2)
        plt.text(mean_price + 1, ax.get_ylim()[1]*0.9, f'Media: Q{mean_price:.2f}', color='#E74C3C', fontweight='bold')

        plt.savefig(os.path.join(self.output_dir, "q5_precio.png"), bbox_inches='tight', dpi=300)
        plt.close()
        
    # ==========================================
    # REPORTES FALTANTES (SECCIÓN 9)
    # ==========================================
        
    def reporte_perfil_demografico(self):
        """Reporte 1: Perfil Demográfico"""
        plt.figure(figsize=(10, 6))
        ax = sns.countplot(data=self.df_abt, x='RangoEdad', hue='Genero', palette='Blues')
        plt.title('1. Perfil Demográfico del Consumidor', fontweight='bold', color='#2C3E50')
        plt.xlabel('Rango de Edad')
        plt.ylabel('Cantidad')
        plt.xticks(rotation=45) # <-- AGREGA ESTA LÍNEA
        plt.savefig(os.path.join(self.output_dir, "reporte_01_demografico.png"), bbox_inches='tight')
        plt.close()

    def reporte_frecuencia_consumo(self):
        """Reporte 2: Frecuencia de Consumo (Segmentos de Lealtad)"""
        plt.figure(figsize=(8, 6))
        segmentos = self.df_abt['Segmento_Lealtad'].value_counts()
        colores = ['#1A5276', '#2980B9', '#7FB3D5']
        # CORRECCIÓN
        sns.barplot(x=segmentos.index, y=segmentos.values, hue=segmentos.index, 
                    palette=colores[:len(segmentos)], legend=False)
        plt.title('2. Frecuencia de Consumo (Segmentación de Lealtad)', fontweight='bold', color='#2C3E50')
        plt.savefig(os.path.join(self.output_dir, "reporte_02_frecuencia.png"), bbox_inches='tight')
        plt.close()

    def reporte_publicidad_efectiva(self):
        """Reporte 7: Tipo de Publicidad más Efectiva"""
        plt.figure(figsize=(10, 6))
        pubs = self.df_abt['TipoPublicidadAtractiva'].value_counts()
        # CORRECCIÓN
        sns.barplot(y=pubs.index, x=pubs.values, hue=pubs.index, palette='magma', legend=False)
        plt.title('7. Eficacia por Canal Publicitario', fontweight='bold', color='#2C3E50')
        plt.xlabel('Impacto (Menciones)')
        plt.savefig(os.path.join(self.output_dir, "reporte_07_publicidad.png"), bbox_inches='tight')
        plt.close()

    def reporte_intencion_compra(self):
        """Reporte 9: Intención de Compra por Campaña (Premium)"""
        plt.figure(figsize=(7, 7))
        intencion = self.df_abt['Target_Premium'].value_counts().rename(index={1: 'Disposición a Pagar Más', 0: 'Sensible al Precio'})
        plt.pie(intencion, labels=intencion.index, autopct='%1.1f%%', colors=['#27AE60', '#E74C3C'], startangle=90, explode=(0.05, 0))
        plt.title('9. Intención de Compra (Edición Mundial)', fontweight='bold', color='#2C3E50')
        plt.savefig(os.path.join(self.output_dir, "reporte_09_intencion_compra.png"), bbox_inches='tight')
        plt.close()

    # ==========================================
    # DASHBOARD EJECUTIVO Y KPIs (SECCIÓN 14)
    # ==========================================
        
    def generar_kpis_dashboard(self):
        """Calcula y muestra los KPIs principales exigidos en la Sección 14"""
        total_encuestas = len(self.df_abt)
        ticket_promedio = self.df_abt['Presupuesto_Numerico'].mean()
        tasa_conversion = self.df_abt['Target_Premium'].mean() * 100
        top_snack = self.df_snacks['Snack'].mode()[0]
        
        # Segmentación extra (Usando .get() o filtrado seguro para evitar errores si no hay "Masculino" o "Femenino")
        df_hombres = self.df_abt[self.df_abt['Genero'] == 'Masculino']
        df_mujeres = self.df_abt[self.df_abt['Genero'] == 'Femenino']
        
        ticket_hombres = df_hombres['Presupuesto_Numerico'].mean() if not df_hombres.empty else 0
        ticket_mujeres = df_mujeres['Presupuesto_Numerico'].mean() if not df_mujeres.empty else 0
        
        print("\n" + "="*50)
        print(" 📊 DASHBOARD EJECUTIVO: KPIs PRINCIPALES ".center(50))
        print("="*50)
        print(f" 👥 Tamaño de la Muestra (N):     {total_encuestas:,} usuarios")
        print(f" 💰 Ticket Promedio Global:       Q{ticket_promedio:.2f}")
        print(f"     ➔ Hombres: Q{ticket_hombres:.2f} | Mujeres: Q{ticket_mujeres:.2f}")
        print(f" 🚀 Tasa de Intención Premium:    {tasa_conversion:.1f}%")
        print(f" 🍟 Snack Líder para Campaña:     {top_snack}")
        print("="*50 + "\n")
        
        # Guardar KPIs usando la ruta dinámica
        kpi_text = (
            f"DASHBOARD EJECUTIVO: KPIs PRINCIPALES\n"
            f"==================================================\n"
            f"Tamaño de la Muestra (N):     {total_encuestas:,} usuarios\n"
            f"Ticket Promedio Global:       Q{ticket_promedio:.2f}\n"
            f"    ➔ Hombres: Q{ticket_hombres:.2f} | Mujeres: Q{ticket_mujeres:.2f}\n"
            f"Tasa de Intención Premium:    {tasa_conversion:.1f}%\n"
            f"Snack Líder para Campaña:     {top_snack}\n"
        )
        ruta_archivo_kpis = os.path.join(self.reports_dir, "KPIs_Ejecutivos.txt")
        with open(ruta_archivo_kpis, "w", encoding="utf-8") as f:
            f.write(kpi_text)

    def reporte_segmentacion_premium(self):
        """Visualización de Segmentación requerida en la Sección 14"""
        plt.figure(figsize=(9, 6))
        ax = sns.countplot(data=self.df_abt, x='Segmento_Lealtad', hue='Target_Premium', palette=['#BDC3C7', '#E74C3C'])
        plt.title('Dashboard Segmentación: Intención Premium vs Lealtad', fontweight='bold', color='#2C3E50')
        plt.xlabel('Segmento de Lealtad')
        plt.ylabel('Cantidad de Usuarios')
        plt.legend(title='Disposición a Pagar Más', labels=['No', 'Sí'])
        plt.savefig(os.path.join(self.output_dir, "dashboard_segmentacion_lealtad.png"), bbox_inches='tight', dpi=300)
        plt.close()

    def ejecutar_todos_los_reportes(self):
        """Método maestro para cumplir con la rúbrica al 100%"""
        self.load_data()
        
        # Generar KPIs en consola (Sección 14)
        self.generar_kpis_dashboard()
        
        # Generar los 10 Reportes Obligatorios (Sección 9) en ORDEN SECUENCIAL
        self.reporte_perfil_demografico()      # Reporte 1
        self.reporte_frecuencia_consumo()      # Reporte 2
        self.q1_snack_a_promocionar()          # Reporte 3
        self.q5_rango_precio_ideal()           # Reporte 4
        self.q3_seleccion_mayor_influencia()   # Reporte 5
        self.q2_jugador_a_utilizar()           # Reporte 6
        self.reporte_publicidad_efectiva()     # Reporte 7
        self.q4_promocion_efectiva()           # Reporte 8
        self.reporte_intencion_compra()        # Reporte 9
        
        # Gráficas de soporte para Dashboard (Sección 14)
        self.reporte_segmentacion_premium()
        
        print("✅ Los 10 Reportes Obligatorios y KPIs han sido exportados exitosamente a sus carpetas.")

if __name__ == "__main__":
    # Ajustar rutas de entrada y de salida según la estructura del repositorio
    ABT_PATH = "../1_data/clean/ABT_Mundial.csv"
    OUTPUT_DIR = "../4_images/dashboard/"
    REPORTS_DIR = "../5_reports/" # <-- NUEVO PARÁMETRO
    
    dashboard = StrategyDashboard(ABT_PATH, OUTPUT_DIR, REPORTS_DIR)
    dashboard.ejecutar_todos_los_reportes()