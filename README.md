# 🌱 Modelo de Predicción Valor FOB Exportaciones Agrícolas Colombianas

## Descripción

Aplicación desarrollada en **Streamlit** e integrada con **DataRobot** para estimar el valor FOB de exportaciones agrícolas colombianas mediante técnicas de Machine Learning.

El sistema permite seleccionar variables clave de una operación de exportación y generar una predicción en tiempo real del valor estimado de exportación utilizando un modelo entrenado sobre más de 86.000 registros históricos.

---

## Objetivo

Facilitar la toma de decisiones en operaciones de comercio exterior mediante la estimación anticipada del valor FOB exportado a partir de variables comerciales y logísticas.

---

## Tecnologías Utilizadas

* Python
* Streamlit
* Pandas
* NumPy
* DataRobot
* Machine Learning
* GitHub
* Streamlit Cloud

---

## Variables de Entrada

La aplicación utiliza las siguientes variables para realizar la predicción:

| Variable            | Descripción                           |
| ------------------- | ------------------------------------- |
| Producto            | Producto agrícola exportado           |
| País                | País de destino de la exportación     |
| Departamento        | Departamento de origen                |
| Ton Netas Expo      | Toneladas netas exportadas            |
| Fecha               | Fecha estimada de exportación         |
| Tradición productos | Clasificación automática del producto |

---

## Variable Objetivo

El modelo predice:

**Valor Miles FOB Del Exportado**

Indicador utilizado para estimar el valor económico de la exportación.

---

## Características de la Aplicación

### Interfaz Ejecutiva

* Diseño corporativo y profesional.
* Paleta de colores orientada a análisis empresarial.
* Diseño responsive para escritorio y dispositivos móviles.

### Automatización

* Carga dinámica de productos.
* Carga dinámica de países.
* Carga dinámica de departamentos.
* Identificación automática del tipo de producto:

  * Tradicional
  * No Tradicional

### Analítica

* Predicción en tiempo real mediante DataRobot.
* Indicadores clave del conjunto de datos.
* Gráficos históricos de exportaciones.
* Ranking de productos exportados.

---

## Modelo Predictivo

### Algoritmo Seleccionado

Light Gradient Boosted Trees Regressor

### Resultados Obtenidos

| Métrica        | Resultado |
| -------------- | --------: |
| R²             |    0.9614 |
| MAE            |     63.99 |
| RMSE           |    425.47 |
| Gamma Deviance |    0.3146 |

El modelo explica aproximadamente el 96% de la variabilidad observada en el valor FOB exportado.

---

## Estructura del Proyecto

```text
exportaciones-agricolas/
│
├── app.py
├── requirements.txt
├── fecha_exportaciones_agricolas.csv
├── README.md
└── .gitignore
```

---

## Instalación Local

### Clonar repositorio

```bash
git clone https://github.com/usuario/exportaciones-agricolas.git
cd exportaciones-agricolas
```

### Instalar dependencias

```bash
pip install -r requirements.txt
```

### Ejecutar aplicación

```bash
streamlit run app.py
```

---

## Configuración de Secrets

Crear el archivo:

```text
.streamlit/secrets.toml
```

Contenido:

```toml
DATAROBOT_API_KEY="TU_API_KEY"
DATAROBOT_DEPLOYMENT_ID="6a3d5f2bc2ffbc809e884f57"
DATAROBOT_ENDPOINT="https://app.datarobot.com/api/v2"
```

⚠️ Nunca subir este archivo a GitHub.

---

## Despliegue en Streamlit Cloud

1. Crear repositorio en GitHub.
2. Subir:

   * app.py
   * requirements.txt
   * fecha_exportaciones_agricolas.csv
   * README.md
3. Conectar repositorio a Streamlit Cloud.
4. Configurar los Secrets.
5. Desplegar la aplicación.

---

## Casos de Uso

* Comercio exterior.
* Planeación de exportaciones.
* Inteligencia de negocios.
* Análisis agroindustrial.
* Evaluación de oportunidades comerciales.
* Simulación de escenarios de exportación.

---

## Autor

Kevin Andrés Nieto

Especialista en Gestión de Facilidades, Operaciones y Analítica de Datos.

---

## Licencia

Este proyecto tiene fines académicos, demostrativos y de análisis empresarial.

