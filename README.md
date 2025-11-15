# 📚 Repositorio de Proyectos con n8n — Gestión, Seguridad y Analítica  

<p align="center">
  <a href="https://streamlit.io/">    <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" />
  </a>
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/Python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54" />
  </a>
  <a href="https://supabase.com/">
    <img src="https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white" />
  </a>
  <a href="https://n8n.io/">
    <img src="https://img.shields.io/badge/N8N-EA4C89?style=for-the-badge&logo=n8n&logoColor=white" />
  </a>
</p>

Este repositorio contiene **tres aplicaciones completas**, cada una organizada en su propia carpeta y documentada.  
A continuación se presenta un resumen para mayor claridad.

---

# 📦 **1. Vista General de los Proyectos**

| Proyecto | Tecnologías | Funcionalidades principales | Carpeta |
|---------|-------------|-----------------------------|---------|
| **Sistema de Gestión de Almacenes** | Streamlit, N8N, Supabase | CRUD, alertas de stock mínimo, estadísticas, PDF | `sistema-almacenes/` |
| **Detección de Phishing en URLs** | Streamlit, FastAPI, N8N, Supabase | Análisis en tiempo real, CSV, gráficos, PDF, mantenedores | `sistema-phishing/` |
| **Sistema Integral de Fatiga** | Streamlit, N8N, Supabase | Gestión de métricas fisiológicas, alertas automáticas, PDF | `sistema-fatiga/` |

---

# 📁 **2. Estructura del Repositorio**

| Carpeta / Archivo | Descripción |
|-------------------|-------------|
| `/sistema-almacenes` | Código fuente del sistema de almacenes |
| `/sistema-phishing` | Código y backend para análisis de phishing |
| `/sistema-fatiga` | Sistema predictivo de fatiga y reportes |
| `README.md` | Documentación general del repositorio |

---

# 📊 **3. Detalles por Proyecto**

## 🔹 **Sistema de Gestión de Almacenes**

| Elemento | Descripción |
|----------|-------------|
| Tecnologías | Streamlit · N8N · Supabase |
| Funciones | CRUD de productos/lineas, alertas, PDF, estadísticas |
| Tablas Supabase | PRODUCTO, LINEA |
| Carpeta | `sistema-almacenes/` |

---

## 🔹 **Detección de Phishing**

| Elemento | Descripción |
|----------|-------------|
| Tecnologías | Streamlit · FastAPI · Supabase · N8N |
| Funciones | Analizar URLs, CSV, gráficos, estadísticas, PDF |
| Tablas Supabase | url_analysis, url_results, users (si aplica) |
| Carpeta | `sistema-phishing/` |

---

## 🔹 **Sistema Integral de Fatiga**

| Elemento | Descripción |
|----------|-------------|
| Tecnologías | Streamlit · Supabase · N8N |
| Funciones | Predicción, visualización de métricas, alertas, PDF |
| Tablas Supabase | metricas_procesadas, operadores |
| Carpeta | `sistema-fatiga/` |

---

# ⚙️ **4. Instalación y Ejecución**

| Herramienta | Cómo instalar |
|-------------|---------------|
| Streamlit | `pip install streamlit` |
| FastAPI | `pip install fastapi uvicorn` |
| Supabase (Python) | `pip install supabase` |
| N8N | Docker o instalación local |

Cada proyecto tiene su propio README interno con pasos detallados.

---

## ✨ Información
Desarrollado como proyectos académicos y solución integral para proyectos de automatización, análisis y gestión basados en Streamlit, Supabase y N8N. 
