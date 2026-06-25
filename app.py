import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime
from io import StringIO

#====================================
# CONFIGURACIÓN
#====================================

st.set_page_config(
    page_title="Predicción Valor FOB Exportaciones",
    page_icon="🌎",
    layout="wide",
    initial_sidebar_state="expanded"
)

#====================================
# ESTILOS CSS
#====================================

st.markdown("""
<style>

html, body, [class*="css"]{
    font-family: 'Segoe UI';
    background:#F4F7FA;
}

/* HEADER */

.header{
background:linear-gradient(90deg,#0B3C5D,#145A32);
padding:25px;
border-radius:15px;
color:white;
margin-bottom:25px;
box-shadow:0px 5px 18px rgba(0,0,0,.20);
}

.header h1{
font-size:36px;
margin-bottom:5px;
color:white;
}

.header p{
font-size:18px;
color:#E8F6F3;
}

/* SIDEBAR */

section[data-testid="stSidebar"]{
background:#102A43;
}

section[data-testid="stSidebar"] label{
color:white;
font-weight:600;
}

section[data-testid="stSidebar"] h2{
color:white;
}

/* BOTÓN */

.stButton>button{

background:#0B5ED7;

color:white;

font-weight:700;

height:60px;

border-radius:10px;

font-size:20px;

border:none;

}

.stButton>button:hover{

background:#084298;

}

/* TARJETAS */

.card{

background:white;

padding:20px;

border-radius:15px;

box-shadow:0px 4px 14px rgba(0,0,0,.12);

margin-bottom:20px;

}

.card h4{

color:#6C757D;

margin-bottom:5px;

}

.valor{

font-size:42px;

font-weight:700;

color:#0B3C5D;

}

.subvalor{

font-size:18px;

color:#198754;

}

/* MÉTRICAS */

[data-testid="metric-container"]{

background:white;

padding:20px;

border-radius:15px;

box-shadow:0px 3px 12px rgba(0,0,0,.10);

}

/* FOOTER */

.footer{

text-align:center;

padding:20px;

color:gray;

font-size:14px;

}

</style>
""", unsafe_allow_html=True)

#====================================
# DATASET
#====================================

@st.cache_data
def cargar_datos():

    df = pd.read_csv("fecha_exportaciones_agricolas.csv")

    df["Fecha"] = pd.to_datetime(df["Fecha"])

    return df

df = cargar_datos()

#====================================
# CATÁLOGOS
#====================================

productos = sorted(df["Producto _(MADR_OAI)"].dropna().unique())

paises = sorted(df["Pais"].dropna().unique())

departamentos = sorted(df["Descripción Departamento"].dropna().unique())

#====================================
# DATAROBOT
#====================================

API_KEY = st.secrets["DATAROBOT_API_KEY"]

DEPLOYMENT_ID = st.secrets["DATAROBOT_DEPLOYMENT_ID"]

URL = f"https://app.datarobot.com/api/v2/deployments/{DEPLOYMENT_ID}/predictions"

HEADERS = {

"Authorization":f"Bearer {API_KEY}",

"Content-Type":"text/csv",

"Accept":"text/csv"

}

#====================================
# HEADER
#====================================

st.markdown("""

<div class="header">

<h1>🌎 Plataforma Inteligente de Predicción de Exportaciones Agrícolas</h1>

<p>

🚢 Comercio Exterior &nbsp;&nbsp;&nbsp;

📦 Exportaciones &nbsp;&nbsp;&nbsp;

🌱 Agroindustria Colombiana &nbsp;&nbsp;&nbsp;

📈 Inteligencia Artificial

</p>

</div>

""",unsafe_allow_html=True)
#====================================
# SIDEBAR
#====================================

st.sidebar.image(
    "https://img.icons8.com/fluency/96/wheat.png",
    width=80
)

st.sidebar.title("Parámetros")

st.sidebar.markdown(
"""
Configure las variables de entrada para realizar la predicción
del Valor FOB utilizando el modelo de Machine Learning desplegado
en DataRobot.
"""
)

#====================================
# FORMULARIO
#====================================

st.markdown("## 📋 Variables para la Predicción")

izquierda, derecha = st.columns([1,2], gap="large")

#============================
# PANEL IZQUIERDO
#============================

with izquierda:

    with st.container(border=True):

        st.subheader("🌱 Producto")

        producto = st.selectbox(
            "Producto",
            productos
        )

        tradicion = (
            df.loc[
                df["Producto _(MADR_OAI)"] == producto,
                "Tradición productos"
            ]
            .mode()
        )

        if len(tradicion):
            tradicion = tradicion.iloc[0]
        else:
            tradicion = "No disponible"

        st.text_input(
            "Tipo de bien",
            value=tradicion,
            disabled=True
        )

        st.write("")

        pais = st.selectbox(
            "🌍 País destino",
            paises
        )

        departamento = st.selectbox(
            "🏢 Departamento",
            departamentos
        )

        toneladas = st.number_input(
            "🚜 Toneladas exportadas",
            min_value=0.0,
            value=100.0,
            step=1.0,
            format="%.2f"
        )

#============================
# PANEL DERECHO
#============================

with derecha:

    with st.container(border=True):

        st.subheader("📅 Horizonte de Predicción")

        c1, c2 = st.columns(2)

        meses = [
            "Enero",
            "Febrero",
            "Marzo",
            "Abril",
            "Mayo",
            "Junio",
            "Julio",
            "Agosto",
            "Septiembre",
            "Octubre",
            "Noviembre",
            "Diciembre"
        ]

        with c1:

            mes = st.selectbox(
                "Mes",
                meses,
                index=datetime.today().month-1
            )

        with c2:

            año = st.selectbox(
                "Año",
                list(range(2025,2036)),
                index=1
            )

        numero_mes = meses.index(mes)+1

        fecha = datetime(
            año,
            numero_mes,
            1
        )

        st.divider()

        moneda = st.radio(
            "💰 Moneda de visualización",
            [
                "USD",
                "COP"
            ],
            horizontal=True
        )

        tasa_cambio = st.number_input(
            "TRM utilizada",
            min_value=3000.0,
            value=4100.0,
            step=10.0
        )

        st.info(
            "La predicción siempre se realiza en dólares FOB. "
            "Si selecciona COP, únicamente se convierte el resultado."
        )

#====================================
# BOTÓN
#====================================

st.write("")

b1, b2, b3 = st.columns([1,2,1])

with b2:

    generar = st.button(
        "📈 GENERAR PREDICCIÓN",
        use_container_width=True
    )

st.divider()
#====================================
# PREDICCIÓN CON DATAROBOT
#====================================

if generar:

    with st.spinner("Generando predicción..."):

        try:

            #-----------------------------
            # DataFrame exactamente igual
            # al utilizado para entrenar
            #-----------------------------

            input_df = pd.DataFrame([{

                "Descripción Departamento": departamento,

                "Pais": pais,

                "Ton Netas Expo": toneladas,

                "Producto _(MADR_OAI)": producto,

                "Tradición productos": tradicion,

                "Fecha": fecha.strftime("%Y-%m-%d")

            }])

            #-----------------------------
            # DataRobot recibe CSV
            #-----------------------------

            csv = input_df.to_csv(index=False)

            response = requests.post(

                URL,

                headers=HEADERS,

                data=csv.encode("utf-8")

            )

            if response.status_code != 200:

                st.error("Error recibido desde DataRobot")

                st.code(response.text)

                st.stop()

            #-----------------------------
            # Convierte respuesta CSV
            #-----------------------------

            resultado = pd.read_csv(

                StringIO(response.text)

            )

            #-----------------------------
            # Obtiene la primera columna
            # (predicción)
            #-----------------------------

            prediccion = float(

                resultado.iloc[0,0]

            )

            if moneda == "COP":

                valor = prediccion * tasa_cambio

                etiqueta = "Valor FOB Estimado (COP)"

                simbolo = "$"

            else:

                valor = prediccion

                etiqueta = "Valor FOB Estimado (USD)"

                simbolo = "US$"

            st.success("Predicción realizada correctamente.")

            st.write("")

            c1,c2,c3 = st.columns(3)

            with c1:

                st.metric(

                    "Producto",

                    producto

                )

            with c2:

                st.metric(

                    "Destino",

                    pais

                )

            with c3:

                st.metric(

                    "Toneladas",

                    f"{toneladas:,.2f}"

                )

            st.write("")

            st.markdown(f"""

            <div class="card">

            <h4>{etiqueta}</h4>

            <div class="valor">

            {simbolo} {valor:,.2f}

            </div>

            <div class="subvalor">

            Modelo de Machine Learning desplegado en DataRobot

            </div>

            </div>

            """,

            unsafe_allow_html=True)

            st.write("")

            a,b = st.columns(2)

            with a:

                st.metric(

                    "Mes",

                    mes

                )

            with b:

                st.metric(

                    "Tipo de bien",

                    tradicion

                )

        except Exception as e:

            st.error("No fue posible obtener la predicción.")

            st.exception(e)
            # =====================================================
# DASHBOARD ANALÍTICO
# =====================================================

st.markdown("## 📊 Dashboard Analítico")

#=========================================
# KPIs
#=========================================

k1, k2, k3, k4 = st.columns(4)

with k1:

    st.metric(
        "🌱 Productos",
        f"{len(productos):,}"
    )

with k2:

    st.metric(
        "🌍 Países",
        f"{len(paises):,}"
    )

with k3:

    st.metric(
        "🏢 Departamentos",
        f"{len(departamentos):,}"
    )

with k4:

    st.metric(
        "📦 Registros",
        f"{len(df):,}"
    )

st.write("")

#=========================================
# INDICADORES GENERALES
#=========================================

c1, c2 = st.columns(2)

with c1:

    toneladas_total = df["Ton Netas Expo"].sum()

    st.markdown(f"""
    <div class="card">
    <h4>🚜 Toneladas Exportadas</h4>
    <div class="valor">
    {toneladas_total:,.0f}
    </div>
    </div>
    """, unsafe_allow_html=True)

with c2:

    valor_total = df["Valor Miles FOB DOL"].sum()

    st.markdown(f"""
    <div class="card">
    <h4>💵 Valor Histórico FOB (Miles USD)</h4>
    <div class="valor">
    {valor_total:,.0f}
    </div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

#=========================================
# HISTÓRICO
#=========================================

st.subheader("📈 Evolución de las Exportaciones")

historico = (

    df.groupby("Fecha")

    [["Ton Netas Expo","Valor Miles FOB DOL"]]

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

    historico.set_index("Fecha")[["Valor Miles FOB DOL"]]

)

st.write("")

#=========================================
# PRODUCTOS Y DESTINOS
#=========================================

g1, g2 = st.columns(2)

with g1:

    st.subheader("📦 Top 10 Productos")

    top_productos = (

        df.groupby("Producto _(MADR_OAI)")

        ["Valor Miles FOB DOL"]

        .sum()

        .sort_values(ascending=False)

        .head(10)

    )

    st.bar_chart(top_productos)

with g2:

    st.subheader("🌍 Top 10 Países")

    top_paises = (

        df.groupby("Pais")

        ["Valor Miles FOB DOL"]

        .sum()

        .sort_values(ascending=False)

        .head(10)

    )

    st.bar_chart(top_paises)

st.write("")

#=========================================
# TRADICIONALES VS NO TRADICIONALES
#=========================================

st.subheader("🌱 Distribución por Tipo de Bien")

tradicional = (

    df.groupby("Tradición productos")

    ["Valor Miles FOB DOL"]

    .sum()

)

st.bar_chart(tradicional)

st.divider()

#=========================================
# INFORMACIÓN DEL MODELO
#=========================================

c1, c2, c3 = st.columns(3)

with c1:

    st.info(f"""
**Modelo**

Regresión

""")

with c2:

    st.info(f"""
**Objetivo**

Valor Miles FOB DOL

""")

with c3:

    st.info(f"""
**Motor**

DataRobot AI Platform

""")

st.write("")

#=========================================
# FOOTER
#=========================================

st.markdown("""

<div class="footer">

<hr>

<h4>

🌎 Plataforma Inteligente de Predicción de Exportaciones Agrícolas

</h4>

<p>

Desarrollado con

<b>Streamlit</b> |

<b>DataRobot AI</b> |

<b>Pandas</b>

</p>

<p>

Machine Learning aplicado al Comercio Exterior Colombiano

</p>

</div>

""",

unsafe_allow_html=True)
            
