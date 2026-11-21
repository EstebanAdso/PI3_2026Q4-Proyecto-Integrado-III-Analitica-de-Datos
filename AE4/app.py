"""Aplicación de Streamlit de la AE4: métricas y visualización del proyecto Olist.

Lee las tablas de resultados generadas por el notebook de la AE3 (AE3/resultados/)
y construye a partir de ellas las métricas, los gráficos y las respuestas a las
preguntas de negocio.

Ejecutar desde la raíz del repositorio:
    streamlit run AE4/app.py
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

RAIZ = Path(__file__).resolve().parents[1]
DIR_RESULTADOS = RAIZ / "AE3" / "resultados"
REPOSITORIO = "https://github.com/EstebanAdso/PI3_2026Q4-Proyecto-Integrado-III-Analitica-de-Datos"

AZUL = "#2a78d6"      # serie principal
NARANJA = "#eb6834"   # resaltado / referencia
GRIS = "#9a9892"      # grupos con pocos datos

st.set_page_config(page_title="Olist: ventas y entregas", page_icon="📦", layout="wide")


# ----------------------------------------------------------------------------- datos
@st.cache_data
def cargar_tablas() -> dict[str, pd.DataFrame]:
    """Carga las cinco tablas de resultados exportadas por el notebook de la AE3."""
    archivos = {
        "p1": "tabla_p1_categorias.csv",
        "p2": "tabla_p2_estados.csv",
        "p3": "tabla_p3_entrega_estados.csv",
        "p4": "tabla_p4_entrega_categorias.csv",
        "p5": "tabla_p5_mensual.csv",
    }
    return {clave: pd.read_csv(DIR_RESULTADOS / archivo) for clave, archivo in archivos.items()}


def num(valor: float, decimales: int = 0) -> str:
    """Formato numérico en español: 1.234.567,89"""
    texto = f"{valor:,.{decimales}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def mostrar_grafico(fig: go.Figure, altura: int = 420) -> None:
    fig.update_layout(
        height=altura,
        separators=",.",
        margin=dict(l=10, r=10, t=60, b=10),
        hoverlabel=dict(font_size=13),
        title_font_size=16,
    )
    fig.update_xaxes(showgrid=True, gridwidth=1, zeroline=False)
    fig.update_yaxes(showgrid=False)
    st.plotly_chart(fig, width="stretch")


def bloque_texto(titulo: str, contenido: str) -> None:
    st.markdown(f"**{titulo}**")
    st.markdown(contenido)


tablas = cargar_tablas()
p1, p2, p3, p4, p5 = (tablas[k] for k in ("p1", "p2", "p3", "p4", "p5"))

# Totales generales (todas las tablas deben coincidir entre sí)
TOTAL_UNIDADES = int(p1["unidades"].sum())
TOTAL_INGRESOS = float(p1["ingresos_brl"].sum())
TOTAL_ORDENES = int(p5["ordenes"].sum())
TOTAL_ENTREGADOS = int(p3["items_entregados"].sum())
TOTAL_TARDIAS = int(p3["entregas_tardias"].sum())
PCT_TARDIAS = TOTAL_TARDIAS / TOTAL_ENTREGADOS * 100
CONSISTENTE = (
    TOTAL_UNIDADES == p2["unidades"].sum() == p5["unidades"].sum()
    and abs(TOTAL_INGRESOS - p2["ingresos_brl"].sum()) < 0.5
    and abs(TOTAL_INGRESOS - p5["ingresos_brl"].sum()) < 0.5
    and TOTAL_ENTREGADOS == p4["items_entregados"].sum()
    and TOTAL_TARDIAS == p4["entregas_tardias"].sum()
)

# Subtotales por región (sumas de la tabla P2)
regiones = (
    p2.groupby("region_cliente", as_index=False)[["unidades", "ingresos_brl"]].sum()
    .assign(
        participacion_ingresos_pct=lambda d: d["ingresos_brl"] / d["ingresos_brl"].sum() * 100,
        ingreso_promedio_item_brl=lambda d: d["ingresos_brl"] / d["unidades"],
    )
    .sort_values("ingresos_brl", ascending=False)
)
regiones_entrega = (
    p3.groupby("region_cliente", as_index=False)[["items_entregados", "entregas_tardias"]].sum()
    .assign(pct_entregas_tardias=lambda d: d["entregas_tardias"] / d["items_entregados"] * 100)
    .set_index("region_cliente")
)

# ----------------------------------------------------------------------------- navegación
PAGINAS = [
    "Inicio: necesidad y datos",
    "P1. Categorías",
    "P2. Estados",
    "P3. Entregas por estado",
    "P4. Entregas por categoría",
    "P5. Evolución mensual",
    "Conclusiones",
]
st.sidebar.title("Olist 2016-2018")
st.sidebar.caption("Proyecto Integrado III - Analítica de Datos")
pagina = st.sidebar.radio("Secciones", PAGINAS)
st.sidebar.divider()
st.sidebar.markdown(f"[Repositorio en GitHub]({REPOSITORIO})")
st.sidebar.caption("Datos: tablas de resultados de la AE3 (`AE3/resultados/`).")
if CONSISTENTE:
    st.sidebar.success("Totales de las 5 tablas verificados: coinciden entre sí.", icon="✅")
else:
    st.sidebar.error("Los totales de las tablas no coinciden. Ejecuta de nuevo el notebook de la AE3.", icon="⚠️")


# ----------------------------------------------------------------------------- Inicio
if pagina == PAGINAS[0]:
    st.title("Ventas y entregas en el marketplace Olist (2016-2018)")
    st.markdown(
        "Análisis descriptivo de las ventas por **categoría de producto**, **estado del cliente** y **mes**, "
        "y del **tiempo de entrega**, para apoyar la priorización comercial y logística de un marketplace."
    )

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Unidades vendidas", num(TOTAL_UNIDADES), help="Ítems de orden vendidos (sin órdenes canceladas ni no disponibles)")
    c2.metric("Órdenes", num(TOTAL_ORDENES))
    c3.metric("Ingresos (BRL)", num(TOTAL_INGRESOS / 1e6, 2) + " M", help="Suma del precio de los productos, sin flete")
    c4.metric("Ítems entregados", num(TOTAL_ENTREGADOS), help="Base para medir el tiempo de entrega")
    c5.metric("Entregas tardías", num(PCT_TARDIAS, 2) + " %", help="Entregas posteriores a la fecha estimada")

    st.subheader("Necesidad")
    st.markdown(
        "El equipo comercial y de operaciones de un marketplace (escenario hipotético) necesita conocer **qué categorías "
        "de producto y qué estados de Brasil concentran las unidades vendidas y los ingresos**, y **cómo se comporta el "
        "tiempo de entrega** en esos grupos, para priorizar decisiones comerciales y logísticas."
    )

    st.subheader("Preguntas de negocio")
    st.markdown(
        """
| Pregunta | Métrica principal | Unidad |
|---|---|---|
| **P1.** ¿Qué categorías concentran las unidades vendidas y los ingresos? | Ingresos, unidades y participación por categoría | BRL, ítems, % |
| **P2.** ¿Cómo se distribuyen las ventas y el ingreso promedio por ítem entre los estados? | Ingresos, participación e ingreso promedio por ítem | BRL, %, BRL/ítem |
| **P3.** ¿Cómo varían el tiempo de entrega y las entregas tardías entre estados? | Mediana de días de entrega y % de entregas tardías | días, % |
| **P4.** ¿Cómo varían el tiempo de entrega y las entregas tardías entre categorías? | Mediana de días de entrega y % de entregas tardías | días, % |
| **P5.** ¿Cómo evolucionan mes a mes las unidades y los ingresos? | Unidades e ingresos por mes de compra | ítems, BRL |
"""
    )

    st.subheader("Datos utilizados")
    st.markdown(
        f"""
- **Dataset:** *Brazilian E-Commerce Public Dataset by Olist*, copia pública en Hugging Face
  ([`bulutttt/olist-raw-data`](https://huggingface.co/datasets/bulutttt/olist-raw-data)). Datos reales y anonimizados,
  licencia CC BY-NC-SA 4.0.
- **Periodo:** compras entre septiembre de 2016 y septiembre de 2018.
- **Unidad de análisis:** el ítem de orden (cada fila es un producto vendido).
- **Preparación (AE3):** {num(TOTAL_UNIDADES)} ítems de {num(TOTAL_ORDENES)} órdenes, sin órdenes canceladas ni no
  disponibles; fechas convertidas, categorías normalizadas y variables derivadas (días de entrega, entrega tardía,
  mes de compra y región del cliente según el IBGE).
- **Ingresos** = precio de venta de los productos en reales brasileños (BRL), **sin flete**. No hay datos de costos.
"""
    )


# ----------------------------------------------------------------------------- P1
elif pagina == PAGINAS[1]:
    st.title("P1. ¿Qué categorías concentran las unidades vendidas y los ingresos?")
    top10 = p1.head(10)
    cat80 = int((p1["participacion_ingresos_acum_pct"] < 80).sum() + 1)
    lider_u = p1.sort_values("unidades", ascending=False).iloc[0]

    with st.expander("Métrica: definición, cálculo y unidad", expanded=True):
        st.markdown(
            "- **Ingresos (BRL):** suma de `price` de los ítems de la categoría (sin flete).\n"
            "- **Unidades (ítems):** cantidad de ítems vendidos de la categoría.\n"
            "- **Participación (%):** ingresos (o unidades) de la categoría ÷ total × 100.\n"
            "- **Ingreso promedio por ítem (BRL/ítem):** ingresos ÷ unidades."
        )

    c1, c2, c3 = st.columns(3)
    c1.metric("Ingresos del top 10", num(top10["participacion_ingresos_pct"].sum(), 2) + " %")
    c2.metric("Categorías para el 80 % de ingresos", f"{cat80} de {len(p1)}")
    c3.metric(f"Más unidades: {lider_u['categoria_producto']}", num(lider_u["unidades"]) + " ítems")

    medidas = {
        "Ingresos (BRL)": ("ingresos_brl", ",.2f"),
        "Unidades vendidas (ítems)": ("unidades", ",d"),
        "Ingreso promedio por ítem (BRL)": ("ingreso_promedio_item_brl", ",.2f"),
    }
    n_cat = st.slider("Cantidad de categorías a mostrar (ordenadas por ingresos)", 5, len(p1), 10)
    medida = st.radio("Medida del gráfico", list(medidas), horizontal=True)
    columna, formato = medidas[medida]
    datos = p1.head(n_cat).sort_values(columna)
    fig = px.bar(
        datos, x=columna, y="categoria_producto", orientation="h",
        title=f"{medida} por categoría · {n_cat} categorías con más ingresos · Olist, sep 2016 - sep 2018",
        labels={columna: medida, "categoria_producto": "Categoría"},
        custom_data=["unidades", "ingresos_brl", "participacion_ingresos_pct", "ingreso_promedio_item_brl"],
    )
    fig.update_traces(
        marker_color=AZUL,
        hovertemplate="<b>%{y}</b><br>Ingresos: %{customdata[1]:,.2f} BRL<br>Participación: %{customdata[2]:.2f} %"
                      "<br>Unidades: %{customdata[0]:,d}<br>Ingreso promedio: %{customdata[3]:,.2f} BRL<extra></extra>",
    )
    mostrar_grafico(fig, altura=max(380, 28 * n_cat + 120))

    with st.expander("Ver tabla de resultados (tabla_p1_categorias.csv)"):
        st.dataframe(p1, hide_index=True, width="stretch")

    r1, r2 = top10.iloc[0], top10.iloc[1]
    bloque_texto("Qué muestran los datos", (
        f"Las ventas se concentran en pocas categorías: las 10 con más ingresos reúnen el "
        f"**{num(top10['participacion_ingresos_pct'].sum(), 2)} %** de los ingresos y {cat80} de las {len(p1)} "
        f"categorías alcanzan el 80 %. **{r1['categoria_producto']}** lidera en ingresos ({num(r1['ingresos_brl'], 2)} BRL). "
        f"**{lider_u['categoria_producto']}** vende más unidades ({num(lider_u['unidades'])}) pero tiene un ingreso promedio "
        f"bajo ({num(lider_u['ingreso_promedio_item_brl'], 2)} BRL/ítem), mientras que **{r2['categoria_producto']}** es "
        f"segunda en ingresos con menos unidades, por su ingreso promedio de {num(r2['ingreso_promedio_item_brl'], 2)} BRL/ítem. "
        "Cambia la medida del gráfico para ver que el ranking no es el mismo."
    ))
    bloque_texto("Decisión que apoya",
                 "Elegir categorías prioritarias según el objetivo: **volumen** (unidades) para la operación logística o "
                 "**valor** (ingresos) para campañas comerciales.")
    bloque_texto("Limitaciones",
                 "Los ingresos no son rentabilidad: no hay costos ni márgenes, así que no se puede afirmar qué categoría "
                 "gana más dinero. Los ingresos no incluyen flete ni descuentos. `sin_categoria` agrupa 1.603 ítems sin categoría.")


# ----------------------------------------------------------------------------- P2
elif pagina == PAGINAS[2]:
    st.title("P2. ¿Cómo se distribuyen las ventas entre los estados del cliente?")
    with st.expander("Métrica: definición, cálculo y unidad", expanded=True):
        st.markdown(
            "- **Ingresos (BRL)** y **unidades (ítems)** por estado del cliente.\n"
            "- **Participación (%):** ingresos del estado ÷ total × 100.\n"
            "- **Ingreso promedio por ítem (BRL/ítem):** ingresos ÷ unidades.\n"
            "- **Región:** agrupación de los estados según la división del IBGE (variable incorporada en la AE3)."
        )

    sp = p2.set_index("customer_state").loc["SP"]
    top3 = p2.head(3)
    c1, c2, c3 = st.columns(3)
    c1.metric("Participación de SP en ingresos", num(sp["participacion_ingresos_pct"], 2) + " %")
    c2.metric("SP + RJ + MG", num(top3["ingresos_brl"].sum() / p2["ingresos_brl"].sum() * 100, 2) + " %")
    sudeste = regiones.set_index("region_cliente").loc["Sudeste"]
    c3.metric("Región Sudeste", num(sudeste["participacion_ingresos_pct"], 2) + " %")

    col_izq, col_der = st.columns([3, 2])
    with col_izq:
        medidas = {
            "Ingresos (BRL)": "ingresos_brl",
            "Unidades vendidas (ítems)": "unidades",
            "Ingreso promedio por ítem (BRL)": "ingreso_promedio_item_brl",
        }
        medida = st.radio("Medida del gráfico", list(medidas), horizontal=True)
        columna = medidas[medida]
        datos = p2.sort_values(columna)
        datos["etiqueta"] = datos["customer_state"] + " · " + datos["region_cliente"]
        fig = px.bar(
            datos, x=columna, y="etiqueta", orientation="h",
            title=f"{medida} por estado del cliente · 27 estados · Olist, sep 2016 - sep 2018",
            labels={columna: medida, "etiqueta": "Estado · región"},
            custom_data=["unidades", "ingresos_brl", "participacion_ingresos_pct", "ingreso_promedio_item_brl"],
        )
        fig.update_traces(
            marker_color=[GRIS if u < 300 else AZUL for u in datos["unidades"]],
            hovertemplate="<b>%{y}</b><br>Ingresos: %{customdata[1]:,.2f} BRL (%{customdata[2]:.2f} %)"
                          "<br>Unidades: %{customdata[0]:,d}<br>Ingreso promedio: %{customdata[3]:,.2f} BRL<extra></extra>",
        )
        mostrar_grafico(fig, altura=760)
        st.caption("Barras grises: estados con menos de 300 unidades (sus promedios son menos estables).")
    with col_der:
        fig_r = px.bar(
            regiones.sort_values("participacion_ingresos_pct"), x="participacion_ingresos_pct", y="region_cliente",
            orientation="h", title="Participación en los ingresos por región (%)",
            labels={"participacion_ingresos_pct": "Participación en ingresos (%)", "region_cliente": "Región"},
            text="participacion_ingresos_pct", custom_data=["ingreso_promedio_item_brl", "ingresos_brl"],
        )
        fig_r.update_traces(
            marker_color=AZUL, texttemplate="%{text:.2f} %", textposition="outside", cliponaxis=False,
            hovertemplate="<b>%{y}</b><br>Ingresos: %{customdata[1]:,.2f} BRL (%{x:.2f} %)"
                          "<br>Ingreso promedio: %{customdata[0]:,.2f} BRL<extra></extra>",
        )
        fig_r.update_xaxes(range=[0, regiones["participacion_ingresos_pct"].max() * 1.25])
        mostrar_grafico(fig_r, altura=340)
        fig_p = px.bar(
            regiones.sort_values("ingreso_promedio_item_brl"), x="ingreso_promedio_item_brl", y="region_cliente",
            orientation="h", title="Ingreso promedio por ítem por región (BRL)",
            labels={"ingreso_promedio_item_brl": "Ingreso promedio por ítem (BRL)", "region_cliente": "Región"},
            text="ingreso_promedio_item_brl",
        )
        fig_p.update_traces(marker_color=AZUL, texttemplate="%{text:,.2f}", textposition="outside", cliponaxis=False,
                            hovertemplate="<b>%{y}</b><br>%{x:,.2f} BRL por ítem<extra></extra>")
        fig_p.update_xaxes(range=[0, regiones["ingreso_promedio_item_brl"].max() * 1.25])
        mostrar_grafico(fig_p, altura=340)

    with st.expander("Ver tabla de resultados (tabla_p2_estados.csv)"):
        st.dataframe(p2, hide_index=True, width="stretch")

    reg = regiones.set_index("region_cliente")
    bloque_texto("Qué muestran los datos", (
        f"Las ventas se concentran en el Sudeste (**{num(reg.loc['Sudeste', 'participacion_ingresos_pct'], 2)} %** de los "
        f"ingresos); solo São Paulo aporta el {num(sp['participacion_ingresos_pct'], 2)} %. El Norte aporta el "
        f"{num(reg.loc['Norte', 'participacion_ingresos_pct'], 2)} %. El ingreso promedio por ítem sigue el patrón "
        f"contrario: es mayor en el Norte ({num(reg.loc['Norte', 'ingreso_promedio_item_brl'], 2)} BRL) y el Nordeste "
        f"({num(reg.loc['Nordeste', 'ingreso_promedio_item_brl'], 2)} BRL) que en el Sudeste "
        f"({num(reg.loc['Sudeste', 'ingreso_promedio_item_brl'], 2)} BRL)."
    ))
    bloque_texto("Decisión que apoya",
                 "SP, RJ y MG son los mercados de mayor volumen para concentrar esfuerzos comerciales. El Norte y el "
                 "Nordeste compran menos pero cada ítem vale más: son candidatos a crecer si mejora su logística (ver P3).")
    bloque_texto("Limitaciones",
                 "El análisis describe la diferencia en el ingreso promedio pero no su causa (por ejemplo, una mezcla de "
                 "categorías distinta). Los estados con pocas unidades, como RR (51) y AP (82), tienen promedios inestables.")


# ----------------------------------------------------------------------------- P3
elif pagina == PAGINAS[3]:
    st.title("P3. ¿Cómo varían el tiempo de entrega y las entregas tardías entre estados?")
    with st.expander("Métrica: definición, cálculo y unidad", expanded=True):
        st.markdown(
            "- **Días de entrega:** fecha de entrega al cliente − fecha de compra, en días. Solo ítems de órdenes "
            "entregadas con fecha.\n"
            "- **Mediana de días (días):** valor central; se prefiere al promedio porque hay entregas extremadamente largas.\n"
            "- **% de entregas tardías (%):** ítems entregados después de la fecha estimada ÷ ítems entregados × 100."
        )

    e = p3.set_index("customer_state")
    c1, c2, c3 = st.columns(3)
    c1.metric("Mediana en SP", num(e.loc["SP", "mediana_dias_entrega"], 2) + " días")
    lento = p3.iloc[0]
    c2.metric("Mediana más alta", f"{lento['customer_state']}: {num(lento['mediana_dias_entrega'], 2)} días")
    c3.metric("Entregas tardías (total)", num(PCT_TARDIAS, 2) + " %")

    datos = p3.sort_values("mediana_dias_entrega").copy()
    datos["etiqueta"] = datos["customer_state"] + " · " + datos["region_cliente"]
    col_izq, col_der = st.columns(2)
    with col_izq:
        fig = px.bar(
            datos, x="mediana_dias_entrega", y="etiqueta", orientation="h",
            title="Mediana de días de entrega por estado del cliente",
            labels={"mediana_dias_entrega": "Mediana de días de entrega (días)", "etiqueta": "Estado · región"},
            custom_data=["items_entregados", "promedio_dias_entrega"],
        )
        fig.update_traces(
            marker_color=[GRIS if n < 300 else AZUL for n in datos["items_entregados"]],
            hovertemplate="<b>%{y}</b><br>Mediana: %{x:.2f} días<br>Promedio: %{customdata[1]:.2f} días"
                          "<br>Ítems entregados: %{customdata[0]:,d}<extra></extra>",
        )
        mostrar_grafico(fig, altura=760)
    with col_der:
        datos_t = datos.copy()
        fig_t = px.bar(
            datos_t, x="pct_entregas_tardias", y="etiqueta", orientation="h",
            title="% de entregas tardías por estado (mismo orden)",
            labels={"pct_entregas_tardias": "Entregas posteriores a la fecha estimada (%)", "etiqueta": "Estado · región"},
            custom_data=["items_entregados", "entregas_tardias"],
        )
        fig_t.update_traces(
            marker_color=[GRIS if n < 300 else NARANJA for n in datos_t["items_entregados"]],
            hovertemplate="<b>%{y}</b><br>Tardías: %{x:.2f} %<br>%{customdata[1]:,d} de %{customdata[0]:,d} ítems<extra></extra>",
        )
        fig_t.add_vline(x=PCT_TARDIAS, line_dash="dash", line_width=1.5,
                        annotation_text=f"Total: {num(PCT_TARDIAS, 2)} %", annotation_position="top")
        mostrar_grafico(fig_t, altura=760)
    st.caption("Periodo: compras de sep 2016 a sep 2018 entregadas. Barras grises: estados con menos de 300 ítems entregados.")

    with st.expander("Ver tabla de resultados (tabla_p3_entrega_estados.csv)"):
        st.dataframe(p3, hide_index=True, width="stretch")

    rg = regiones_entrega
    bloque_texto("Qué muestran los datos", (
        f"El tiempo de entrega crece con la distancia al Sudeste, donde está la mayoría de vendedores: SP tiene la menor "
        f"mediana ({num(e.loc['SP', 'mediana_dias_entrega'], 2)} días) y AM, RR y AP superan los 24 días. Pero el "
        f"**% de entregas tardías no sigue el mismo orden**: el Norte tarda más pero incumple poco "
        f"({num(rg.loc['Norte', 'pct_entregas_tardias'], 2)} %), porque su fecha estimada ya es más amplia; el Nordeste "
        f"tiene el mayor incumplimiento ({num(rg.loc['Nordeste', 'pct_entregas_tardias'], 2)} %), con AL "
        f"({num(e.loc['AL', 'pct_entregas_tardias'], 2)} %) y MA ({num(e.loc['MA', 'pct_entregas_tardias'], 2)} %). "
        f"RJ incumple el {num(e.loc['RJ', 'pct_entregas_tardias'], 2)} % frente a {num(e.loc['SP', 'pct_entregas_tardias'], 2)} % en SP."
    ))
    bloque_texto("Decisión que apoya",
                 "Distinguir dos problemas logísticos: **entregas largas** (Norte), que requieren rutas o centros de "
                 "distribución más cercanos, e **incumplimiento de la fecha prometida** (Nordeste y RJ), que requiere "
                 "revisar las estimaciones o el desempeño de las transportadoras.")
    bloque_texto("Limitaciones",
                 "La medida es por ítem (una orden con varios productos pesa más). Los estados con pocos ítems entregados, "
                 "como RR (46), tienen porcentajes inestables. El análisis no demuestra las causas de las demoras.")


# ----------------------------------------------------------------------------- P4
elif pagina == PAGINAS[4]:
    st.title("P4. ¿Cómo varían el tiempo de entrega y las entregas tardías entre categorías?")
    with st.expander("Métrica: definición, cálculo y unidad", expanded=True):
        st.markdown(
            "Las mismas métricas de P3 (**mediana de días de entrega**, en días, y **% de entregas tardías**, en %), "
            "calculadas por categoría de producto."
        )

    minimo = st.slider("Mostrar categorías con al menos N ítems entregados", 1, 2000, 100, step=50)
    solo_top10 = st.toggle("Solo las 10 categorías con más ingresos (P1)", value=True)
    datos = p4[p4["items_entregados"] >= minimo]
    if solo_top10:
        datos = datos[datos["categoria_producto"].isin(p1.head(10)["categoria_producto"])]
    datos = datos.sort_values("mediana_dias_entrega")

    if datos.empty:
        st.warning("Ninguna categoría cumple el filtro.")
    else:
        altura = max(380, 26 * len(datos) + 120)
        col_izq, col_der = st.columns(2)
        with col_izq:
            fig = px.bar(
                datos, x="mediana_dias_entrega", y="categoria_producto", orientation="h",
                title=f"Mediana de días de entrega por categoría ({len(datos)} categorías)",
                labels={"mediana_dias_entrega": "Mediana de días de entrega (días)", "categoria_producto": "Categoría"},
                custom_data=["items_entregados", "promedio_dias_entrega"],
            )
            fig.update_traces(marker_color=AZUL,
                              hovertemplate="<b>%{y}</b><br>Mediana: %{x:.2f} días<br>Promedio: %{customdata[1]:.2f} días"
                                            "<br>Ítems entregados: %{customdata[0]:,d}<extra></extra>")
            mostrar_grafico(fig, altura=altura)
        with col_der:
            fig_t = px.bar(
                datos, x="pct_entregas_tardias", y="categoria_producto", orientation="h",
                title="% de entregas tardías por categoría (mismo orden)",
                labels={"pct_entregas_tardias": "Entregas posteriores a la fecha estimada (%)", "categoria_producto": "Categoría"},
                custom_data=["items_entregados", "entregas_tardias"],
            )
            fig_t.update_traces(marker_color=NARANJA,
                                hovertemplate="<b>%{y}</b><br>Tardías: %{x:.2f} %<br>%{customdata[1]:,d} de %{customdata[0]:,d} ítems<extra></extra>")
            fig_t.add_vline(x=PCT_TARDIAS, line_dash="dash", line_width=1.5,
                            annotation_text=f"Total: {num(PCT_TARDIAS, 2)} %", annotation_position="top")
            mostrar_grafico(fig_t, altura=altura)

    with st.expander("Ver tabla de resultados (tabla_p4_entrega_categorias.csv)"):
        st.dataframe(p4, hide_index=True, width="stretch")

    t10 = p4[p4["categoria_producto"].isin(p1.head(10)["categoria_producto"])]
    m100 = p4[p4["items_entregados"] >= 100]
    bloque_texto("Qué muestran los datos", (
        f"Entre categorías el tiempo de entrega varía **menos que entre estados**. En las 10 categorías con más ingresos, "
        f"la mediana va de {num(t10['mediana_dias_entrega'].min(), 2)} a {num(t10['mediana_dias_entrega'].max(), 2)} días "
        f"y las entregas tardías van de {num(t10['pct_entregas_tardias'].min(), 2)} % a "
        f"{num(t10['pct_entregas_tardias'].max(), 2)} %, cerca del total ({num(PCT_TARDIAS, 2)} %). Entre las categorías "
        f"con al menos 100 ítems, la más lenta es **office_furniture** ({num(m100['mediana_dias_entrega'].max(), 2)} días, "
        "productos voluminosos). Desactiva el filtro del top 10 para comparar todas."
    ))
    bloque_texto("Decisión que apoya",
                 "Como la categoría influye menos que la región, las acciones logísticas tendrían más alcance si se "
                 "orientan por región; por categoría, solo casos puntuales como los muebles voluminosos.")
    bloque_texto("Limitaciones",
                 f"{int((p4['items_entregados'] < 100).sum())} categorías tienen menos de 100 ítems entregados y sus medidas "
                 "son poco estables. Categoría y región se mezclan (una categoría puede venderse más en estados lejanos) "
                 "y este análisis descriptivo no separa ambos efectos.")


# ----------------------------------------------------------------------------- P5
elif pagina == PAGINAS[5]:
    st.title("P5. ¿Cómo evolucionan mes a mes las unidades vendidas y los ingresos?")
    with st.expander("Métrica: definición, cálculo y unidad", expanded=True):
        st.markdown(
            "- **Unidades (ítems)** e **ingresos (BRL)** agrupados por mes de compra (`AAAA-MM`).\n"
            "- **Ingreso promedio por ítem (BRL/ítem):** ingresos ÷ unidades del mes.\n"
            "- Los meses con menos de 100 unidades corresponden al inicio y al corte del dataset."
        )

    excluir = st.toggle("Ocultar meses con menos de 100 unidades (inicio y corte del dataset)", value=True)
    datos = p5[p5["unidades"] >= 100] if excluir else p5
    mx = p5.loc[p5["ingresos_brl"].idxmax()]
    fechas = pd.to_datetime(p5["anio_mes_compra"])
    ingresos_ea = p5.assign(anio=fechas.dt.year, mes=fechas.dt.month).query("mes <= 8").groupby("anio")["ingresos_brl"].sum()
    crec = (ingresos_ea.loc[2018] / ingresos_ea.loc[2017] - 1) * 100

    c1, c2, c3 = st.columns(3)
    c1.metric(f"Mes con más ingresos: {mx['anio_mes_compra']}", num(mx["ingresos_brl"], 2) + " BRL")
    c2.metric("Ingresos ene-ago 2018 vs. 2017", "+" + num(crec, 2) + " %")
    c3.metric("Meses en la serie", str(len(datos)))

    fig = px.line(
        datos, x="anio_mes_compra", y="ingresos_brl", markers=True,
        title="Ingresos por mes de compra (BRL) · Olist",
        labels={"anio_mes_compra": "Mes de compra", "ingresos_brl": "Ingresos (BRL)"},
        custom_data=["unidades", "ingreso_promedio_item_brl"],
    )
    fig.update_traces(line=dict(color=AZUL, width=2), marker=dict(size=8),
                      hovertemplate="<b>%{x}</b><br>Ingresos: %{y:,.2f} BRL<br>Unidades: %{customdata[0]:,d}"
                                    "<br>Ingreso promedio: %{customdata[1]:,.2f} BRL<extra></extra>")
    fig.update_layout(hovermode="x unified")
    fig.update_xaxes(tickformat="%Y-%m")
    mostrar_grafico(fig, altura=380)

    col_izq, col_der = st.columns(2)
    with col_izq:
        fig_u = px.line(datos, x="anio_mes_compra", y="unidades", markers=True,
                        title="Unidades vendidas por mes (ítems)",
                        labels={"anio_mes_compra": "Mes de compra", "unidades": "Unidades (ítems)"})
        fig_u.update_traces(line=dict(color=AZUL, width=2), marker=dict(size=8),
                            hovertemplate="<b>%{x}</b><br>%{y:,d} ítems<extra></extra>")
        fig_u.update_xaxes(tickformat="%Y-%m")
        mostrar_grafico(fig_u, altura=340)
    with col_der:
        fig_p = px.line(datos, x="anio_mes_compra", y="ingreso_promedio_item_brl", markers=True,
                        title="Ingreso promedio por ítem por mes (BRL)",
                        labels={"anio_mes_compra": "Mes de compra", "ingreso_promedio_item_brl": "Ingreso promedio por ítem (BRL)"})
        fig_p.update_traces(line=dict(color=AZUL, width=2), marker=dict(size=8),
                            hovertemplate="<b>%{x}</b><br>%{y:,.2f} BRL por ítem<extra></extra>")
        fig_p.update_yaxes(rangemode="tozero")
        fig_p.update_xaxes(tickformat="%Y-%m")
        mostrar_grafico(fig_p, altura=340)

    with st.expander("Ver tabla de resultados (tabla_p5_mensual.csv)"):
        st.dataframe(p5, hide_index=True, width="stretch")

    completos = p5[p5["unidades"] >= 100]
    bloque_texto("Qué muestran los datos", (
        f"Las ventas crecieron: entre enero y agosto de 2018 los ingresos fueron **{num(crec, 2)} % mayores** que en los "
        f"mismos meses de 2017. El pico fue **noviembre de 2017** ({num(mx['ingresos_brl'], 2)} BRL; "
        f"{num(mx['unidades'])} ítems) y desde 2018 las ventas se estabilizan entre unas 7.000 y 8.200 unidades por mes. "
        f"El ingreso promedio por ítem se mantiene entre {num(completos['ingreso_promedio_item_brl'].min(), 2)} y "
        f"{num(completos['ingreso_promedio_item_brl'].max(), 2)} BRL: el crecimiento viene de **más unidades**, no de precios más altos."
    ))
    bloque_texto("Decisión que apoya",
                 "Planificar campañas y capacidad logística para los meses de mayor demanda, como noviembre.")
    bloque_texto("Limitaciones",
                 "Los meses 2016-09, 2016-11, 2016-12 y 2018-09 tienen menos de 100 unidades (2016-11 no tiene ventas): "
                 "reflejan el inicio y el corte del dataset, no caídas reales. Los ingresos no se ajustan por inflación.")


# ----------------------------------------------------------------------------- Conclusiones
else:
    st.title("Conclusiones, recomendaciones y limitaciones")
    top10 = p1.head(10)
    reg = regiones.set_index("region_cliente")
    rg = regiones_entrega

    st.subheader("Conclusiones")
    st.markdown(f"""
1. **Concentración por categoría (P1):** 10 de {len(p1)} categorías generan el {num(top10['participacion_ingresos_pct'].sum(), 2)} %
   de los ingresos. Volumen y valor no coinciden: hay categorías con muchas unidades y bajo ingreso por ítem, y al revés.
2. **Concentración regional (P2):** el Sudeste reúne el {num(reg.loc['Sudeste', 'participacion_ingresos_pct'], 2)} % de los
   ingresos; el Norte y el Nordeste compran menos pero con mayor ingreso promedio por ítem.
3. **Entregas por región (P3):** el tiempo de entrega depende sobre todo de la región; el incumplimiento de la fecha estimada
   es mayor en el Nordeste ({num(rg.loc['Nordeste', 'pct_entregas_tardias'], 2)} %) y en RJ.
4. **Entregas por categoría (P4):** la categoría influye menos que la región, salvo productos voluminosos como los muebles de oficina.
5. **Tendencia (P5):** el negocio creció entre 2017 y 2018 por mayor volumen de unidades, con un pico en noviembre de 2017.
""")

    st.subheader("Recomendaciones")
    st.markdown("""
- Priorizar campañas comerciales en las categorías del top 10 y en SP, RJ y MG, que concentran el volumen.
- Evaluar el crecimiento en el Norte y el Nordeste, donde cada ítem vale más, junto con mejoras logísticas en esas regiones.
- Revisar las fechas estimadas y el desempeño de las transportadoras en el Nordeste y en RJ, donde más se incumple.
- Preparar capacidad comercial y logística para los picos de demanda de fin de año.
- Incorporar datos de costos y márgenes antes de decidir por rentabilidad.
""")

    st.subheader("Limitaciones")
    st.markdown("""
- El análisis es **descriptivo**: muestra diferencias entre grupos pero no demuestra sus causas.
- **Ingresos no es rentabilidad:** no hay costos ni márgenes; los ingresos son el precio de venta sin flete ni descuentos.
- El tiempo de entrega solo se mide en ítems entregados con fecha, y por ítem (las órdenes grandes pesan más).
- Los grupos con pocos datos (estados del Norte, categorías con menos de 100 ítems, meses del inicio y el corte) son poco estables.
- La moneda se asume en BRL y los datos describen 2016-2018, no la situación actual.
""")
    st.info(f"Código, datos y documento del proyecto: [{REPOSITORIO}]({REPOSITORIO})")
