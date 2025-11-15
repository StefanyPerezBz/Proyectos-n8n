# 📦 Sistema de Gestión de Almacenes

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

Aplicación desarrollada con **Streamlit**, **Supabase** y **N8N**.

## ✔ Funcionalidades

| Módulo | Descripción |
|--------|-------------|
| CRUD de Productos | Crear, editar, leer y eliminar |
| CRUD de Líneas | Gestión completa |
| Alertas automáticas | Stock ≤ punto de reorden |
| Estadísticas | KPIs, tablas, gráficas |
| Reporte PDF | Generación automática |

---

## 🗂 Tablas Supabase

| Tabla | Campos |
|-------|--------|
| LINEA | idLinea, descripcion |
| PRODUCTO | codigo, descripcion, precio, stock, reorden, idLinea |

---

## 📁 Estructura del Proyecto

```
sistema-almacenes/
├── streamlit-app/
├── n8n-flows/
└── supabase/
```

---

## ⚙ Instalación

```
pip install streamlit supabase
streamlit run app.py
```


