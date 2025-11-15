# 🛡 Sistema de Detección de Phishing

<p align="center">
  <a href="https://streamlit.io/">
    <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" />
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

Aplicación construida con **Streamlit**, **FastAPI**, **Supabase** y **N8N**.

## ✔ Funcionalidades

| Módulo | Descripción |
|--------|-------------|
| Análisis en tiempo real | Evalúa una URL |
| Carga de CSV | Analiza múltiples URLs |
| Estadísticas | KPIs y gráficos |
| PDF | Reportes automáticos |
| CRUD | Mantenedores completos |

---

## 🗂 Tablas Supabase

| Tabla | Campos |
|------|---------|
| url_analysis | url, risk_level, result |
| url_results | features, prediction |
| users | email, password |

---

## 📁 Estructura

```
sistema-phishing/
├── streamlit-app/
├── fastapi-backend/
└── n8n-flows/
```

---

## ⚙ Ejecutar

```
pip install streamlit fastapi uvicorn supabase
streamlit run main.py
uvicorn main:app --reload
```

