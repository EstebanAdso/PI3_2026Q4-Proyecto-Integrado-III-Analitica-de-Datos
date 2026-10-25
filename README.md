# PI3_2026Q4 - Proyecto Integrado III: Analítica de Datos

Proyecto del curso Proyecto Integrado III - Analítica de Datos (IU Digital).

## Objetivo

Construir un mecanismo reutilizable para **obtener, describir, transformar y
resumir datos de un negocio comercial**, con el código versionado en GitHub y
ejecutado automáticamente, y usarlo como base del proyecto integrador:

- Una clase en Python obtiene los datos desde Hugging Face como DataFrame.
- Notebooks de Jupyter describen y transforman esos datos.
- Otra clase en Python resume el DataFrame en un archivo `.txt`.
- GitHub Actions ejecuta los notebooks en cada cambio y deja la evidencia en el repositorio.

## Actividades

| Actividad | Carpeta | Qué contiene |
|---|---|---|
| **EA1** - Carga y creación de dataset | `src/actividad_1/` | Notebook con 8 transformaciones del dataset y sus resúmenes `.txt` |
| **AE2** - Proyecto integrador: ideación, diseño y documentación de la necesidad | `AE2/` | Documento Word con la necesidad y el diseño, notebook de reconocimiento del dataset y resumen `.txt` |

## Dataset

Use **[Olist - Brazilian E-Commerce](https://huggingface.co/datasets/bulutttt/olist-raw-data)**:
datos **reales y anonimizados** de un negocio comercial (marketplace de Brasil)
con clientes, órdenes, facturación, productos y proveedores.

| Ficha | Valor |
|---|---|
| Identificador | `bulutttt/olist-raw-data` |
| Enlace | https://huggingface.co/datasets/bulutttt/olist-raw-data |
| Fuente original | [Brazilian E-Commerce Public Dataset by Olist (Kaggle)](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) |
| Revisión usada en la AE2 | `5acf1f37d7197d4979e714721a1ec13a7c3da728` |
| Split | `train` (único disponible); cada tabla se carga por su archivo `.csv` |
| Periodo | Compras entre septiembre de 2016 y septiembre de 2018 |
| Licencia | CC BY-NC-SA 4.0 (uso no comercial con atribución), según la fuente original |

| Tabla | Contenido |
|---|---|
| Clientes | Clientes y su ciudad/estado |
| Órdenes | Encabezado de cada orden: estado y fechas de compra y entrega |
| Ítems | Detalle de la orden: producto, vendedor, precio y flete |
| Pagos | Facturación de cada orden: medio de pago, cuotas y valor |
| Productos | Catálogo de productos y su categoría |
| Vendedores | Proveedores que venden en el marketplace |
| Categorías | Traducción de las categorías de producto |

Los datos **no se guardan en el repositorio**: se descargan desde Hugging Face al
ejecutar los notebooks. El dataset es público y no requiere registro. En el
repositorio solo quedan los resúmenes y las tablas agregadas que generan los
notebooks.

## AE2 - Necesidad analítica del proyecto integrador

- **Propósito:** formular y documentar una necesidad de analítica descriptiva a
  partir del dataset de Olist, y reconocer sus datos.
- **Beneficiario (escenario hipotético):** el equipo comercial y de operaciones
  de un marketplace.
- **Necesidad:** conocer qué categorías de producto y qué estados de Brasil
  concentran las unidades vendidas y los ingresos, y cómo se comporta el tiempo
  de entrega en esos grupos, para priorizar decisiones comerciales y logísticas.
- **Pregunta de análisis:** ¿cómo se distribuyen las unidades vendidas y los
  ingresos por venta de productos entre las categorías de producto y los estados
  del cliente en las órdenes de Olist registradas entre septiembre de 2016 y
  septiembre de 2018, y cómo varía el tiempo de entrega entre esos grupos?
- **Unidad de análisis:** el ítem de orden (cada fila es un producto vendido).
  El DataFrame tiene 112.650 filas y 30 columnas.

| Archivo | Contenido |
|---|---|
| `AE2/documento/AE2_Necesidad_y_Diseno_Olist.docx` | Documento con portada, introducción, necesidad, justificación, objetivos, marco teórico, metodología (ficha, diccionario de variables, alcance y diseño), reconocimiento del dataset y referencias |
| `AE2/notebooks/AE2_reconocimiento_olist.ipynb` | Obtiene 6 tablas de Hugging Face, las une en un DataFrame de ítems y muestra registros, dimensiones, columnas, tipos y nulos. Genera y verifica el resumen `.txt` |
| `AE2/resultados/resumen_dataframe.txt` | Resumen generado automáticamente: dataset, revisión, split, archivos, filas, columnas, tipos y nulos |

## Archivos del proyecto

```
.
├── .github/workflows/ejecutar-notebooks.yml
├── AE2/
│   ├── documento/
│   │   └── AE2_Necesidad_y_Diseno_Olist.docx
│   ├── notebooks/
│   │   └── AE2_reconocimiento_olist.ipynb
│   └── resultados/
│       └── resumen_dataframe.txt
├── src/
│   ├── clases_po/
│   │   ├── __init__.py
│   │   ├── hf_loader.py
│   │   └── dataset_summarizer.py
│   └── actividad_1/
│       ├── EA1_olist_comercial.ipynb
│       ├── datos/
│       └── reportes/
├── requirements.txt
└── README.md
```

| Archivo | Qué hace |
|---|---|
| `src/clases_po/hf_loader.py` | Clase **`HFDatasetLoader`**. Se conecta a Hugging Face, descarga una tabla del dataset y la devuelve como DataFrame de pandas. Permite indicar el split, el archivo (`data_files`) y la revisión. Con `load_tables()` carga varias tablas a la vez. |
| `src/clases_po/dataset_summarizer.py` | Clase **`DatasetSummarizer`**. Recibe un DataFrame y genera un resumen: origen de los datos, filas, columnas, tipos, valores nulos, duplicados, estadísticas, valores más frecuentes y rango de fechas. Lo muestra en pantalla o lo guarda en `.txt`. |
| `src/clases_po/__init__.py` | Permite importar las dos clases con `from clases_po import HFDatasetLoader, DatasetSummarizer`. |
| `src/actividad_1/EA1_olist_comercial.ipynb` | Notebook de la EA1: carga las tablas, aplica 8 transformaciones y resume el resultado. |
| `AE2/notebooks/AE2_reconocimiento_olist.ipynb` | Notebook de la AE2: obtiene el dataset, lo describe y genera el resumen `.txt`. |
| `.github/workflows/ejecutar-notebooks.yml` | GitHub Action que ejecuta los dos notebooks en cada push a `main` y sube los resultados al repositorio. |
| `requirements.txt` | Librerías necesarias. |

## Instalación

Requiere Python 3.12.

```bash
git clone https://github.com/EstebanAdso/PI3_2026Q4-Proyecto-Integrado-III-Analitica-de-Datos.git
cd PI3_2026Q4-Proyecto-Integrado-III-Analitica-de-Datos
python -m venv .venv
```

Activar el entorno virtual:

```bash
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Linux / macOS
source .venv/bin/activate
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

## Uso

### Ejecutar los notebooks

Abrirlos y ejecutar las celdas en orden:

```bash
jupyter notebook
```

O ejecutarlos completos desde la terminal. AE2:

```bash
cd AE2/notebooks
jupyter nbconvert --to notebook --execute --inplace AE2_reconocimiento_olist.ipynb
```

EA1:

```bash
cd src/actividad_1
jupyter nbconvert --to notebook --execute --inplace EA1_olist_comercial.ipynb
```

### Usar las clases

Desde un script o notebook ubicado en `src/` (los notebooks del proyecto ya
agregan `src` a la ruta automáticamente):

```python
from clases_po import DatasetSummarizer, HFDatasetLoader

# Cargar una tabla
ordenes = HFDatasetLoader("bulutttt/olist-raw-data", data_files="olist_orders_dataset.csv").load()

# Cargar varias tablas
tablas = HFDatasetLoader.load_tables(
    "bulutttt/olist-raw-data",
    {"clientes": "olist_customers_dataset.csv", "pagos": "olist_order_payments_dataset.csv"},
)

# Generar el resumen
DatasetSummarizer(ordenes, titulo="Órdenes", metadatos={"Dataset": "bulutttt/olist-raw-data"}).guardar("reportes/ordenes.txt")
```

## Proceso de los notebooks

### AE2 - Reconocimiento del dataset

1. **Obtención:** descarga 6 tablas de Olist con `HFDatasetLoader`, fijando la revisión del repositorio.
2. **Construcción del DataFrame:** une ítems, órdenes, productos, categorías, clientes y vendedores (una fila por producto vendido) y verifica que no se pierdan ni dupliquen filas.
3. **Descripción básica:** registros de ejemplo, dimensiones, columnas, tipos, nulos y variables principales.
4. **Resumen:** `DatasetSummarizer` genera `AE2/resultados/resumen_dataframe.txt` y el notebook verifica que corresponda al DataFrame.

### EA1 - Transformaciones

1. **Carga:** descarga las 7 tablas de Olist con `HFDatasetLoader`.
2. **Transformaciones:**
   1. Seleccionar, renombrar y traducir las columnas de productos.
   2. Reemplazar las categorías vacías por `sin_categoria`.
   3. Convertir las fechas de texto a tipo fecha.
   4. Filtrar solo las órdenes entregadas.
   5. Agrupar los pagos por orden (total facturado, cuotas y medio de pago).
   6. Unir ítems, órdenes, productos, vendedores, clientes y pagos en una sola tabla de ventas.
   7. Crear columnas nuevas: total de la línea, días de entrega, entrega tardía, mes y si cliente y vendedor están en el mismo estado.
   8. Agrupar las ventas por vendedor y por categoría/mes.
3. **Resumen:** pasa la tabla de ventas transformada a `DatasetSummarizer` y guarda el `.txt`.

## Resultados generados

| Archivo | Contenido |
|---|---|
| `AE2/resultados/resumen_dataframe.txt` | Resumen del DataFrame de reconocimiento de la AE2 |
| `src/actividad_1/reportes/ventas_olist.txt` | Resumen de la tabla de ventas transformada (EA1) |
| `src/actividad_1/reportes/ventas_por_vendedor.txt` | Resumen de las ventas agrupadas por vendedor (EA1) |
| `src/actividad_1/datos/ventas_por_vendedor.csv` | Ventas, órdenes y tiempos de entrega por vendedor (EA1) |
| `src/actividad_1/datos/ventas_por_categoria_mes.csv` | Órdenes, ingreso y flete por categoría y mes (EA1) |

## Ejecución automática (GitHub Actions)

El archivo `.github/workflows/ejecutar-notebooks.yml` define un proceso que
GitHub ejecuta en sus propios servidores **cada vez que se hace push a `main`**.
También se puede lanzar manualmente desde la pestaña **Actions** del repositorio.

El workflow no guarda datos: **ejecuta los notebooks desde cero** en una
máquina limpia, sin nada del computador local, en este orden:

1. **Descargar el repositorio** en una máquina Linux nueva.
2. **Configurar Python 3.12** e instalar las librerías de `requirements.txt`.
3. **Limpiar resultados anteriores:** borra el contenido de
   `src/actividad_1/datos/`, `src/actividad_1/reportes/` y `AE2/resultados/`.
4. **Ejecutar los notebooks** con `jupyter nbconvert --execute`: descargan el
   dataset desde Hugging Face y generan de nuevo los `.csv` y los `.txt`.
5. **Guardar los resultados:** hace un commit como `github-actions[bot]` con los
   notebooks ejecutados (con sus salidas visibles), los `.csv` y los `.txt`. El
   mensaje lleva `[skip ci]` para que ese commit no vuelva a disparar el
   workflow y no se forme un ciclo infinito.

### Evidencia de funcionamiento

- En la pestaña **Actions**, la ejecución aparece en verde.
- En el historial aparece el commit `chore: actualizar resultados de los notebooks [skip ci]`
  hecho por `github-actions[bot]`. Como los `.txt` incluyen la fecha y hora de
  generación, este commit aparece en cada ejecución exitosa.

### Idempotencia

El proceso es **idempotente**: ejecutarlo una o muchas veces deja el
repositorio en el mismo estado, porque cada ejecución parte de cero y produce
los mismos resultados a partir del mismo dataset (lo único que cambia es la
fecha de generación de los `.txt`). No se acumulan archivos viejos ni se mezclan
resultados de ejecuciones anteriores.

Por eso **no es necesario borrar manualmente las carpetas de resultados** antes
de hacer push:

- En GitHub Actions, el paso 3 las limpia antes de ejecutar los notebooks.
  Los archivos que se suban desde el computador local nunca se usan: siempre se
  regeneran a partir de los datos de Hugging Face. Si la descarga o un notebook
  fallan, el workflow queda en rojo aunque esos archivos ya estén en el
  repositorio.
- En local, los notebooks crean las carpetas si no existen y sobrescriben los
  mismos archivos en cada ejecución.
