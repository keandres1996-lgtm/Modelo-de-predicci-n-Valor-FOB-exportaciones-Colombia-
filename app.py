import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import date

# =====================================================
# CONFIGURACIÓN DE LA PÁGINA
# =====================================================

st.set_page_config(
    page_title="Predicción Inteligente de Exportaciones Agrícolas",
    page_icon="🌎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# PALETA CORPORATIVA
# =====================================================

st.markdown("""
<style>

html, body, [class*="css"] {
    font-family: 'Segoe UI', sans-serif;
}

.main{
    background:#F3F6FA;
}

.block-container{
    padding-top:1rem;
    padding-bottom:1rem;
    padding-left:2rem;
    padding-right:2rem;
}

h1{
    color:#0F4C81;
    font-weight:700;
}

h2,h3{
    color:#1B5E20;
}

section[data-testid="stSidebar"]{
    background:#0F2D52;
}

section[data-testid="stSidebar"] *{
    color:white;
}

.stButton>button{
    width:100%;
    height:55px;
    border-radius:12px;
    border:none;
    background:#0F4C81;
    color:white;
    font-size:18px;
    font-weight:bold;
}

.stButton>button:hover{
    background:#1565C0;
    color:white;
}

div[data-testid="metric-container"]{

    background:white;

    border-radius:15px;

    padding:20px;

    border-left:8px solid #2E7D32;

    box-shadow:0px 3px 12px rgba(0,0,0,.08);

}

div[data-testid="stSelectbox"]{

    background:white;

    border-radius:10px;

}

div[data-testid="stNumberInput"]{

    background:white;

    border-radius:10px;

}

div[data-testid="stDateInput"]{

    background:white;

    border-radius:10px;

}

.footer{

    text-align:center;

    color:gray;

    margin-top:40px;

}

</style>
""", unsafe_allow_html=True)

# =====================================================
# CARGAR BASE
# =====================================================

@st.cache_data
def cargar_datos():

    df = pd.read_csv("fecha_exportaciones_agricolas.csv")

    df["Fecha"] = pd.to_datetime(df["Fecha"])

    return df

df = cargar_datos()

# =====================================================
# CATÁLOGOS
# =====================================================

productos = sorted(
    df["Producto _(MADR_OAI)"]
    .dropna()
    .unique()
)

paises = sorted(
    df["Pais"]
    .dropna()
    .unique()
)

departamentos = sorted(
    df["Descripción Departamento"]
    .dropna()
    .unique()
)

# =====================================================
# CONFIGURACIÓN DATAROBOT
# =====================================================

API_KEY = st.secrets["DATAROBOT_API_KEY"]

DEPLOYMENT_ID = st.secrets["DATAROBOT_DEPLOYMENT_ID"]

URL_PREDICCION = (
    f"https://app.datarobot.com/api/v2/deployments/"
    f"{DEPLOYMENT_ID}/predictions"
)

HEADERS = {

    "Authorization": f"Bearer {API_KEY}",

    "Content-Type":"text/csv; charset=UTF-8",

    "Accept":"text/csv"

}

# =====================================================
# ENCABEZADO
# =====================================================

st.title("🌎 Predicción Inteligente de Exportaciones Agrícolas Colombianas")

st.markdown("""

Sistema desarrollado mediante **Machine Learning** para estimar el

**Valor FOB de las exportaciones agrícolas colombianas**.

---

**Sectores incluidos**

🌱 Agroindustria

🚜 Producción agrícola

🚢 Comercio exterior

📦 Exportaciones

📈 Analítica predictiva

""")

st.divider()
# =====================================================
# PANEL LATERAL
# =====================================================

with st.sidebar:

    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/59/Empty.png/1px-Empty.png",
        width=1
    )

    st.markdown("## ⚙️ Parámetros de Predicción")

    producto = st.selectbox(
        "🌱 Producto",
        productos
    )

    pais = st.selectbox(
        "🌍 País destino",
        paises
    )

    departamento = st.selectbox(
        "🏢 Departamento origen",
        departamentos
    )

    toneladas = st.number_input(
        "🚚 Toneladas Netas Exportadas",
        min_value=0.0,
        value=100.0,
        step=1.0
    )

    col_mes, col_anio = st.columns(2)

    with col_mes:

        mes = st.selectbox(
            "Mes",
            list(range(1,13)),
            index=date.today().month-1
        )

    with col_anio:

        anio = st.selectbox(
            "Año",
            list(range(2026,2036)),
            index=0
        )

    moneda = st.radio(
        "💰 Mostrar resultado en",
        [
            "USD",
            "COP"
        ],
        horizontal=True
    )

# =====================================================
# OBTENER INFORMACIÓN DEL PRODUCTO
# =====================================================

registro = df[
    df["Producto _(MADR_OAI)"] == producto
]

# Tipo de bien

if "Tradición productos" in df.columns:

    tradicion = registro["Tradición productos"].mode()

    if len(tradicion):

        tradicion = tradicion.iloc[0]

    else:

        tradicion = "No disponible"

else:

    tradicion = "No disponible"

# Partida Arancelaria

nombre_partida = None

for columna in df.columns:

    texto = columna.lower()

    if (
        "partida" in texto
        or "arancel" in texto
        or "subpartida" in texto
        or "nandina" in texto
    ):

        nombre_partida = columna

        break

if nombre_partida:

    partida = registro[nombre_partida].mode()

    if len(partida):

        partida = partida.iloc[0]

    else:

        partida = "No disponible"

else:

    partida = "No disponible"

# Fecha que enviará al modelo

fecha_prediccion = pd.Timestamp(
    year=anio,
    month=mes,
    day=1
)

# =====================================================
# TARJETAS INFORMATIVAS
# =====================================================

st.subheader("📋 Información del Producto")

c1, c2 = st.columns(2)

with c1:

    st.metric(
        "🏷️ Tipo de Bien",
        tradicion
    )

with c2:

    st.metric(
        "📦 Partida Arancelaria",
        str(partida)
    )

st.divider()

# =====================================================
# BOTÓN DE PREDICCIÓN
# =====================================================

col1, col2, col3 = st.columns([1,2,1])

with col2:

    generar = st.button(
        "📈 GENERAR PREDICCIÓN",
        use_container_width=True
    )
    # =====================================================
# PREDICCIÓN CON DATAROBOT
# =====================================================

if generar:

    try:

        # -----------------------------
        # Construir registro
        # -----------------------------

        input_df = pd.DataFrame([{

            "Fecha": fecha_prediccion.strftime("%Y-%m-%d"),

            "Producto _(MADR_OAI)": producto,

            "Pais": pais,

            "Descripción Departamento": departamento,

            "Ton Netas Expo": toneladas,

            "Tradición productos": tradicion

        }])

        # -----------------------------
        # Convertir a CSV
        # -----------------------------

        csv_data = input_df.to_csv(
            index=False
        )

        # -----------------------------
        # Consumir API DataRobot
        # -----------------------------

        response = requests.post(

            URL_PREDICCION,

            headers=HEADERS,

            data=csv_data.encode("utf-8")

        )

        if response.status_code != 200:

            st.error("DataRobot respondió:")

            st.code(response.text)

            st.stop()

        # -----------------------------
        # Leer respuesta CSV
        # -----------------------------

        resultado = pd.read_csv(

            pd.io.common.StringIO(
                response.text
            )

        )

        # ------------------------------------
        # Encontrar automáticamente la columna
        # de predicción
        # ------------------------------------

        prediccion = None

        posibles = [

            "prediction",

            "Prediction",

            "Predicted_Value",

            "prediction_value",

            "Predicted",

            "Value"

        ]

        for columna in posibles:

            if columna in resultado.columns:

                prediccion = float(

                    resultado[columna].iloc[0]

                )

                break

        if prediccion is None:

            columnas_numericas = resultado.select_dtypes(
                include="number"
            ).columns

            prediccion = float(
                resultado[columnas_numericas[0]].iloc[0]
            )

        # ------------------------------------
        # Conversión a COP
        # ------------------------------------

        TRM = 4100

        valor_cop = prediccion * TRM

        # ------------------------------------
        # RESULTADOS
        # ------------------------------------

        st.success(
            "Predicción generada correctamente."
        )

        st.subheader("📈 Resultado de la Predicción")

        c1, c2 = st.columns(2)

        with c1:

            st.metric(

                "💵 Valor FOB (USD)",

                f"USD {prediccion:,.2f}"

            )

        with c2:

            st.metric(

                "🇨🇴 Valor FOB (COP)",

                f"$ {valor_cop:,.0f}"

            )

        st.divider()

        st.subheader("📄 Registro enviado al modelo")

        st.dataframe(
            input_df,
            use_container_width=True
        )

        st.subheader("🤖 Respuesta completa del modelo")

        st.dataframe(
            resultado,
            use_container_width=True
        )

    except Exception as e:

        st.error(e)
    
# =====================================================
# BOTÓN PREDICCIÓN
# =====================================================

st.markdown("<br>", unsafe_allow_html=True)

col_btn1, col_btn2, col_btn3 = st.columns([1,2,1])

with col_btn2:
    generar = st.button(
        "🚀 Generar Predicción",
        use_container_width=True
    )

# =====================================================
# PREDICCIÓN DATAROBOT
# =====================================================

if generar:

    try:

        fecha_pred = f"{anio}-{mes:02d}-01"

        input_df = pd.DataFrame([{
            "Producto _(MADR_OAI)": producto,
            "Pais": pais,
            "Descripción Departamento": departamento,
            "Ton Netas Expo": toneladas,
            "Tradición productos": tradicion,
            "Fecha": fecha_pred
        }])

        csv_data = input_df.to_csv(index=False)

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "text/csv; charset=UTF-8",
            "Accept": "text/csv"
        }

        url = f"{ENDPOINT}/api/v2/deployments/{DEPLOYMENT_ID}/predictions"

        response = requests.post(
            url,
            headers=headers,
            data=csv_data.encode("utf-8"),
            timeout=60
        )

        if response.status_code != 200:
            st.error(response.text)
            st.stop()

        resultado = pd.read_csv(io.StringIO(response.text))

        prediccion = float(resultado.iloc[0,0])

        TRM = 4100

        col1,col2 = st.columns(2)

        with col1:

            st.markdown("""
            <div class="card">
            <h3>🌍 Valor FOB Estimado</h3>
            </div>
            """,unsafe_allow_html=True)

            st.metric(
                "USD",
                f"${prediccion:,.2f}"
            )

        with col2:

            st.markdown("""
            <div class="card">
            <h3>💰 Equivalente COP</h3>
            </div>
            """,unsafe_allow_html=True)

            st.metric(
                "COP",
                f"${prediccion*TRM:,.0f}"
            )

    except Exception as e:

        st.error(e)

# =====================================================
# DASHBOARD
# =====================================================

st.divider()

st.subheader("📈 Histórico de Toneladas Exportadas")

historico = (
    df.groupby("Fecha")["Ton Netas Expo"]
      .sum()
      .reset_index()
)

historico["Fecha"] = pd.to_datetime(historico["Fecha"])

historico = historico.sort_values("Fecha")

st.line_chart(
    historico.set_index("Fecha")
)

# =====================================================
# TOP PRODUCTOS
# =====================================================

st.subheader("📦 Top 10 Productos")

top = (
    df.groupby("Producto _(MADR_OAI)")["Ton Netas Expo"]
      .sum()
      .sort_values(ascending=False)
      .head(10)
)

st.bar_chart(top)

# =====================================================
# TOP PAÍSES
# =====================================================

st.subheader("🌎 Top Países Destino")

top_paises = (
    df.groupby("Pais")["Ton Netas Expo"]
      .sum()
      .sort_values(ascending=False)
      .head(10)
)

st.bar_chart(top_paises)

# =====================================================
# KPIs
# =====================================================

st.divider()

valor_total = df["Miles FOB Dol Expo"].sum()

ton_total = df["Ton Netas Expo"].sum()

k1,k2,k3,k4 = st.columns(4)

k1.metric(
    "🌱 Productos",
    len(productos)
)

k2.metric(
    "🌍 Países",
    len(paises)
)

k3.metric(
    "🚚 Toneladas",
    f"{ton_total:,.0f}"
)

k4.metric(
    "💵 FOB Histórico",
    f"USD {valor_total:,.0f}"
)

st.divider()

st.caption(
    "Modelo de Inteligencia Artificial • DataRobot • Exportaciones Agrícolas Colombianas"
)
