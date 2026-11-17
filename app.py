"""
Dónde se gana y dónde se pierde plata: análisis de ventas, descuentos y rentabilidad.
Datos: Superstore (2014-2017). Herramientas: Python, pandas, Plotly, Streamlit.
"""
import io
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Análisis Superstore", layout="wide")

POS, NEG, NEU = "#1f6f78", "#c8472f", "#9aa5b4"
ARCHIVO = Path(__file__).parent / "superstore.csv"  # renombrá tu CSV con este nombre
MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]


def pesos(x):
    return f"${x:,.0f}".replace(",", ".")


@st.cache_data
def cargar(contenido: bytes) -> pd.DataFrame:
    df = pd.read_csv(io.BytesIO(contenido), encoding="latin-1")
    df["Order Date"] = pd.to_datetime(df["Order Date"])
    df["Año"] = df["Order Date"].dt.year
    df["Mes"] = df["Order Date"].dt.month
    df["Rango descuento"] = pd.cut(
        df["Discount"],
        bins=[-0.01, 0, 0.2, 0.4, 1],
        labels=["Sin descuento", "1-20%", "21-40%", "Más de 40%"],
    )
    return df


# ---------- Datos ----------
if ARCHIVO.exists():
    df_all = cargar(ARCHIVO.read_bytes())
else:
    subido = st.sidebar.file_uploader("Subí el CSV de Superstore", type="csv")
    if subido is None:
        st.info("Subí el archivo CSV de Superstore en la barra lateral para empezar.")
        st.stop()
    df_all = cargar(subido.getvalue())

# ---------- Filtros ----------
st.sidebar.header("Filtros")
anios = sorted(df_all["Año"].unique())
cats = sorted(df_all["Category"].unique())
regs = sorted(df_all["Region"].unique())
f_anio = st.sidebar.multiselect("Año", anios, default=anios)
f_cat = st.sidebar.multiselect("Categoría", cats, default=cats)
f_reg = st.sidebar.multiselect("Región", regs, default=regs)

df = df_all[
    df_all["Año"].isin(f_anio) & df_all["Category"].isin(f_cat) & df_all["Region"].isin(f_reg)
]
if df.empty:
    st.warning("No hay datos con los filtros elegidos.")
    st.stop()

# ---------- Encabezado y KPIs ----------
st.title("Dónde se gana y dónde se pierde plata")
st.caption(
    f"Análisis de {len(df):,} líneas de venta de una tienda minorista (2014-2017): "
    "rentabilidad por subcategoría, efecto de los descuentos, concentración de ventas y estacionalidad."
    .replace(",", ".")
)

ventas = df["Sales"].sum()
ganancia = df["Profit"].sum()
prod = df.groupby("Product Name")["Profit"].sum()
perdida = prod[prod < 0]

k1, k2, k3, k4 = st.columns(4)
k1.metric("Ventas totales", pesos(ventas))
k2.metric("Margen total", f"{ganancia / ventas * 100:.1f}%")
k3.metric("Productos con pérdida", f"{len(perdida)} de {len(prod)}")
k4.metric("Pérdida de esos productos", pesos(perdida.sum()))

st.divider()
izq, der = st.columns(2)

# ---------- 1. Subcategorías ----------
with izq:
    st.subheader("Qué subcategorías dejan ganancia y cuáles pierden")
    sub = (
        df.groupby("Sub-Category")[["Sales", "Profit"]].sum().sort_values("Profit").reset_index()
    )
    sub["Resultado"] = sub["Profit"].apply(lambda v: "Pérdida" if v < 0 else "Ganancia")
    fig = px.bar(
        sub, x="Profit", y="Sub-Category", orientation="h", color="Resultado",
        color_discrete_map={"Pérdida": NEG, "Ganancia": POS},
        labels={"Profit": "Beneficio ($)", "Sub-Category": ""},
    )
    fig.update_layout(showlegend=False, height=460, margin=dict(t=10))
    st.plotly_chart(fig, use_container_width=True)
    negativas = sub[sub["Profit"] < 0]["Sub-Category"].tolist()
    if negativas:
        st.caption("Subcategorías con pérdida en esta selección: " + ", ".join(negativas) + ".")

# ---------- 2. Descuentos ----------
with der:
    st.subheader("Efecto del descuento sobre el margen")
    d = df.groupby("Rango descuento", observed=True)[["Sales", "Profit"]].sum()
    d["Margen %"] = d["Profit"] / d["Sales"] * 100
    d = d.reset_index()
    d["Resultado"] = d["Margen %"].apply(lambda v: "Pérdida" if v < 0 else "Ganancia")
    fig = px.bar(
        d, x="Rango descuento", y="Margen %", color="Resultado",
        color_discrete_map={"Pérdida": NEG, "Ganancia": POS}, text="Margen %",
    )
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig.update_layout(showlegend=False, height=460, margin=dict(t=10), xaxis_title="")
    st.plotly_chart(fig, use_container_width=True)
    m = d.set_index("Rango descuento")["Margen %"]
    if "Sin descuento" in m.index and "Más de 40%" in m.index:
        st.caption(
            f"Sin descuento el margen es {m['Sin descuento']:.1f}%; "
            f"con más de 40% de descuento, {m['Más de 40%']:.1f}%."
        )

st.divider()
izq2, der2 = st.columns(2)

# ---------- 3. ABC ----------
with izq2:
    st.subheader("Concentración de ventas (análisis ABC)")
    abc = df.groupby("Product Name")["Sales"].sum().sort_values(ascending=False).to_frame()
    abc["acum"] = abc["Sales"].cumsum() / abc["Sales"].sum() * 100
    abc["Clase"] = pd.cut(abc["acum"], bins=[0, 80, 95, 100.01], labels=["A", "B", "C"])
    r = abc.groupby("Clase", observed=True).agg(n=("Sales", "count"), v=("Sales", "sum"))
    r["% de productos"] = r["n"] / len(abc) * 100
    r["% de ventas"] = r["v"] / abc["Sales"].sum() * 100
    r = r[["% de productos", "% de ventas"]].reset_index().melt(
        id_vars="Clase", var_name="Indicador", value_name="%"
    )
    fig = px.bar(
        r, x="Clase", y="%", color="Indicador", barmode="group", text="%",
        color_discrete_map={"% de productos": NEU, "% de ventas": POS},
    )
    fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    fig.update_layout(height=380, margin=dict(t=10), legend_title_text="")
    st.plotly_chart(fig, use_container_width=True)
    a = abc[abc["Clase"] == "A"]
    st.caption(
        f"{len(a)} productos ({len(a) / len(abc) * 100:.0f}% del catálogo) generan el 80% de las ventas."
    )

# ---------- 4. Estacionalidad ----------
with der2:
    st.subheader("Ventas promedio por mes del año")
    mes = df.groupby("Mes")["Sales"].sum() / df["Año"].nunique()
    mes = mes.reindex(range(1, 13), fill_value=0)
    top3 = mes.nlargest(3).index
    t = pd.DataFrame({
        "Mes": MESES, "Ventas": mes.values,
        "Destacado": ["Mayor venta" if i + 1 in top3 else "Resto" for i in range(12)],
    })
    fig = px.bar(
        t, x="Mes", y="Ventas", color="Destacado",
        color_discrete_map={"Mayor venta": POS, "Resto": NEU},
    )
    fig.update_layout(height=380, margin=dict(t=10), xaxis_title="", legend_title_text="")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Meses de mayor venta: " + ", ".join(MESES[i - 1] for i in sorted(top3)) + ".")

# ---------- Conclusiones ----------
st.divider()
st.subheader("Recomendaciones")
st.markdown(
    "- Poner un tope de **20%** a los descuentos: pasado ese nivel el margen se vuelve negativo.\n"
    "- **Tables, Bookcases y Supplies**: ganan sin descuento y pierden con descuento. Sin descuento en Tables y Supplies; tope de 20% en Bookcases.\n"
    "- Concentrar el control de stock y de proveedores en los **productos clase A**.\n"
    "- Reforzar stock **desde agosto** para los meses pico y comprar poco en enero y febrero."
)

with st.expander("Ver y descargar los datos filtrados"):
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.download_button(
        "Descargar CSV", df.to_csv(index=False).encode("utf-8"), "superstore_filtrado.csv", "text/csv"
    )

st.caption("Datos públicos de Superstore (Kaggle). Análisis descriptivo hecho en Python.")
