# Diccionario de Datos: Tablas Analíticas Base (ABT)
**Capa de Infraestructura:** Feature Engineering (Fase 3)  
**Proyecto:** Estrategia de Marketing e Inteligencia de Negocios - Mundial FIFA 2026  
**Formato de Almacenamiento:** Valores Separados por Comas (.csv)  

---

## 1. Propósito del Documento
Este componente de gobernanza de datos provee la documentación técnica y el esquema estructural de las tres **Analytical Base Tables (ABT)** generadas en la fase de ingeniería. El objetivo es proporcionar un marco de referencia unificado para la capa de Inteligencia de Negocios (BI), garantizando la correcta interpretación de los metadatos, los tipos de variables y la procedencia algorítmica de cada indicador compuesto.

---

## 2. Especificación Técnica de las Tablas Analíticas

### 2.1. Estructura de la Tabla Maestra: `ABT_Mundial.csv`
Esta tabla consolida las respuestas a nivel de encuesta individual e integra las variables compuestas y segmentaciones estratégicas precalculadas mediante lógica condicional vectorizada.

| Nombre de la Columna | Tipo de Dato | Origen / Regla de Transformación | Descripción / Valores Permitidos |
| :--- | :--- | :--- | :--- |
| `EncuestaID` | Int64 | Campo Clave (Dataset Depurado) | Identificador único y primario de cada encuesta procesada. |
| `RangoEdad` | String / Categórico | Dataset Depurado | Clasificación demográfica original del encuestado por rango de edad. |
| `Genero` | String | Transformación síncrona: `.str.strip().str.title()` | Género homologado del consumidor (Masculino / Femenino / No Binario). |
| `Departamento` | String | Dataset Depurado | Ubicación geográfica estandarizada a nivel departamental dentro de Guatemala. |
| `Disposicion_Gasto_Premium` | String / Categórico | **Ingeniería de Variables (`np.select`):**<br>Cruza el presupuesto habitual por partido (`GastoSnacksPartido`) con la disposición a pagar extra por ediciones especiales (`PagaMasEdicionMundial`). | Clasificación de potencial económico:<br>- `Premium Alta`: Gasto >Q51 **Y** disposición de pago Sí.<br>- `Moderada`: Gasto entre Q25-Q50 **Ó** disposición de pago Sí.<br>- `Sensible Al Precio`: Casos restantes de bajo presupuesto. |
| `Segmento_Lealtad_Mundial` | String / Categórico | **Ingeniería de Variables (`np.select`):**<br>Evalúa la coincidencia de tres criterios comerciales de fidelidad: ver los partidos, comprar diseños personalizados y coleccionar tarjetas oficiales. | Clasificación de fidelidad del cliente:<br>- `Fanático Target (Alto)`: Cumple los 3 criterios.<br>- `Casual`: Cumple con interés parcial o intermitente.<br>- `Espectador Pasivo`: Consumidor con nula intención de compra. |
| `Segmento_Edad_Analitico` | String / Categórico | **Reducción de Dimensionalidad (`.map()`):**<br>Consolida las opciones originales de edad en cuatro macrosegmentos ejecutivos. | Categorías demográficas compactas:<br>- `Jóvenes (<25)`<br>- `Adulto Joven (25-34)`<br>- `Adulto Maduro (35-54)`<br>- `Adulto Mayor (55+)` |

---

### 2.2. Estructura de la Tabla Granular: `ABT_Snacks.csv`
Estructura normalizada diseñada específicamente para el análisis del volumen y participación de mercado de los productos de consumo masivo, donde el registro ha sido desanidado por opción individual elegida.

| Nombre de la Columna | Tipo de Dato | Origen / Regla de Transformación | Descripción / Valores Permitidos |
| :--- | :--- | :--- | :--- |
| `EncuestaID` | Int64 | Clave Foránea (Dataset Depurado) | Llave de vinculación hacia la tabla maestra `ABT_Mundial.csv`. Permite relaciones 1:N. |
| `RangoEdad` | String | Dataset Depurado | Rango de edad del encuestado para segmentación cruzada de productos. |
| `Genero` | String | Transformación síncrona: `.str.strip().str.title()` | Género homologado del consumidor. |
| `Departamento` | String | Dataset Depurado | Ubicación geográfica para análisis de distribución y logística regional. |
| `FrecuenciaConsumoSnacks`| String | Dataset Depurado | Hábito declarado de consumo de alimentos durante las transmisiones de partidos. |
| `SaborPreferido` | String | Transformación síncrona: `.str.strip().str.title()` | Perfil organoléptico preferido del encuestado (ej. Salado, Dulce, Picante). |
| `Snack` | String | **Desanidamiento Estructural (`.explode()`):**<br>Generado tras vectorizar la celda original `SnacksSeleccionados` mediante la separación del caracter punto y coma (`;`). | Nombre individualizado del snack seleccionado. Cada registro representa una mención única. |

---

### 2.3. Estructura de la Tabla Granular: `ABT_Jugadores.csv`
Estructura normalizada orientada al análisis de líderes de opinión de fútbol, útil para la toma de decisiones en campañas publicitarias de embajadores de marca.

| Nombre de la Columna | Tipo de Dato | Origen / Regla de Transformación | Descripción / Valores Permitidos |
| :--- | :--- | :--- | :--- |
| `EncuestaID` | Int64 | Clave Foránea (Dataset Depurado) | Llave de vinculación hacia la tabla maestra `ABT_Mundial.csv`. Permite relaciones 1:N. |
| `RangoEdad` | String | Dataset Depurado | Edad del encuestado, orientada a identificar tendencias generacionales de idolatría. |
| `Genero` | String | Transformación síncrona: `.str.strip().str.title()` | Género homologado del consumidor. |
| `Departamento` | String | Dataset Depurado | Ubicación geográfica del mercado. |
| `SeleccionApoya` | String | Dataset Depurado | Entidad futbolística nacional o internacional por la cual el usuario muestra simpatía. |
| `Jugador` | String | **Desanidamiento Estructural (`.explode()`):**<br>Generado tras vectorizar la celda original `JugadoresInfluyentes` mediante la separación del caracter punto y coma (`;`). | Nombre formateado del futbolista influyente mencionado en la encuesta. |

---

## 3. Normas de Integración Relacional para Modelado de BI
Para resguardar la integridad referencial y evitar duplicidades numéricas artificiales en las pantallas de reportería, se establecen las siguientes directrices de arquitectura:
1. **Esquema del Modelo:** Las tablas deben conectarse bajo un patrón de **Esquema en Estrella**. `ABT_Mundial.csv` se establece como la tabla de hechos central.
2. **Cardinalidad de las Relaciones:** Las uniones desde `ABT_Mundial` hacia `ABT_Snacks` y `ABT_Jugadores` deben configurarse obligatoriamente de **Uno a Muchos (1:N)** utilizando la columna `EncuestaID` como puente de filtrado.
3. **Dirección de Filtrado:** La dirección del filtro debe configurarse en modalidad **Única (Single)**, fluyendo desde la tabla maestra hacia las tablas granulares desanidadas, impidiendo la contaminación del conteo de encuestas base.