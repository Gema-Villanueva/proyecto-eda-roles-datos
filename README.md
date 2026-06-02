# 📊 Análisis Exploratorio de Datos: Roles de Datos en España

Proyecto de análisis exploratorio de datos (EDA) sobre las ofertas laborales de roles de datos en España. Este proyecto incluye la recopilación, limpieza, análisis y visualización de datos del mercado laboral.

---

## 🎯 Objetivo del Proyecto

Analizar las tendencias del mercado laboral en roles de datos en España, identificando patrones sobre:
- Requisitos de las posiciones disponibles
- Niveles salariales
- Habilidades y competencias más demandadas
- Ubicaciones geográficas
- Tipos de empresas que contratan

---

## 📁 Estructura del Repositorio

```
proyecto-eda-roles-datos/
├── 📂 data/                 # Datos crudos y procesados
├── 📂 notebooks/            # Notebooks de análisis (Jupyter)
├── 📂 src/                  # Código fuente y funciones reutilizables
├── 📂 scripts/              # Scripts de utilidad y automatización
├── 📂 images/               # Gráficos y visualizaciones generadas
├── 📂 slides/               # Presentaciones del proyecto
├── 📄 streamlit_app.py      # Aplicación interactiva Streamlit
├── 📄 requirements.txt       # Dependencias del proyecto
├── 📄 .env.example          # Ejemplo de variables de entorno
└── 📄 README.md             # Este archivo
```

### Descripción de Directorios

| Directorio | Descripción |
|-----------|------------|
| **data/** | Contiene los datasets crudos y procesados utilizados en el análisis |
| **notebooks/** | Jupyter notebooks con análisis paso a paso del EDA |
| **src/** | Módulos Python con funciones reutilizables |
| **scripts/** | Scripts para recopilación, limpieza y procesamiento de datos |
| **images/** | Visualizaciones, gráficos y diagramas generados |
| **slides/** | Presentaciones en PowerPoint o similares |

---

## 🛠️ Requisitos

- Python 3.8+
- pip (gestor de paquetes)

---

## 📦 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/Gema-Villanueva/proyecto-eda-roles-datos.git
cd proyecto-eda-roles-datos
```

### 2. Crear un entorno virtual (recomendado)

```bash
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate

# En macOS/Linux:
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env con tus credenciales si es necesario
```

---

## 🚀 Uso

### Ejecutar la aplicación Streamlit

```bash
streamlit run streamlit_app.py
```

La aplicación se abrirá en `http://localhost:8501`

### Ejecutar los notebooks

```bash
jupyter notebook
```

Navega a la carpeta `notebooks/` para explorar los análisis.

---

## 📚 Dependencias Principales

| Paquete | Versión | Propósito |
|---------|---------|----------|
| **pandas** | 3.0.3 | Manipulación y análisis de datos |
| **numpy** | 2.4.6 | Operaciones numéricas |
| **matplotlib** | 3.10.9 | Visualizaciones estáticas |
| **seaborn** | 0.13.2 | Visualizaciones estadísticas |
| **plotly** | 6.7.0 | Visualizaciones interactivas |
| **streamlit** | ≥1.38.0 | Aplicación web interactiva |
| **scipy** | 1.17.1 | Análisis estadístico |
| **statsmodels** | 0.14.6 | Modelado estadístico avanzado |
| **requests** | 2.34.2 | Recopilación de datos (API) |
| **python-dotenv** | 1.2.2 | Gestión de variables de entorno |

Ver `requirements.txt` para la lista completa.

---

## 📊 Análisis Realizado

El proyecto incluye análisis en las siguientes áreas:

- **Análisis descriptivo**: Estadísticas generales de los datos
- **Análisis de tendencias**: Evolución temporal de las ofertas
- **Análisis geográfico**: Distribución por regiones
- **Análisis de salarios**: Rangos salariales por rol y experiencia
- **Análisis de habilidades**: Competencias más demandadas
- **Correlaciones**: Relaciones entre variables

---

## 📋 Notas Importantes

- **Archivo resumen de limpieza**: Consulta el [resumen del Notebook 02_cleaning](https://drive.google.com/file/d/1g_i_RqJJvXcAPSGRkVwbPwOxGejGn5eY/view?usp=drive_link)
- Los datos crudos se encuentran en la carpeta `data/`
- Las visualizaciones generadas se guardan en `images/`

---

## 📝 Notebooks Disponibles

En la carpeta `notebooks/` encontrarás:

1. **01_exploracion_inicial.ipynb** - Carga y exploración básica de datos
2. **02_cleaning.ipynb** - Limpieza y preparación de datos
3. **03_analisis_exploratorio.ipynb** - EDA detallado
4. **04_visualizaciones.ipynb** - Gráficos y visualizaciones
5. **05_conclusiones.ipynb** - Hallazgos y conclusiones

---

## 👥 Contribuciones

Las contribuciones son bienvenidas. Para contribuir:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-feature`)
3. Commit tus cambios (`git commit -m 'Agrega nueva feature'`)
4. Push a la rama (`git push origin feature/nueva-feature`)
5. Abre un Pull Request

---

## 📄 Licencia

Este proyecto no tiene licencia especificada. Consulta con el propietario del repositorio para más información.

---

## 📧 Contacto

Para preguntas o sugerencias sobre este proyecto, contacta con [Gema-Villanueva](https://github.com/Gema-Villanueva).

---

## 🔗 Enlaces Útiles

- [Documentación de Pandas](https://pandas.pydata.org/)
- [Documentación de Streamlit](https://docs.streamlit.io/)
- [Jupyter Notebook](https://jupyter.org/)

---

**Última actualización**: 2 de junio de 2026
