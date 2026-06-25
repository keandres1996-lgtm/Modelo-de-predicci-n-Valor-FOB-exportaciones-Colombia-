# 🌱 Predicción FOB — Exportaciones Agrícolas Colombia

Sistema de analítica predictiva para estimar el **Valor FOB exportado** (en Miles de USD y pesos colombianos) de productos agrícolas colombianos, potenciado por un modelo de Machine Learning desplegado en **DataRobot**.

---

## 📋 Descripción general

Esta aplicación web, construida con **Streamlit**, permite a equipos de comercio exterior, analistas agropecuarios y tomadores de decisiones obtener proyecciones mensuales del valor FOB de exportación para cualquier combinación de producto, departamento de origen y país de destino registrada en la base de datos histórica del MADR-OAI.

El flujo completo es:

1. El usuario configura los parámetros en el panel lateral izquierdo.
2. La app construye el CSV de entrada y lo envía a la **API de Batch Predictions de DataRobot**.
3. DataRobot ejecuta el modelo XGBoost entrenado y devuelve las predicciones.
4. Los resultados se muestran como tarjetas KPI, gráficos y tabla descargable, con opción de conversión a pesos colombianos (COP).

---

## 🗂️ Estructura del proyecto

```
proyecto/
│
├── app.py                              # Aplicación principal Streamlit
├── fecha_exportaciones_agricolas.csv   # Dataset histórico (MADR-OAI)
├── requirements.txt                    # Dependencias Python
└── .streamlit/
    └── secrets.toml                    # Credenciales (NO subir a Git)
```

---

## ⚙️ Requisitos previos

- Python **3.9** o superior
- Cuenta activa en **DataRobot** con un deployment de predicción configurado
- Acceso a la API de DataRobot (API Key)

---

## 🚀 Instalación y ejecución local

### 1. Clonar o descargar el proyecto

```bash
git clone https://github.com/tu-org/fob-exportaciones.git
cd fob-exportaciones
```

### 2. Crear y activar un entorno virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

Contenido de `requirements.txt`:

```
streamlit>=1.35.0
pandas>=2.0.0
numpy>=1.25.0
requests>=2.31.0
```

### 4. Configurar credenciales

Crear el archivo `.streamlit/secrets.toml` (nunca incluir en control de versiones):

```toml
DATAROBOT_API_KEY       = "tu_api_key_aqui"
DATAROBOT_DEPLOYMENT_ID = "id_del_deployment_aqui"
DATAROBOT_ENDPOINT      = "https://app.datarobot.com"   # o tu instancia privada
```

### 5. Ubicar el dataset

Copiar el archivo `fecha_exportaciones_agricolas.csv` en la **raíz del proyecto** (mismo directorio que `app.py`).

### 6. Ejecutar la aplicación

```bash
streamlit run app.py
```

La app estará disponible en `http://localhost:8501`.

---

## 🗃️ Dataset de referencia

| Columna | Tipo | Descripción |
|---|---|---|
| `Descripción Departamento` | texto | Departamento colombiano de origen |
| `Pais` | texto | País de destino de la exportación |
| `Valor Miles FOB Dol Expo` | numérico | Valor FOB histórico en miles de USD |
| `Ton Netas Expo` | numérico | Toneladas netas exportadas |
| `Producto _(MADR_OAI)` | texto | Nombre del producto (clasificación MADR) |
| `Tradición productos` | texto | `Tradicional` / `No tradicional` |
| `Fecha` | fecha | Fecha de corte mensual (`YYYY-MM-01`) |

El dataset cubre el período **enero 2024 – marzo 2026** con **86.532 registros**, 256+ productos, 174 países de destino y 27 departamentos.

---

## 🖥️ Funcionalidades de la interfaz

### Panel lateral (sidebar)
| Sección | Control | Descripción |
|---|---|---|
| 📦 Producto | Selectbox | Lista dinámica de todos los productos del dataset |
| 🏷️ Tipo de bien | Solo lectura | Se autocompleta: `Tradicional` / `No tradicional` |
| 🌍 País destino | Selectbox | 174 países disponibles |
| 🗺️ Departamento | Selectbox | 27 departamentos exportadores |
| ⚖️ Toneladas | Número | Volumen estimado de exportación |
| 📅 Año | Número | Año objetivo de la predicción (2024–2035) |
| 🗓️ Meses | Multiselect | Selección múltiple de meses en español |
| 💱 Conversión COP | Toggle + TRM | Activa conversión a pesos con TRM ajustable |

### Panel principal — Estado inicial
- Resumen de parámetros seleccionados
- Gráfico de líneas del **histórico de exportaciones** (toneladas)
- KPIs del dataset: productos, países, departamentos y total de registros

### Panel principal — Resultados
- **Tarjetas KPI por mes**: valor FOB en grande con equivalente en COP
- **Tarjetas resumen**: Total FOB, Promedio mensual, Mejor mes, Total en millones COP
- **Gráfico de barras** comparativo por mes
- **Tabla detallada** con columna COP opcional
- **Descarga en CSV** con nombre automático por producto y año
- **Resumen ejecutivo** en texto con todos los indicadores clave

---

## 🔗 Integración con DataRobot

La app utiliza la **Batch Predictions API v2** de DataRobot con el siguiente flujo:

```
POST /api/v2/batchPredictions/   →  Crea el job
PUT  {csvUploadUrl}              →  Sube el CSV de entrada
GET  /api/v2/batchPredictions/{id}/  →  Polling cada 5 s hasta completar
GET  {downloadUrl}               →  Descarga resultados
```

El CSV enviado a DataRobot incluye las columnas:

```
Descripción Departamento | Pais | Ton Netas Expo |
Producto _(MADR_OAI)     | Tradición productos | Fecha
```

El timeout máximo de espera es **300 segundos**. Si el job falla o se agota el tiempo, la app muestra un mensaje de error descriptivo.

---

## 💱 Conversión a pesos colombianos (COP)

Cuando el toggle **"Mostrar también en pesos colombianos"** está activo:

- Se habilita un campo editable con la **TRM** (Tasa Representativa del Mercado).
- El valor por defecto es **$ 4.150 COP/USD** — actualizable en cada sesión.
- La conversión aplica a: tarjetas por mes, tarjeta resumen "Total COP", tabla descargable y resumen ejecutivo.
- Los valores en COP son **referenciales** y dependen del tipo de cambio vigente.

> Para obtener la TRM oficial del día consultar el Banco de la República: [https://www.banrep.gov.co/es/estadisticas/trm](https://www.banrep.gov.co/es/estadisticas/trm)

---

## 🎨 Diseño y paleta de colores

| Elemento | Color |
|---|---|
| Fondo principal | `#F0F4F8` gris claro institucional |
| Sidebar | `#0B1F3A → #0F2D4A` azul marino corporativo |
| Acentos / botones | `#2E86C1` azul ejecutivo |
| KPI card — COP | `#2E7D32` verde sector agro |
| Textos principales | `#0B1F3A` azul oscuro |
| Fuente | Inter (Google Fonts) + fallback Segoe UI |

---

## 🔒 Seguridad y buenas prácticas

- Las credenciales de DataRobot se almacenan exclusivamente en `.streamlit/secrets.toml`.
- Agregar `.streamlit/secrets.toml` al `.gitignore` antes de publicar el repositorio.
- El dataset CSV **no debe contener datos personales** ni información sensible.
- Para producción, considerar restringir el acceso a la app mediante autenticación de Streamlit Cloud o un proxy corporativo.

Ejemplo de `.gitignore`:

```
.streamlit/secrets.toml
venv/
__pycache__/
*.pyc
```

---

## ☁️ Despliegue en Streamlit Community Cloud

1. Subir el proyecto a un repositorio GitHub (privado recomendado).
2. Ir a [share.streamlit.io](https://share.streamlit.io) e iniciar sesión.
3. Hacer clic en **New app** y seleccionar el repositorio.
4. En **Advanced settings → Secrets**, pegar el contenido del `secrets.toml`.
5. Asegurarse de que `fecha_exportaciones_agricolas.csv` esté en el repositorio.
6. Clic en **Deploy**.

---

## 🐛 Solución de problemas frecuentes

| Error | Causa probable | Solución |
|---|---|---|
| `KeyError: 'DATAROBOT_API_KEY'` | `secrets.toml` no configurado | Crear el archivo con las tres claves requeridas |
| `FileNotFoundError: fecha_exportaciones_agricolas.csv` | Dataset no encontrado | Copiar el CSV a la raíz del proyecto |
| `❌ Error DataRobot: 401` | API Key inválida o expirada | Verificar y regenerar la clave en DataRobot |
| `❌ Error DataRobot: 404` | Deployment ID incorrecto | Confirmar el ID en el panel de DataRobot |
| `Tiempo de espera agotado` | Job muy grande o red lenta | Reducir el número de meses o aumentar `TIMEOUT` en `app.py` |
| Catálogos vacíos en selectbox | CSV con columnas renombradas | Verificar que los nombres de columna coincidan con los esperados |

---

## 📦 Variables de entorno / secrets

| Clave | Requerido | Descripción |
|---|---|---|
| `DATAROBOT_API_KEY` | ✅ Sí | Token de autenticación de la API de DataRobot |
| `DATAROBOT_DEPLOYMENT_ID` | ✅ Sí | ID del deployment del modelo XGBoost |
| `DATAROBOT_ENDPOINT` | Opcional | URL base de DataRobot (default: `https://app.datarobot.com`) |

---

## 🤝 Contribuciones

1. Hacer fork del repositorio.
2. Crear una rama descriptiva: `git checkout -b feature/nueva-funcionalidad`.
3. Hacer commit de los cambios: `git commit -m "feat: descripción del cambio"`.
4. Abrir un Pull Request con descripción detallada.

---

## 📄 Licencia

Uso interno — Proyecto de Inteligencia Comercial Agropecuaria.
Consultar con el equipo responsable antes de redistribuir.

---

*🇨🇴 Inteligencia Comercial Agropecuaria · Machine Learning aplicado al Comercio Exterior Colombiano · Fuente: MADR · OAI · DataRobot*
