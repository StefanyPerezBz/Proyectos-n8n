# ⛏ Sistema Integral de Fatiga

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

Proyecto basado en **Streamlit**, **Supabase** y **N8N**.

## ✔ Funcionalidades

| Módulo | Descripción |
|--------|-------------|
| Carga de métricas | HRV, SpO2, Fatiga |
| Dashboard | KPIs, gráficas |
| Predicción | Modelo + N8N |
| Alertas | Integración automática |
| PDF | Reportes ejecutivos |

---

## 🗂 Tablas Supabase

| Tabla | Campos |
|------|---------|
| metricas_procesadas | hrv, spo2, fatiga, timestamp |
| operadores | nombre, apellido, turno |

---

## 📁 Estructura

```
sistema-fatiga/
├── streamlit-app/
├── n8n-flows/
└── supabase/
```

---

## ⚙ Instalación

```
pip install streamlit supabase
streamlit run main.py
```

