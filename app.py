import streamlit as st
import pandas as pd
import numpy as np
from datetime import date

# ==========================
# CONFIGURACIÓN DE PÁGINA
# ==========================

st.set_page_config(
    page_title="Modelo de Predicción Valor FOB Exportaciones Agrícolas Colombianas",
    page_icon="🌎",
    layout="wide"
)

# ==========================
# ESTILOS
# ==========================

st.markdown("""
<style>

.main {
    background-color: #F5F7FA;
}

h1 {
    color: #0F4C81;
}

h2, h3 {
    color: #2E7D32;
}

.block-container {
    padding-top: 1rem;
}

.metric-card {
    background-color: white;
    padding: 20px;
    border-radius: 12px;
    border-left: 5px solid #0F4C81;
}

.stButton > button {
    background-color: #0F4C81;
    color: white;
    border-radius: 10px;
    font-size: 18px;
    font-weight: bold;
    height: 3.5em;
    width: 100%;
}

.stButton > button:hover {
    background-color: #0A365A;
    color: white;
}

.readonly-box {
    padding: 10px;
    border-radius: 8px;
    background-color: #F1F5F9;
    border: 1px solid #D1D5DB;
}

</style>
""", unsafe_allow_html=True)

# ==========================
# CARGAR DATASET
# ==========================

@st.cache_data
def cargar_datos():
    return pd.read_csv("fecha_exportaciones_agricolas.csv")

df = cargar_datos()

# ==========================
# CATÁLOGOS DINÁMICOS
# ==========================

productos = sorted(
    df["Producto _(MADR_OAI)"]
    .dropna()
    .astype(str)
    .unique()
)

paises = sorted(
    df["Pais"]
    .dropna()
    .astype(str)
    .unique()
)

departamentos = sorted(
    df["Descripción Departamento"]
    .dropna()
    .astype(str)
    .unique()
)

# ==========================
# CONEXIÓN DATAROBOT
# ==========================

API_KEY = st.secrets["DATAROBOT_API_KEY"]
DEPLOYMENT_ID = st.secrets["DATAROBOT_DEPLOYMENT_ID"]
ENDPOINT = st.secrets["DATAROBOT_ENDPOINT"]


# ==========================
# ENCABEZADO
# ==========================

st.title("🌱 Predicción Inteligente de Exportaciones Agrícolas")

st.markdown("""
Sistema de análisis predictivo para estimar el **Valor FOB Exportado**
utilizando inteligencia artificial y modelos de Machine Learning desarrollados en DataRobot.

🌍 Comercio Exterior | 🚢 Exportaciones | 📦 Logística | 📈 Analítica Predictiva
""")

st.divider()

# ==========================
# FORMULARIO
# ==========================

col1, col2 = st.columns(2)

with col1:

    producto = st.selectbox(
        "📦 Producto",
        productos
    )

    pais = st.selectbox(
        "🌍 País destino",
        paises
    )

    departamento = st.selectbox(
        "🏢 Departamento",
        departamentos
    )

with col2:

    toneladas = st.number_input(
        "🚚 Toneladas Netas Exportadas",
        min_value=0.0,
        value=100.0,
        step=1.0
    )

    fecha = st.date_input(
        "📅 Fecha estimada",
        value=date.today()
    )

# ==========================
# TRADICIÓN AUTOMÁTICA
# ==========================

tradicion = (
    df.loc[
        df["Producto _(MADR_OAI)"] == producto,
        "Tradición productos"
    ]
    .mode()
)

if len(tradicion) > 0:
    tradicion = tradicion.iloc[0]
else:
    tradicion = "No disponible"

st.markdown("### Tipo de Bien")

st.text_input(
    "",
    value=tradicion,
    disabled=True
)

# ==========================
# BOTÓN CENTRADO
# ==========================

st.write("")

c1, c2, c3 = st.columns([1,2,1])

with c2:
    generar = st.button(
        "📈 Generar Predicción",
        use_container_width=True
    )

import requests
import io

# ==========================
# PREDICCIÓN
# ==========================

if generar:

    try:

        input_df = pd.DataFrame([{
            "Descripción Departamento": departamento,
            "Pais": pais,
            "Ton Netas Expo": toneladas,
            "Producto _(MADR_OAI)": producto,
            "Tradición productos": tradicion,
            "Fecha": fecha.strftime("%Y-%m-%d")
        }])

        csv_data = input_df.to_csv(
            index=False
        )

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "text/csv; charset=UTF-8",
            "Accept": "text/csv"
        }

        response = requests.post(
            f"{ENDPOINT}/api/v2/deployments/{DEPLOYMENT_ID}/predictions",
            headers=headers,
            data=csv_data.encode("utf-8"),
            timeout=120
        )

        response.raise_for_status()

        resultado_df = pd.read_csv(
            io.StringIO(response.text)
        )

        columnas_numericas = resultado_df.select_dtypes(
            include=["number"]
        ).columns

        if len(columnas_numericas) == 0:
            raise Exception(
                "No se encontró ninguna columna numérica en la respuesta de DataRobot"
            )

        prediccion = float(
            resultado_df[columnas_numericas[0]].iloc[0]
        )

        st.success(
            "Predicción generada exitosamente"
        )

        st.markdown("## 📈 Resultado")

        st.metric(
            label="Valor FOB Estimado",
            value=f"USD {prediccion:,.2f}"
        )

        with st.expander("Ver respuesta completa de DataRobot"):
            st.dataframe(resultado_df)

    except Exception as e:

        st.error(
            f"Error al consultar DataRobot: {e}"
        )
# ==========================
# HISTÓRICOS
# ==========================

st.divider()

st.subheader("📊 Histórico de Exportaciones")

historico = (
    df.groupby("Fecha")["Ton Netas Expo"]
    .sum()
    .reset_index()
)

historico["Fecha"] = pd.to_datetime(
    historico["Fecha"]
)

historico = historico.sort_values(
    "Fecha"
)

st.line_chart(
    historico.set_index("Fecha")
)

# ==========================
# TOP PRODUCTOS
# ==========================

st.subheader("📦 Top 10 Productos Exportados")

top_productos = (
    df.groupby("Producto _(MADR_OAI)")["Ton Netas Expo"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

st.bar_chart(top_productos)

# ==========================
# KPIs
# ==========================

st.divider()

k1, k2, k3 = st.columns(3)

with k1:
    st.metric(
        "Productos",
        len(productos)
    )

with k2:
    st.metric(
        "Países Destino",
        len(paises)
    )

with k3:
    st.metric(
        "Registros",
        f"{len(df):,}"
    )

st.caption(
    "Modelo desplegado en DataRobot | Machine Learning para Comercio Exterior y Exportaciones Agrícolas"
)
