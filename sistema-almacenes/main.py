# ==========================================================
# 🏭 SISTEMA DE GESTIÓN DE ALMACÉN — Streamlit + n8n + Supabase
# ==========================================================
import streamlit as st
from datetime import datetime
import sys, os

# Garantiza que se puedan importar módulos locales
sys.path.append(os.path.dirname(__file__))

# Clientes personalizados
from supabase_client import SupabaseClient
from n8n_client import N8NClient


# ==========================================================
# CONFIGURACIÓN GENERAL
# ==========================================================
st.set_page_config(
    page_title="Sistema de Gestión de Almacén",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==========================================================
# INICIALIZACIÓN DE COMPONENTES
# ==========================================================
@st.cache_resource
def init_components():
    return {"db": SupabaseClient(), "n8n": N8NClient()}


components = init_components()
db = components["db"]
n8n = components["n8n"]

# ==========================================================
# SIDEBAR PRINCIPAL
# ==========================================================
st.sidebar.title("🏭 Sistema de Gestión de Almacén")

menu = st.sidebar.radio(
    "Selecciona un módulo:",
    [
        "📊 Dashboard",
        "📦 Productos",
        "🏷️ Líneas",
        "🧾 Reportes PDF",
        "🚨 Alertas de Stock",
    ],
)

# ==========================================================
# MÓDULO PRODUCTOS
# ==========================================================
if menu == "📦 Productos":
    st.header("📦 Mantenedor de Productos")

    subopcion = st.sidebar.radio(
        "Acción:",
        [
            "➕ Crear Producto",
            "📖 Leer Productos",
            "✏️ Actualizar Producto",
            "🗑️ Eliminar Producto",
        ],
    )

    from modulos.productos import (
        crear_producto,
        leer_productos,
        actualizar_producto,
        eliminar_producto,
    )

    if subopcion == "➕ Crear Producto":
        crear_producto(db, n8n)
    elif subopcion == "📖 Leer Productos":
        leer_productos(db)
    elif subopcion == "✏️ Actualizar Producto":
        actualizar_producto(db, n8n)
    elif subopcion == "🗑️ Eliminar Producto":
        eliminar_producto(db, n8n)


# ==========================================================
# MÓDULO LÍNEAS
# ==========================================================
elif menu == "🏷️ Líneas":
    st.header("🏷️ Mantenedor de Líneas")

    subopcion = st.sidebar.radio(
        "Acción:",
        ["➕ Crear Línea", "📖 Leer Líneas", "✏️ Actualizar Línea", "🗑️ Eliminar Línea"],
    )

    from modulos.lineas import (
        crear_linea,
        leer_lineas,
        actualizar_linea,
        eliminar_linea,
    )

    if subopcion == "➕ Crear Línea":
        crear_linea(db, n8n)
    elif subopcion == "📖 Leer Líneas":
        leer_lineas(db)
    elif subopcion == "✏️ Actualizar Línea":
        actualizar_linea(db, n8n)
    elif subopcion == "🗑️ Eliminar Línea":
        eliminar_linea(db, n8n)

# ==========================================================
# DASHBOARD
# ==========================================================
elif menu == "📊 Dashboard":
    from modulos.dashboard import mostrar_dashboard

    mostrar_dashboard(db)

# ==========================================================
# REPORTES PDF
# ==========================================================
elif menu == "🧾 Reportes PDF":
    st.header("🧾 Generar Reportes en PDF")
    from modulos.reportes import generar_reportes

    generar_reportes(db, n8n)

# ==========================================================
# ALERTAS
# ==========================================================
elif menu == "🚨 Alertas de Stock":
    st.header("🚨 Alerta Automática por Stock Bajo")
    from modulos.alertas import disparar_alertas

    disparar_alertas(db, n8n)

# ==========================================================
# PIE DE PÁGINA
# ==========================================================
st.markdown(
    """
    ---
    **Desarrollado por:** Stefany Perez 
    🧠 *— Proyecto de Gestión de Almacén*
    """
)
