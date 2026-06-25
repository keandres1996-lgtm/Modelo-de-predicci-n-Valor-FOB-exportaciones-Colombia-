import streamlit as st
import pandas as pd
import numpy as np
import requests
import json
import io
import time
from datetime import datetime

# ══════════════════════════════════════════════════════════════
# CONFIGURACIÓN DE PÁGINA
# ══════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Predicción FOB · Exportaciones Agrícolas Colombia",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════
# CREDENCIALES
# ══════════════════════════════════════════════════════════════

API_KEY       = st.secrets["DATAROBOT_API_KEY"]
DEPLOYMENT_ID = st.secrets["DATAROBOT_DEPLOYMENT_ID"]
DR_HOST       = st.secrets.get("DATAROBOT_ENDPOINT", "https://app.datarobot.com")

HEADERS_JSON = {
    "Authorization": f"Token {API_KEY}",
    "Content-Type":  "application/json; encoding=utf-8",
}
HEADERS_CSV = {
    "Authorization": f"Token {API_KEY}",
    "Content-Type":  "text/csv; encoding=utf-8",
}

BATCH_URL     = f"{DR_HOST}/api/v2/batchPredictions/"
POLL_INTERVAL = 5
TIMEOUT       = 300

# ══════════════════════════════════════════════════════════════
# DATOS Y CATÁLOGOS DINÁMICOS
# ══════════════════════════════════════════════════════════════

DATA_PATH = "fecha_exportaciones_agricolas.csv"

@st.cache_data
def cargar_datos():
    df = pd.read_csv(DATA_PATH)
    df["Fecha"] = pd.to_datetime(df["Fecha"])
    return df

df = cargar_datos()

productos     = sorted(df["Producto _(MADR_OAI)"].dropna().astype(str).unique())
paises        = sorted(df["Pais"].dropna().astype(str).unique())
departamentos = sorted(df["Descripción Departamento"].dropna().astype(str).unique())
meses_es      = ["Enero","Febrero","Marzo","Abril","Mayo","Junio",
                 "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]
meses_num     = {m: i+1 for i, m in enumerate(meses_es)}

# Tasa de cambio aproximada (actualizable)
TRM_DEFAULT = 4_150.0

# ══════════════════════════════════════════════════════════════
# ESTILOS CORPORATIVOS
# ══════════════════════════════════════════════════════════════

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
}

/* ── Fondo principal ── */
.main { background-color: #F0F4F8; }
.block-container { padding-top: 0.5rem !important; max-width: 1280px; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0B1F3A 0%, #0F2D4A 60%, #0D2137 100%);
    border-right: 1px solid #1A3A5C;
    min-width: 300px !important;
}
[data-testid="stSidebar"] * { color: #CBD9E8 !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stNumberInput label,
[data-testid="stSidebar"] .stMultiSelect label,
[data-testid="stSidebar"] .stSlider label {
    color: #7AAECF !important;
    font-size: 0.73rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
}
[data-testid="stSidebar"] h2 {
    color: #4DA6E0 !important;
    font-size: 0.78rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    border-bottom: 1px solid #1E4A6E !important;
    padding-bottom: 5px !important;
    margin-top: 1.1rem !important;
}
[data-testid="stSidebar"] .stSelectbox > div > div,
[data-testid="stSidebar"] .stNumberInput input,
[data-testid="stSidebar"] .stMultiSelect > div > div {
    background: #091828 !important;
    border: 1px solid #1E4A6E !important;
    color: #DDE8F2 !important;
    border-radius: 7px !important;
    font-size: 0.85rem !important;
}

/* ── Header app ── */
.app-header {
    background: linear-gradient(135deg, #0B1F3A 0%, #0F3460 55%, #1A527A 100%);
    border-radius: 12px;
    padding: 1.4rem 2rem 1.2rem;
    margin-bottom: 1.2rem;
    border-left: 4px solid #2E86C1;
    box-shadow: 0 4px 16px rgba(11,31,58,0.35);
    display: flex;
    align-items: center;
    gap: 1rem;
}
.app-header-text h1 {
    color: #FFFFFF !important;
    font-size: 1.55rem !important;
    font-weight: 700 !important;
    margin: 0 0 0.2rem 0 !important;
    line-height: 1.2 !important;
}
.app-header-text p {
    color: #88BEDD !important;
    font-size: 0.82rem !important;
    margin: 0 !important;
    line-height: 1.5 !important;
}

/* ── KPI cards grandes ── */
.kpi-card {
    background: linear-gradient(145deg, #FFFFFF 0%, #F7FAFD 100%);
    border: 1px solid #D4E4F0;
    border-top: 4px solid #2E86C1;
    border-radius: 12px;
    padding: 1.4rem 1.6rem 1.2rem;
    text-align: center;
    box-shadow: 0 2px 12px rgba(46,134,193,0.10);
    transition: transform 0.18s, box-shadow 0.18s;
    height: 100%;
}
.kpi-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 20px rgba(46,134,193,0.18);
}
.kpi-card.green { border-top-color: #2E7D32; }
.kpi-card.amber  { border-top-color: #E65100; }
.kpi-card.teal   { border-top-color: #00695C; }
.kpi-icon  { font-size: 1.6rem; margin-bottom: 6px; line-height: 1; }
.kpi-label {
    color: #5A7A95;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 600;
    margin-bottom: 6px;
}
.kpi-value {
    color: #0B1F3A;
    font-size: 2rem;
    font-weight: 800;
    line-height: 1;
    margin-bottom: 4px;
}
.kpi-value.big { font-size: 1.7rem; }
.kpi-sub {
    color: #2E86C1;
    font-size: 0.77rem;
    font-weight: 500;
}
.kpi-cop {
    color: #2E7D32;
    font-size: 0.85rem;
    font-weight: 600;
    margin-top: 5px;
    padding: 3px 8px;
    background: #E8F5E9;
    border-radius: 20px;
    display: inline-block;
}

/* ── Badge tradición ── */
.badge-trad {
    display: inline-block;
    background: #E8F5E9;
    color: #2E7D32;
    border: 1px solid #A5D6A7;
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.76rem;
    font-weight: 700;
}
.badge-notrad {
    display: inline-block;
    background: #E3F2FD;
    color: #1565C0;
    border: 1px solid #90CAF9;
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.76rem;
    font-weight: 700;
}

/* ── Campo readonly ── */
.ro-box {
    background: #0B1F3A;
    border: 1px solid #1E4A6E;
    border-radius: 8px;
    padding: 0.55rem 0.85rem;
    margin-bottom: 0.7rem;
}
.ro-label {
    color: #4A8FB5;
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    font-weight: 600;
    margin-bottom: 3px;
}
.ro-value { color: #C8DEF0; font-size: 0.87rem; font-weight: 500; }

/* ── Botón predicción ── */
div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #1A5276 0%, #2E86C1 100%) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 9px !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    letter-spacing: 0.05em !important;
    padding: 0.75rem 2rem !important;
    box-shadow: 0 4px 16px rgba(46,134,193,0.45) !important;
    transition: all 0.2s !important;
    width: 100% !important;
    text-transform: uppercase !important;
}
div[data-testid="stButton"] > button:hover {
    background: linear-gradient(135deg, #21618C 0%, #3498DB 100%) !important;
    box-shadow: 0 7px 20px rgba(46,134,193,0.6) !important;
    transform: translateY(-1px) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #E8F0F7;
    border-radius: 10px 10px 0 0;
    padding: 4px 8px 0;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    color: #5A7A95 !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    border-radius: 6px 6px 0 0 !important;
}
.stTabs [aria-selected="true"] {
    color: #1A5276 !important;
    background: white !important;
    border-bottom: 3px solid #2E86C1 !important;
}

/* ── Sección de resultados ── */
.results-header {
    background: linear-gradient(90deg, #0F3460 0%, #1A5276 100%);
    border-radius: 10px;
    padding: 0.9rem 1.4rem;
    margin: 0.5rem 0 1.2rem;
    color: #FFFFFF;
    font-size: 1rem;
    font-weight: 700;
    letter-spacing: 0.03em;
}

/* ── TRM converter ── */
.trm-box {
    background: linear-gradient(135deg, #1B5E20 0%, #2E7D32 100%);
    border-radius: 10px;
    padding: 1rem 1.4rem;
    margin-bottom: 1rem;
    color: white;
    font-size: 0.88rem;
}

/* ── Footer ── */
.footer {
    background: #0B1F3A;
    border-radius: 8px;
    padding: 0.7rem 1.5rem;
    text-align: center;
    color: #3A6A8A;
    font-size: 0.76rem;
    margin-top: 1.5rem;
}

hr { border-color: #C8D8E8 !important; }

@media (max-width: 640px) {
    .app-header h1 { font-size: 1.1rem !important; }
    .kpi-value { font-size: 1.4rem !important; }
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# BATCH PREDICTION API
# ══════════════════════════════════════════════════════════════

class DRError(Exception):
    pass

def _dr_post(url, payload):
    r = requests.post(url, headers=HEADERS_JSON,
                      data=json.dumps(payload).encode(), timeout=TIMEOUT)
    if not r.ok:
        raise DRError(f"{r.status_code}: {r.text}")
    return r.json()

def _dr_get(url):
    r = requests.get(url, headers=HEADERS_JSON, timeout=TIMEOUT)
    if not r.ok:
        raise DRError(f"{r.status_code}: {r.text}")
    return r.json()

def _poll(job_url, status_box):
    deadline = time.time() + TIMEOUT
    while time.time() < deadline:
        job = _dr_get(job_url)
        st = job.get("status", "")
        pct = round(float(job.get("percentageCompleted", 0)))
        if st == "INITIALIZING":
            status_box.info("⏳ Iniciando modelo en DataRobot…")
        elif st == "RUNNING":
            status_box.info(f"⚙️ Procesando… {pct}%")
        elif st == "COMPLETED":
            return job
        elif st in ("ABORTED", "FAILED"):
            raise DRError(f"Trabajo fallido: {job.get('statusDetails','')}")
        time.sleep(POLL_INTERVAL)
    raise DRError("Tiempo de espera agotado.")

def batch_predict(csv_bytes, status_box):
    job = _dr_post(BATCH_URL, {"deploymentId": DEPLOYMENT_ID})
    upload_url = job["links"]["csvUpload"]
    status_box.info("📤 Subiendo datos al modelo…")
    h = {**HEADERS_CSV, "Content-length": str(len(csv_bytes))}
    requests.put(upload_url, headers=h, data=csv_bytes, timeout=TIMEOUT)
    done = _poll(job["links"]["self"], status_box)
    dl_url = done["links"]["download"]
    r = requests.get(dl_url, headers=HEADERS_JSON, timeout=TIMEOUT)
    r.raise_for_status()
    return pd.read_csv(io.StringIO(r.text))

# ══════════════════════════════════════════════════════════════
# CONSTRUCCIÓN CSV DE ENTRADA
# ══════════════════════════════════════════════════════════════

def build_input_df(rows):
    records = []
    for r in rows:
        mn = r["mes_num"]
        records.append({
            "Descripción Departamento": r["departamento"],
            "Pais":                     r["pais"],
            "Ton Netas Expo":           r["toneladas"],
            "Producto _(MADR_OAI)":     r["producto"],
            "Tradición productos":      r["tradicion"],
            "Fecha":                    f"{r['anio']}-{mn:02d}-01",
        })
    return pd.DataFrame(records)

# ══════════════════════════════════════════════════════════════
# HEADER PRINCIPAL
# ══════════════════════════════════════════════════════════════

st.markdown(f"""
<div class="app-header">
  <div style="font-size:3rem;line-height:1">🌱</div>
  <div class="app-header-text">
    <h1>Predicción FOB — Exportaciones Agrícolas Colombia</h1>
    <p>
      🚢 Comercio Exterior &nbsp;|&nbsp; 📦 Logística Agro &nbsp;|&nbsp;
      📈 Machine Learning · DataRobot &nbsp;|&nbsp;
      {datetime.now().strftime('%d/%m/%Y %H:%M')}
    </p>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# SIDEBAR — PANEL DE CONFIGURACIÓN
# ══════════════════════════════════════════════════════════════

with st.sidebar:

    st.markdown("## 📦 Producto")
    producto = st.selectbox("Producto agrícola", productos, key="prod")

    # Auto-completado tradición
    tradicion = (
        df.loc[df["Producto _(MADR_OAI)"] == producto, "Tradición productos"]
        .mode()
    )
    tradicion = tradicion.iloc[0] if len(tradicion) > 0 else "No disponible"
    badge = ("badge-trad" if tradicion == "Tradicional" else "badge-notrad")

    st.markdown(f"""
    <div class="ro-box">
      <div class="ro-label">🏷️ Tipo de Bien</div>
      <div class="ro-value"><span class="{badge}">{tradicion}</span></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("## 🌍 Origen y Destino")
    departamento = st.selectbox("Departamento exportador", departamentos)
    pais         = st.selectbox("País de destino", paises)

    st.markdown("## ⚖️ Volumen")
    toneladas = st.number_input(
        "Toneladas netas a exportar",
        min_value=0.0, max_value=500_000.0,
        value=100.0, step=10.0,
    )

    st.markdown("## 📅 Período (múltiple)")
    anio = st.number_input("Año", 2024, 2035, 2026)
    meses_sel = st.multiselect(
        "Meses a predecir",
        meses_es,
        default=["Enero", "Febrero", "Marzo"],
        help="Seleccione uno o varios meses",
    )

    st.markdown("## 💱 Conversión a COP")
    usar_cop = st.toggle("Mostrar también en pesos colombianos", value=True)
    if usar_cop:
        trm = st.number_input(
            "TRM (COP por 1 USD)",
            min_value=1_000.0, max_value=10_000.0,
            value=TRM_DEFAULT, step=50.0,
            help="Tasa Representativa del Mercado vigente",
        )
    else:
        trm = TRM_DEFAULT

    st.markdown("---")
    predecir = st.button("🔍  Generar Predicción", use_container_width=True)

# ══════════════════════════════════════════════════════════════
# PANEL CENTRAL — Estado previo a la predicción
# ══════════════════════════════════════════════════════════════

if not predecir:
    col_params, col_hist = st.columns([2, 3])

    with col_params:
        st.markdown("#### 📌 Parámetros seleccionados")
        items = {
            "🌱 Producto":    producto,
            "🏷️ Tipo bien":   tradicion,
            "🗺️ Departamento": departamento,
            "🌍 País destino": pais,
            "⚖️ Toneladas":   f"{toneladas:,.1f} t",
            "📅 Año":         str(anio),
            "🗓️ Meses":       ", ".join(meses_sel) if meses_sel else "—",
        }
        for k, v in items.items():
            st.markdown(
                f"<div style='display:flex;justify-content:space-between;"
                f"padding:5px 0;border-bottom:1px solid #CBD5E1;font-size:0.84rem'>"
                f"<span style='color:#5A7A95'>{k}</span>"
                f"<span style='color:#0B1F3A;font-weight:600'>{v}</span></div>",
                unsafe_allow_html=True,
            )

    with col_hist:
        st.markdown("#### 📊 Histórico exportaciones (toneladas)")
        hist = (
            df.groupby("Fecha")["Ton Netas Expo"]
            .sum()
            .reset_index()
            .sort_values("Fecha")
            .set_index("Fecha")
        )
        st.line_chart(hist, color="#2E86C1")

    st.divider()

    # KPIs exploratorios del dataset
    st.markdown("#### 🔍 Resumen del dataset de referencia")
    k1, k2, k3, k4 = st.columns(4)
    kpis = [
        ("🌱", "Productos", str(len(productos)), "distintos"),
        ("🌍", "Países destino", str(len(paises)), "mercados"),
        ("🗺️", "Departamentos", str(len(departamentos)), "regiones"),
        ("📋", "Registros", f"{len(df):,}", "filas históricas"),
    ]
    for col, (icon, lbl, val, sub) in zip([k1, k2, k3, k4], kpis):
        with col:
            st.markdown(f"""
            <div class="kpi-card">
              <div class="kpi-icon">{icon}</div>
              <div class="kpi-label">{lbl}</div>
              <div class="kpi-value">{val}</div>
              <div class="kpi-sub">{sub}</div>
            </div>""", unsafe_allow_html=True)

    st.info("👈 Configure los parámetros en el panel izquierdo y haga clic en **Generar Predicción**.")

# ══════════════════════════════════════════════════════════════
# PREDICCIÓN
# ══════════════════════════════════════════════════════════════

if predecir:
    if not meses_sel:
        st.warning("⚠️ Seleccione al menos un mes en el panel izquierdo.")
        st.stop()

    rows = []
    for mes in meses_sel:
        rows.append({
            "anio":        anio,
            "mes_num":     meses_num[mes],
            "departamento": departamento,
            "pais":        pais,
            "producto":    producto,
            "tradicion":   tradicion,
            "toneladas":   toneladas,
        })

    input_df  = build_input_df(rows)
    csv_bytes = input_df.to_csv(index=False).encode("utf-8")
    status_box = st.empty()

    try:
        result_raw = batch_predict(csv_bytes, status_box)
        status_box.empty()

        pred_col = next(
            (c for c in result_raw.columns if "prediction" in c.lower()),
            result_raw.columns[-1],
        )

        result_df = input_df.copy()
        result_df["Mes"] = meses_sel
        result_df["FOB_Miles_USD"] = result_raw[pred_col].values.round(2)
        result_df["FOB_USD"]       = (result_df["FOB_Miles_USD"] * 1_000).round(0)
        result_df["FOB_COP"]       = (result_df["FOB_USD"] * trm).round(0)

        # ── Encabezado resultados ─────────────────────────────
        st.markdown(
            f'<div class="results-header">📈 Resultados de Predicción &nbsp;·&nbsp; '
            f'{producto} &nbsp;·&nbsp; {departamento} → {pais} &nbsp;·&nbsp; {anio}</div>',
            unsafe_allow_html=True,
        )

        # ── TRM info ──────────────────────────────────────────
        if usar_cop:
            st.markdown(f"""
            <div class="trm-box">
              💱 &nbsp;<strong>Conversión activa:</strong>
              TRM utilizada: <strong>$ {trm:,.0f} COP/USD</strong>
              &nbsp;·&nbsp; Los valores en COP son referenciales y dependen del tipo de cambio vigente.
            </div>
            """, unsafe_allow_html=True)

        # ── KPI cards por mes ──────────────────────────────────
        st.markdown("#### 🗓️ Predicción por mes")
        n = len(result_df)
        cols = st.columns(min(n, 4))
        for i, row in result_df.iterrows():
            col_idx = i % min(n, 4)
            with cols[col_idx]:
                cop_html = (
                    f'<div class="kpi-cop">🇨🇴 $ {row["FOB_COP"]:,.0f} COP</div>'
                    if usar_cop else ""
                )
                st.markdown(f"""
                <div class="kpi-card">
                  <div class="kpi-icon">🚢</div>
                  <div class="kpi-label">📅 {row['Mes']} {anio}</div>
                  <div class="kpi-value big">$ {row['FOB_Miles_USD']:,.1f}K</div>
                  <div class="kpi-sub">Miles USD FOB</div>
                  {cop_html}
                </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── KPI totales ───────────────────────────────────────
        total_usd  = result_df["FOB_Miles_USD"].sum()
        prom_usd   = result_df["FOB_Miles_USD"].mean()
        max_usd    = result_df["FOB_Miles_USD"].max()
        mes_max    = result_df.loc[result_df["FOB_Miles_USD"].idxmax(), "Mes"]
        total_cop  = result_df["FOB_COP"].sum()

        st.markdown("#### 📊 Resumen consolidado")
        r1, r2, r3, r4 = st.columns(4)
        resumen = [
            (r1, "🚢",  "Total FOB Predicho",   f"$ {total_usd:,.1f}K",  "Miles USD acumulado",   ""),
            (r2, "📈",  "Promedio por Mes",      f"$ {prom_usd:,.1f}K",   "Miles USD / mes",       ""),
            (r3, "🏆",  f"Mejor Mes — {mes_max}", f"$ {max_usd:,.1f}K",  "Miles USD FOB",         ""),
            (r4, "🇨🇴", "Total en COP",          f"$ {total_cop/1e6:,.1f}M", "Millones de pesos", "green"),
        ]
        for col, icon, lbl, val, sub, card_cls in resumen:
            with col:
                cls = f"kpi-card {card_cls}".strip()
                st.markdown(f"""
                <div class="{cls}">
                  <div class="kpi-icon">{icon}</div>
                  <div class="kpi-label">{lbl}</div>
                  <div class="kpi-value">{val}</div>
                  <div class="kpi-sub">{sub}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Gráfica y tabla ───────────────────────────────────
        tab1, tab2 = st.tabs(["📊 Gráfico comparativo", "📋 Tabla detallada"])

        with tab1:
            chart_df = result_df.set_index("Mes")[["FOB_Miles_USD"]].rename(
                columns={"FOB_Miles_USD": "FOB Predicho (Miles USD)"}
            )
            st.bar_chart(chart_df, color="#1A5276")
            st.caption(f"Valor FOB mensual predicho — {producto} · {departamento} → {pais}")

        with tab2:
            display_cols = ["Mes", "Fecha", "Ton Netas Expo", "FOB_Miles_USD"]
            rename_map   = {
                "Ton Netas Expo": "Toneladas",
                "FOB_Miles_USD":  "FOB Predicho (Miles USD)",
            }
            if usar_cop:
                display_cols.append("FOB_COP")
                rename_map["FOB_COP"] = f"FOB COP (TRM {trm:,.0f})"

            st.dataframe(
                result_df[display_cols].rename(columns=rename_map),
                use_container_width=True,
                hide_index=True,
            )
            csv_out = result_df.rename(columns=rename_map).to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️  Descargar resultados CSV",
                csv_out,
                f"fob_{producto[:20].replace(' ','_')}_{anio}.csv",
                "text/csv",
                use_container_width=True,
            )

        # ── Resumen ejecutivo ─────────────────────────────────
        st.divider()
        st.success(
            f"**Resumen ejecutivo** · **{producto}** ({tradicion.lower()}) "
            f"desde **{departamento}** hacia **{pais}** · Año **{anio}** · "
            f"Meses: **{', '.join(meses_sel)}**\n\n"
            f"**FOB total:** USD {total_usd:,.1f} miles"
            + (f" · **COP:** $ {total_cop/1e6:,.1f} M (TRM {trm:,.0f})" if usar_cop else "")
            + f" · **Promedio mensual:** USD {prom_usd:,.1f} miles · "
            f"**Mejor mes:** {mes_max}"
        )

    except DRError as e:
        status_box.empty()
        st.error(f"❌ Error DataRobot: {e}")
    except Exception as e:
        status_box.empty()
        st.error(f"❌ Error inesperado: {e}")

# ══════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════

st.markdown("""
<div class="footer">
  🇨🇴 Inteligencia Comercial Agropecuaria &nbsp;|&nbsp;
  Machine Learning · DataRobot &nbsp;|&nbsp;
  Fuente: MADR · OAI &nbsp;|&nbsp;
  🌱 🚜 🚢 📦 📈
</div>
""", unsafe_allow_html=True)
