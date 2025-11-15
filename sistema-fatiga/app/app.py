import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
import base64
from datetime import datetime, timedelta
import PyPDF2
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from supabase import create_client, Client
import json
from typing import Dict, List, Tuple, Any
import bcrypt
import jwt
import time
from dotenv import load_dotenv
import os
import requests

# ===============================================
# 🔧 CONFIGURACIÓN GENERAL DE LA APLICACIÓN
# ===============================================
st.set_page_config(
    page_title="Sistema de Gestión de Fatiga",
    page_icon="😴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cargar variables de entorno desde .env
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

WEBHOOK_OPERADORES_CREATE = os.getenv("WEBHOOK_OPERADORES_CREATE")
WEBHOOK_OPERADORES_UPDATE = os.getenv("WEBHOOK_OPERADORES_UPDATE")
WEBHOOK_OPERADORES_DELETE = os.getenv("WEBHOOK_OPERADORES_DELETE")

WEBHOOK_DISPOSITIVOS_CREATE = os.getenv("WEBHOOK_DISPOSITIVOS_CREATE")
WEBHOOK_DISPOSITIVOS_UPDATE = os.getenv("WEBHOOK_DISPOSITIVOS_UPDATE")
WEBHOOK_DISPOSITIVOS_DELETE = os.getenv("WEBHOOK_DISPOSITIVOS_DELETE")

WEBHOOK_USUARIOS_CREATE = os.getenv("WEBHOOK_USUARIOS_CREATE")
WEBHOOK_USUARIOS_UPDATE = os.getenv("WEBHOOK_USUARIOS_UPDATE")
WEBHOOK_USUARIOS_DELETE = os.getenv("WEBHOOK_USUARIOS_DELETE")

WEBHOOK_METRICAS_CREATE = os.getenv("WEBHOOK_METRICAS_CREATE")
WEBHOOK_METRICAS_UPDATE = os.getenv("WEBHOOK_METRICAS_UPDATE")
WEBHOOK_METRICAS_DELETE = os.getenv("WEBHOOK_METRICAS_DELETE")

WEBHOOK_MEDICIONES_CREATE = os.getenv("WEBHOOK_MEDICIONES_CREATE")
WEBHOOK_MEDICIONES_DELETE = os.getenv("WEBHOOK_MEDICIONES_DELETE")

WEBHOOK_ALERTAS_EMAIL = os.getenv("WEBHOOK_ALERTAS_EMAIL")

WEBHOOK_INFORMES_CREATE = os.getenv("WEBHOOK_INFORMES_CREATE")
WEBHOOK_INFORMES_EMAIL = os.getenv("WEBHOOK_INFORMES_EMAIL")


# ===============================================
# 🔄 INICIALIZAR ESTADO DE SESIÓN
# ===============================================
if 'supabase' not in st.session_state:
    st.session_state.supabase = None
if 'usuario_actual' not in st.session_state:
    st.session_state.usuario_actual = None
if 'pagina_actual' not in st.session_state:
    st.session_state.pagina_actual = "Panel de Control"
if 'alertas_no_leidas' not in st.session_state:
    st.session_state.alertas_no_leidas = 0

def enviar_a_n8n(url, payload):
    try:
        r = requests.post(url, json=payload, timeout=12)
        if r.status_code == 200:
            return r.json()
        else:
            return {"error": f"Error HTTP {r.status_code}", "detalle": r.text}
    except Exception as e:
        return {"error": str(e)}

# ===============================================
# 🧭 BARRA LATERAL (login + conexión + navegación)
# ===============================================
def barra_lateral():
    st.sidebar.title("Sistema de Gestión de Fatiga")

    # -------------------------------
    # 🔐 CONFIGURACIÓN DE BASE DE DATOS
    # -------------------------------
    st.sidebar.subheader("Configuración de Base de Datos")

    # Campos visibles pero bloqueados
    url_supabase = st.sidebar.text_input(
        "URL de Supabase",
        value=SUPABASE_URL if SUPABASE_URL else "",
        type="password",
        disabled=True
    )
    clave_supabase = st.sidebar.text_input(
        "Clave de Supabase",
        value=SUPABASE_KEY if SUPABASE_KEY else "",
        type="password",
        disabled=True
    )

    # Conexión automática
    if 'supabase' not in st.session_state or st.session_state.supabase is None:
        if SUPABASE_URL and SUPABASE_KEY:
            try:
                st.session_state.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
                st.sidebar.success("✅ Conectado automáticamente a Supabase")
            except Exception as e:
                st.sidebar.error(f"Error al conectar automáticamente: {str(e)}")
        else:
            st.sidebar.warning("⚠️ Variables SUPABASE_URL o SUPABASE_KEY no encontradas en .env")

    # -------------------------------
    # 🔑 INICIO / CIERRE DE SESIÓN
    # -------------------------------
    if not st.session_state.usuario_actual:
        st.sidebar.subheader("Iniciar Sesión")
        email = st.sidebar.text_input("Email")
        contrasena = st.sidebar.text_input("Contraseña", type="password")

        if st.sidebar.button("Iniciar Sesión"):
            if email and contrasena:
                try:
                    response = st.session_state.supabase.table("usuarios_sistema").select("*").eq("email", email).execute()
                    if response.data:
                        usuario = response.data[0]
                        if bcrypt.checkpw(contrasena.encode('utf-8'), usuario['contrasena_hash'].encode('utf-8')):
                            st.session_state.usuario_actual = usuario
                            st.sidebar.success(f"Bienvenido, {usuario['nombre']}!")
                            st.rerun()
                        else:
                            st.sidebar.error("Contraseña incorrecta")
                    else:
                        st.sidebar.error("Usuario no encontrado")
                except Exception as e:
                    st.sidebar.error(f"Error al iniciar sesión: {str(e)}")
            else:
                st.sidebar.error("Por favor ingrese email y contraseña")
    else:
        st.sidebar.success(f"Conectado como: {st.session_state.usuario_actual['nombre']} {st.session_state.usuario_actual['apellido']}")
        st.sidebar.info(f"Rol: {st.session_state.usuario_actual['rol']}")
        if st.sidebar.button("Cerrar Sesión"):
            st.session_state.usuario_actual = None
            st.rerun()

    # -------------------------------
    # 📋 NAVEGACIÓN ENTRE MÓDULOS
    # -------------------------------
    if st.session_state.usuario_actual:
        st.sidebar.subheader("Navegación")
        rol = st.session_state.usuario_actual['rol']

        if rol in ['administrador', 'gerente_seguridad']:
            if st.sidebar.button("Panel de Control Principal"):
                st.session_state.pagina_actual = "Panel de Control Principal"
                st.rerun()

        if rol in ['administrador', 'supervisor']:
            if st.sidebar.button("Vista de Supervisor"):
                st.session_state.pagina_actual = "Vista de Supervisor"
                st.rerun()

        if rol == 'administrador':
            if st.sidebar.button("Mantenimiento de Tablas"):
                st.session_state.pagina_actual = "Mantenimiento de Tablas"
                st.rerun()

        if rol in ['administrador', 'gerente_seguridad']:
            if st.sidebar.button("Generador de Reportes"):
                st.session_state.pagina_actual = "Generador de Reportes"
                st.rerun()
            # 🔔 NUEVO: BOTÓN PARA VER ALERTAS
            if st.sidebar.button("Alertas"):
                st.session_state.pagina_actual = "Alertas"
                st.rerun()

# Panel de Control Principal (Gerente de Seguridad)
def panel_control_principal():
    st.title("Panel de Control Principal")

    # =========================================================
    # 📡 Cargar Alertas Activas
    # =========================================================
    try:
        response = st.session_state.supabase.table("alertas").select("*").eq("estado", "activa").execute()
        alertas_activas = response.data
        st.session_state.alertas_no_leidas = len(alertas_activas)
    except Exception as e:
        st.error(f"Error al obtener alertas: {str(e)}")
        alertas_activas = []

    # =========================================================
    # 📊 KPIs PRINCIPALES
    # =========================================================
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Alertas Activas", st.session_state.alertas_no_leidas)

    with col2:
        try:
            response = st.session_state.supabase.table("metricas_procesadas").select("indice_fatiga").execute()
            metricas = response.data
            if metricas:
                prom = sum(m['indice_fatiga'] for m in metricas) / len(metricas)
                st.metric("Fatiga Promedio", f"{prom:.2f}")
            else:
                st.metric("Fatiga Promedio", "N/A")
        except:
            st.metric("Fatiga Promedio", "Error")

    with col3:
        try:
            response = st.session_state.supabase.table("metricas_procesadas").select("id_operador").eq("clasificacion_riesgo", "Crítico").execute()
            operadores_riesgo = len(set(m['id_operador'] for m in response.data))
            st.metric("Operadores en Riesgo", operadores_riesgo)
        except:
            st.metric("Operadores en Riesgo", "Error")

    with col4:
        try:
            response = st.session_state.supabase.table("operadores").select("id").execute()
            st.metric("Operadores Totales", len(response.data))
        except:
            st.metric("Operadores Totales", "Error")

    # =========================================================
    # 🗺️ MAPA DE ESTADO DE LA FLOTA
    # =========================================================
    st.subheader("Estado de Fatiga de la Flota")

    try:
        operadores = st.session_state.supabase.table("operadores").select("*").execute().data

        datos_mapa = []

        for op in operadores:
            met = (
                st.session_state.supabase
                .table("metricas_procesadas")
                .select("*")
                .eq("id_operador", op["id"])
                .order("timestamp", desc=True)
                .limit(1)
                .execute()
                .data
            )

            if met:
                m = met[0]

                # --------------- ASIGNAR COLOR REAL ------------------
                color_raw = {
                    "Crítico": "red",
                    "Alto": "orange",
                    "Medio": "yellow",
                    "Bajo": "green"
                }.get(m["clasificacion_riesgo"], "green")

                datos_mapa.append({
                    "Operador": f"{op['nombre']} {op['apellido']}",
                    "Índice de Fatiga": m["indice_fatiga"],
                    "Clasificación": m["clasificacion_riesgo"],
                    "Color": color_raw,
                    "Color_Label": m["clasificacion_riesgo"],
                    "Turno": op.get("turno_asignado", "N/A")
                })

        if datos_mapa:
            df_mapa = pd.DataFrame(datos_mapa)

            # --------------- GRÁFICO DE ESTADO DE FLOTA ---------------
            fig = px.scatter(
                df_mapa,
                x=[i % 5 for i in range(len(df_mapa))],
                y=[i // 5 for i in range(len(df_mapa))],
                color="Color",
                hover_name="Operador",
                hover_data={
                    "Índice de Fatiga": True,
                    "Clasificación": True,
                    "Turno": True,
                    "Color_Label": False,
                    "Color": False
                },
                color_discrete_map={
                    "red": "red",
                    "orange": "orange",
                    "yellow": "yellow",
                    "green": "green"
                },
                title="Mapa de Estado de Fatiga de Operadores"
            )

            fig.update_xaxes(showticklabels=False)
            fig.update_yaxes(showticklabels=False)
            fig.update_layout(height=420)
            st.plotly_chart(fig, use_container_width=True)

            st.dataframe(df_mapa[["Operador", "Índice de Fatiga", "Clasificación", "Turno"]])
        else:
            st.info("No hay métricas registradas.")
    except Exception as e:
        st.error(f"Error al cargar mapa de flota: {str(e)}")

    # =========================================================
    # 📈 GRÁFICO: EVOLUCIÓN ÚLTIMAS 24H
    # =========================================================
    st.subheader("Análisis de Tendencias")

    colA, colB = st.columns(2)

    with colA:
        try:
            hace_24h = datetime.now() - timedelta(hours=24)
            metricas = (
                st.session_state.supabase
                .table("metricas_procesadas")
                .select("*")
                .gte("timestamp", hace_24h.isoformat())
                .execute()
                .data
            )

            if metricas:
                df = pd.DataFrame(metricas)
                df["timestamp"] = pd.to_datetime(df["timestamp"])
                df["hora"] = df["timestamp"].dt.floor("H")

                df_agg = df.groupby("hora")["indice_fatiga"].mean().reset_index()

                fig = px.line(
                    df_agg,
                    x="hora",
                    y="indice_fatiga",
                    title="Evolución del Índice de Fatiga (24h)",
                    labels={"hora": "Hora", "indice_fatiga": "Fatiga Promedio"}
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Sin datos en las últimas 24h.")
        except Exception as e:
            st.error(f"Error generando evolución: {str(e)}")

    # =========================================================
    # 🥧 GRÁFICO: DISTRIBUCIÓN DE RIESGOS
    # =========================================================
    with colB:
        try:
            operadores = st.session_state.supabase.table("operadores").select("id").execute().data

            clasifs = []
            for op in operadores:
                m = (
                    st.session_state.supabase
                    .table("metricas_procesadas")
                    .select("clasificacion_riesgo")
                    .eq("id_operador", op["id"])
                    .order("timestamp", desc=True)
                    .limit(1)
                    .execute()
                    .data
                )
                if m:
                    clasifs.append(m[0]["clasificacion_riesgo"])

            if clasifs:
                df = pd.DataFrame(clasifs, columns=["Nivel de Riesgo"])
                conteo = df["Nivel de Riesgo"].value_counts().reset_index()
                conteo.columns = ["Nivel de Riesgo", "Cantidad"]

                fig = px.pie(
                    conteo,
                    names="Nivel de Riesgo",
                    values="Cantidad",
                    title="Distribución de Operadores por Nivel de Riesgo"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Sin clasificaciones disponibles.")
        except Exception as e:
            st.error(f"Error generando distribución: {str(e)}")

    # =========================================================
    # 🚨 ALERTAS RECIENTES
    # =========================================================
    st.subheader("Alertas Recientes")

    try:
        alertas = (
            st.session_state.supabase
            .table("alertas")
            .select("*")
            .eq("estado", "activa")
            .order("timestamp", desc=True)
            .limit(10)
            .execute()
            .data
        )

        if not alertas:
            st.info("No hay alertas activas.")
            return

        op_ids = list(set(a["id_operador"] for a in alertas))
        ops = (
            st.session_state.supabase
            .table("operadores")
            .select("id,nombre,apellido")
            .in_("id", op_ids)
            .execute()
            .data
        )

        ops_map = {o["id"]: f"{o['nombre']} {o['apellido']}" for o in ops}

        for alert in alertas:
            col1, col2, col3, col4, col5, col6 = st.columns([1, 2, 1, 3, 2, 1])

            with col1:
                st.write(alert["id"][:8] + "...")

            with col2:
                st.write(ops_map.get(alert["id_operador"], "Desconocido"))

            with col3:
                st.write(alert["nivel_alerta"])

            with col4:
                st.write(alert["descripcion"])

            with col5:
                st.write(alert["timestamp"])

            with col6:
                if st.button("Resolver", key=f"resolver_{alert['id']}"):
                    st.session_state.supabase.table("alertas").update({
                        "estado": "resuelta",
                        "timestamp_resolucion": datetime.now().isoformat()
                    }).eq("id", alert["id"]).execute()

                    st.success("Alerta resuelta.")
                    st.rerun()

    except Exception as e:
        st.error(f"Error al cargar alertas: {str(e)}")



def vista_supervisor():
    st.title("Vista de Supervisor de Turno")

    # ================================
    # 🔵 1. Cargar operadores desde BD
    # ================================
    try:
        operadores = (
            st.session_state.supabase
            .table("operadores")
            .select("id, nombre, apellido, turno_asignado")
            .order("id")
            .execute()
            .data
        )
    except Exception as e:
        st.error(f"❌ Error al consultar operadores: {str(e)}")
        return

    st.subheader("Operadores en Turno")

    if not operadores:
        st.info("No hay operadores registrados.")
        return

    # ================================
    # 🔵 2. Obtener ultima métrica de cada operador
    # ================================
    lista_operadores = []

    for op in operadores:
        try:
            met_resp = (
                st.session_state.supabase
                .table("metricas_procesadas")
                .select("*")
                .eq("id_operador", op["id"])
                .order("timestamp", desc=True)
                .limit(1)
                .execute()
                .data
            )

            if met_resp:
                metrica = met_resp[0]
            else:
                metrica = None

        except Exception as e:
            st.error(f"❌ Error obteniendo métricas del operador {op['id']}: {str(e)}")
            metrica = None

        # ======================
        # Estado visual
        # ======================
        if metrica:
            clasif = metrica.get("clasificacion_riesgo", "Desconocido")
            indice = metrica.get("indice_fatiga", 0)

            if clasif == "Crítico":
                estado = "⚠️ Crítico"
            elif clasif == "Alto":
                estado = "🔶 Alto"
            elif clasif == "Medio":
                estado = "🟡 Medio"
            else:
                estado = "🟢 Bajo"

            timestamp = metrica.get("timestamp", "N/D")
        else:
            clasif = "Sin datos"
            estado = "⚪ Sin Métricas"
            indice = "N/A"
            timestamp = "N/A"

        lista_operadores.append({
            "id": op["id"],
            "Nombre": f"{op['nombre']} {op['apellido']}",
            "Turno": op.get("turno_asignado", "N/A"),
            "Índice de Fatiga": indice,
            "Clasificación": clasif,
            "Estado": estado,
            "Última Actualización": timestamp
        })

    # Convertir a DataFrame
    df = pd.DataFrame(lista_operadores)

    # ======================
    # 🔵 Mostrar la tabla
    # ======================
    st.dataframe(df, use_container_width=True)

    # ======================
    # 🔵 Botón ver detalles
    # ======================
    st.subheader("Ver detalles de operador")

    lista_nombres = [f"{o['Nombre']} - ID {o['id']}" for o in lista_operadores]
    seleccionado = st.selectbox("Selecciona un operador", lista_nombres)

    if st.button("Ver Detalles"):
        # Extraer ID
        op_id = seleccionado.split("ID ")[1]
        st.session_state.operador_seleccionado = op_id
        st.session_state.pagina_actual = "Detalles Operador"
        st.rerun()

    # ======================
    # 🔴 3. Panel de alertas
    # ======================
    st.subheader("Alertas Activas")

    try:
        alertas = (
            st.session_state.supabase
            .table("alertas")
            .select("*")
            .eq("estado", "activa")
            .order("timestamp", desc=True)
            .execute()
            .data
        )
    except Exception as e:
        st.error(f"❌ Error al cargar alertas: {str(e)}")
        alertas = []

    if not alertas:
        st.info("No hay alertas activas.")
        return

    # Obtener nombres de los operadores
    ids = list({a["id_operador"] for a in alertas})

    try:
        ops_map = (
            st.session_state.supabase
            .table("operadores")
            .select("id, nombre, apellido")
            .in_("id", ids)
            .execute()
            .data
        )
        nombre_map = {o["id"]: f"{o['nombre']} {o['apellido']}" for o in ops_map}
    except:
        nombre_map = {}

    # Mostrar alertas
    for alerta in alertas:
        nombre_op = nombre_map.get(alerta["id_operador"], "Desconocido")
        with st.expander(f"⚠️ {alerta['nivel_alerta']} – {nombre_op} – {alerta['id'][:8]}"):
            st.write(f"**Descripción:** {alerta['descripcion']}")
            st.write(f"**Fecha:** {alerta['timestamp']}")

            col1 = st.columns(1)[0]

            with col1:
                if st.button("Ignorar", key=f"ign_{alerta['id']}"):
                    st.session_state.supabase.table("alertas").update({
                        "estado": "resuelta",
                        "timestamp_resolucion": datetime.now().isoformat()
                    }).eq("id", alerta["id"]).execute()
                    st.success("Alerta marcada como resuelta")
                    st.rerun()

# Vista de detalles de operador
def vista_detalles_operador():
    st.title("Detalles del Operador")
    
    if 'operador_seleccionado' not in st.session_state:
        st.error("No se ha seleccionado un operador")
        return
    
    try:
        # ---------------------------
        # 📌 Obtener datos del operador
        # ---------------------------
        operador_response = st.session_state.supabase.table("operadores").select("*").eq("id", st.session_state.operador_seleccionado).execute()
        
        if not operador_response.data:
            st.error("Operador no encontrado")
            return
        
        operador = operador_response.data[0]
        
        # ---------------------------
        # 📌 Información general
        # ---------------------------
        st.subheader("Información General del Operador")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Nombre", f"{operador['nombre']} {operador['apellido']}")
        
        with col2:
            st.metric("Turno", operador.get('turno_asignado', 'N/A'))
        
        with col3:
            metrica_reciente = (
                st.session_state.supabase
                .table("metricas_procesadas")
                .select("*")
                .eq("id_operador", operador['id'])
                .order("timestamp", desc=True)
                .limit(1)
                .execute()
                .data
            )
            if metrica_reciente:
                st.metric("Índice de Fatiga", f"{metrica_reciente[0]['indice_fatiga']:.2f}")
            else:
                st.metric("Índice de Fatiga", "N/A")
        
        st.markdown("---")

        # ------------------------------------------------
        # 📊 GRÁFICO 1 — Evolución del Índice de Fatiga
        # ------------------------------------------------
        st.subheader("📈 Evolución del Índice de Fatiga Durante el Turno")

        hoy = datetime.now().date()
        inicio_turno = datetime.combine(hoy, datetime.min.time())
        
        metricas = (
            st.session_state.supabase
            .table("metricas_procesadas")
            .select("*")
            .eq("id_operador", operador['id'])
            .gte("timestamp", inicio_turno.isoformat())
            .order("timestamp")
            .execute()
            .data
        )
        
        if metricas:
            df = pd.DataFrame(metricas)
            df['timestamp'] = pd.to_datetime(df['timestamp'])

            fig_fatiga = px.line(
                df,
                x="timestamp",
                y="indice_fatiga",
                markers=True,
                title=f"Índice de Fatiga de {operador['nombre']} {operador['apellido']}",
                labels={"timestamp": "Hora", "indice_fatiga": "Índice de Fatiga"},
            )

            fig_fatiga.add_hline(
                y=80,
                line_dash="dash",
                line_color="red",
                annotation_text="Umbral crítico"
            )

            fig_fatiga.update_layout(height=380)

            st.plotly_chart(fig_fatiga, use_container_width=True)
        else:
            st.info("No hay datos de fatiga registrados en este turno.")

        st.markdown("---")

        # ------------------------------------------------
        # 📊 GRÁFICO 2 — Métricas fisiológicas clave
        # ------------------------------------------------
        st.subheader("❤️‍🩹 Métricas Fisiológicas del Turno")

        if metricas:
            df_phy = pd.DataFrame(metricas)
            df_phy['timestamp'] = pd.to_datetime(df_phy['timestamp'])

            # Mapa de qué métricas existen
            metricas_disponibles = {
                "HRV (ms)": "hrv",
                "SpO2 (%)": "spo2",
                "Frecuencia Cardíaca (bpm)": "frecuencia_cardiaca",
                "Temperatura de la Piel (°C)": "temperatura_piel"
            }

            # Generar gráfico por cada métrica
            for titulo, columna in metricas_disponibles.items():
                if columna in df_phy.columns and df_phy[columna].notna().any():

                    st.markdown(f"### {titulo}")

                    fig = px.line(
                        df_phy,
                        x="timestamp",
                        y=columna,
                        markers=True,
                        title="",
                        labels={"timestamp": "Hora", columna: titulo},
                    )

                    fig.update_layout(height=300)

                    st.plotly_chart(fig, use_container_width=True)

                    st.markdown("---")
        else:
            st.info("No hay métricas fisiológicas registradas para este operador.")
        
        # --------------------------
        # 🔙 Botón volver
        # --------------------------
        if st.button("⬅ Volver a Vista de Supervisor"):
            st.session_state.pagina_actual = "Vista de Supervisor"
            st.rerun()

    except Exception as e:
        st.error(f"Error al cargar detalles del operador: {str(e)}")


# =====================================================
#  Mantenimiento de Tablas (CRUD via N8N)
# =====================================================
def mantenimiento_tablas():
    st.title("Mantenimiento de Tablas")
    
    # Solo administradores pueden acceder
    if st.session_state.usuario_actual['rol'] != 'administrador':
        st.error("No tienes permisos para acceder a esta página")
        return
    
    # Seleccionar módulo
    tabla_seleccionada = st.selectbox(
        "Selecciona una tabla para administrar",
        ["operadores", "dispositivos", "usuarios_sistema", "metricas_procesadas", "mediciones_crudas"]
    )

    # =====================================================
    # 🔵 OPERADORES (CRUD via N8N)
    # =====================================================
    if tabla_seleccionada == "operadores":

        # Mostrar alerta si viene del último insert
        if "operador_creado" in st.session_state:
            st.success("✅ Operador creado exitosamente")
            del st.session_state["operador_creado"]

        st.subheader("Gestión de Operadores")

        # Crear nuevo operador
        with st.expander("➕ Agregar Nuevo Operador"):
            nombre = st.text_input("Nombre", key="crear_nombre")
            apellido = st.text_input("Apellido", key="crear_apellido")
            turno = st.selectbox("Turno", ["Mañana", "Tarde", "Noche"], key="crear_turno")

            if st.button("Guardar Operador"):
                if not nombre or not apellido:
                    st.error("⚠ Debes completar todos los campos")
                else:
                    payload = {
                        "nombre": nombre,
                        "apellido": apellido,
                        "turno_asignado": turno
                    }
                    resultado = enviar_a_n8n(WEBHOOK_OPERADORES_CREATE, payload)

                    if "error" in resultado:
                        st.error(f"❌ Error: {resultado['error']}")
                    else:
                        # Guardar estado para mostrar mensaje luego del rerun
                        st.session_state["operador_creado"] = True
                        st.rerun()

        # Listar operadores
        st.subheader("Operadores Registrados")
        try:
            response = st.session_state.supabase.table("operadores").select("*").order("id", desc=False).execute()
            operadores = response.data
        except Exception as e:
            st.error(f"❌ Error al cargar operadores: {e}")
            operadores = []

        if operadores:
            for operador in operadores:
                col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 1, 1])

                with col1:
                    st.write(operador["nombre"])

                with col2:
                    st.write(operador["apellido"])

                with col3:
                    st.write(operador.get("turno_asignado", "N/A"))

                with col4:
                    if st.button("Editar", key=f"edit_op_{operador['id']}"):
                        st.session_state.operador_editar = operador
                        st.session_state.pagina_actual = "Editar Operador"
                        st.rerun()

                with col5:
                    if st.button("❌", key=f"del_op_{operador['id']}"):
                        payload = {"id": operador["id"]}
                        resultado = enviar_a_n8n(WEBHOOK_OPERADORES_DELETE, payload)

                        if "error" in resultado:
                            st.error(f"❌ Error: {resultado['error']}")
                        else:
                            st.success("🗑 Operador eliminado")
                            st.rerun()
        else:
            st.info("No hay operadores registrados")

    # =====================================================
    # 🟢 DISPOSITIVOS (CRUD via N8N)
    # =====================================================
    elif tabla_seleccionada == "dispositivos":

        # Mostrar alerta si viene del último insert
        if "dispositivo_creado" in st.session_state:
            st.success("📱 Dispositivo registrado exitosamente")
            del st.session_state["dispositivo_creado"]

        st.subheader("Gestión de Dispositivos")

        # Crear dispositivo
        with st.expander("➕ Registrar Nuevo Dispositivo"):
            tipo = st.selectbox("Tipo de dispositivo", 
            [
                "SmartWatch",
                "Banda",
                "Casco Inteligente",
                "Chaleco Biométrico",
                "GPS Tracker",
                "BodyCam",
                "Tablet Rugged",
                "Smartphone Rugged",
                "Pulsioxímetro IoT",
                "Sensor de Proximidad",
                "Sensor de Vibración Portátil"
            ])
            modelo = st.text_input("Modelo")

            # Cargar operadores
            try:
                operadores = st.session_state.supabase.table("operadores").select("id,nombre,apellido").execute().data
                opciones = {f"{o['nombre']} {o['apellido']}": o['id'] for o in operadores}
            except:
                opciones = {}

            operador_sel = st.selectbox("Asignar a:", list(opciones.keys()) if opciones else ["Sin operadores"])
            operador_id = opciones.get(operador_sel)

            if st.button("Guardar Dispositivo"):
                if not modelo:
                    st.error("⚠ Debes escribir el modelo del dispositivo")
                else:
                    payload = {
                        "tipo": tipo,
                        "modelo": modelo,
                        "id_operador_asignado": operador_id
                    }

                    resultado = enviar_a_n8n(WEBHOOK_DISPOSITIVOS_CREATE, payload)

                    if "error" in resultado:
                        st.error(f"❌ Error: {resultado['error']}")
                    else:
                        st.session_state["dispositivo_creado"] = True
                        st.rerun()

        # Listar dispositivos
        st.subheader("Dispositivos Registrados")

        try:
            dispositivos = st.session_state.supabase.table("dispositivos").select("*").order("id", desc=False).execute().data
        except:
            dispositivos = []

        if dispositivos:
            # Mapeo operador → nombre completo
            try:
                operadores = st.session_state.supabase.table("operadores").select("id,nombre,apellido").execute().data
                map_operadores = {o["id"]: f"{o['nombre']} {o['apellido']}" for o in operadores}
            except:
                map_operadores = {}

            for dispositivo in dispositivos:
                col1, col2, col3, col4, col5 = st.columns([2,2,2,1,1])

                with col1: st.write(dispositivo["tipo"])
                with col2: st.write(dispositivo["modelo"])
                with col3: st.write(map_operadores.get(dispositivo["id_operador_asignado"], "Sin asignar"))

                # Botón editar
                with col4:
                    if st.button("Editar", key=f"edit_dis_{dispositivo['id']}"):
                        st.session_state.dispositivo_editar = dispositivo
                        st.session_state.pagina_actual = "Editar Dispositivo"
                        st.rerun()

                # Botón eliminar
                with col5:
                    if st.button("❌", key=f"del_dis_{dispositivo['id']}"):
                        payload = {"id": dispositivo["id"]}
                        resultado = enviar_a_n8n(WEBHOOK_DISPOSITIVOS_DELETE, payload)

                        if "error" in resultado:
                            st.error(f"❌ Error: {resultado['error']}")
                        else:
                            st.success("🗑 Dispositivo eliminado")
                            st.rerun()

        else:
            st.info("No hay dispositivos registrados.")

    # =====================================================
    # 🟡 USUARIOS DEL SISTEMA (CRUD via N8N)
    # =====================================================
    elif tabla_seleccionada == "usuarios_sistema":
        st.subheader("Gestión de Usuarios del Sistema")

        # Crear usuario
        with st.expander("➕ Agregar Nuevo Usuario"):
            nombre_usuario = st.text_input("Nombre de usuario")
            contrasena = st.text_input("Contraseña", type="password")
            nombre = st.text_input("Nombre")
            apellido = st.text_input("Apellido")
            email = st.text_input("Email")
            rol = st.selectbox("Rol", ["administrador", "gerente_seguridad", "supervisor"])

            if st.button("Guardar Usuario"):
                if not nombre or not apellido or not email or not nombre_usuario or not contrasena:
                    st.error("⚠ Todos los campos son obligatorios")
                else:
                    # Generar hash seguro en Streamlit
                    contrasena_hash = bcrypt.hashpw(contrasena.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

                    payload = {
                        "nombre_usuario": nombre_usuario,
                        "nombre": nombre,
                        "apellido": apellido,
                        "email": email,
                        "rol": rol,
                        "contrasena_hash": contrasena_hash
                    }

                    resultado = enviar_a_n8n(WEBHOOK_USUARIOS_CREATE, payload)

                    if "error" in resultado:
                        st.error(f"❌ Error: {resultado['error']}")
                    else:
                        st.success("👤 Usuario agregado")
                        st.rerun()

        # Listar usuarios
        st.subheader("Usuarios Registrados")
        try:
            usuarios = st.session_state.supabase.table("usuarios_sistema").select("*").execute().data
        except:
            usuarios = []

        if usuarios:
            for usuario in usuarios:
                col1, col2, col3, col4, col5 = st.columns([2,2,2,1,1])

                with col1: st.write(usuario["nombre"])
                with col2: st.write(usuario["apellido"])
                with col3: st.write(usuario["rol"])

                with col4:
                    if st.button("Editar", key=f"edit_usr_{usuario['id']}"):
                        st.session_state.usuario_editar = usuario
                        st.session_state.pagina_actual = "Editar Usuario"
                        st.rerun()

                with col5:
                    if st.button("❌", key=f"del_usr_{usuario['id']}"):
                        payload = {"id": usuario["id"]}
                        resultado = enviar_a_n8n(WEBHOOK_USUARIOS_DELETE, payload)

                        if "error" in resultado:
                            st.error(f"❌ Error: {resultado['error']}")
                        else:
                            st.success("🗑 Usuario eliminado")
                            st.rerun()
        else:
            st.info("No hay usuarios registrados")

    # =====================================================
    # 🔴 MÉTRICAS PROCESADAS (CRUD via N8N)
    # =====================================================
    elif tabla_seleccionada == "metricas_procesadas":
        
        st.subheader("Gestión de Métricas Procesadas")

        # ==========================
        # ➕ Crear nueva métrica
        # ==========================
        with st.expander("➕ Agregar Nueva Métrica"):
            # Seleccionar operador
            try:
                operadores = st.session_state.supabase.table("operadores").select("id,nombre,apellido").execute().data
                opciones_ops = {f"{o['nombre']} {o['apellido']}": o['id'] for o in operadores}
            except:
                opciones_ops = {}

            operador_sel = st.selectbox("Operador", list(opciones_ops.keys()))
            id_operador = opciones_ops.get(operador_sel)

            indice_fatiga = st.number_input("Índice de Fatiga (0-100)", min_value=0.0, max_value=100.0)
            clasificacion = st.selectbox("Clasificación de Riesgo", ["Bajo", "Medio", "Alto", "Crítico"])
            hrv = st.number_input("HRV", min_value=0.0)
            spo2 = st.number_input("SpO2 (%)", min_value=0.0, max_value=100.0)
            frecuencia = st.number_input("Frecuencia Cardíaca (bpm)", min_value=0)
            temperatura = st.number_input("Temperatura de Piel", min_value=0.0)

            if st.button("Guardar Métrica"):
                payload = {
                    "id_operador": id_operador,
                    "indice_fatiga": indice_fatiga,
                    "clasificacion_riesgo": clasificacion,
                    "hrv": hrv,
                    "spo2": spo2,
                    "frecuencia_cardiaca": frecuencia,
                    "temperatura_piel": temperatura,
                    "timestamp": datetime.now().isoformat()
                }

                resultado = enviar_a_n8n(WEBHOOK_METRICAS_CREATE, payload)

                if "error" in resultado:
                    st.error("❌ Error: " + resultado["error"])
                else:
                    st.success("📊 Métrica registrada correctamente")
                    st.rerun()

        # ==========================
        # 📋 Listado de métricas
        # ==========================
        st.subheader("Métricas Registradas")

        try:
            metricas = st.session_state.supabase.table("metricas_procesadas").select("*").order("timestamp", desc=True).limit(50).execute().data
        except:
            metricas = []

        if metricas:
            for m in metricas:
                col1, col2, col3, col4, col5 = st.columns([2,2,2,1,1])

                with col1: st.write(m["timestamp"])
                with col2: st.write(m["indice_fatiga"])
                with col3: st.write(m["clasificacion_riesgo"])

                with col4:
                    if st.button("Editar", key=f"edit_m_{m['id']}"):
                        st.session_state.metrica_editar = m
                        st.session_state.pagina_actual = "Editar Métrica"
                        st.rerun()

                with col5:
                    if st.button("❌", key=f"del_m_{m['id']}"):
                        payload = {"id": m["id"]}
                        r = enviar_a_n8n(WEBHOOK_METRICAS_DELETE, payload)

                        if "error" in r:
                            st.error("❌ Error: " + r["error"])
                        else:
                            st.success("🗑 Métrica eliminada")
                            st.rerun()
        else:
            st.info("No hay métricas registradas.")

    # =====================================================
    # 🟠 MEDICIONES CRUDAS (CRUD via N8N)
    # =====================================================
    elif tabla_seleccionada == "mediciones_crudas":

        st.subheader("Gestión de Mediciones Crudas")

        # -------------------------
        # Crear medición cruda
        # -------------------------
        with st.expander("➕ Registrar Medición Cruda"):
            timestamp = st.text_input("Timestamp (ISO8601)", datetime.now().isoformat())
            
            # Dispositivos
            try:
                dispositivos = st.session_state.supabase.table("dispositivos").select("id, tipo, modelo").execute().data
                opciones = {f"{d['tipo']} {d['modelo']}": d["id"] for d in dispositivos}
            except:
                opciones = {}

            disp_sel = st.selectbox("Dispositivo", list(opciones.keys()))
            id_disp = opciones.get(disp_sel)

            raw_text = st.text_area("Datos Brutos (JSON)", "{\n  \"hrv_raw\": 50,\n  \"spo2_raw\": 97\n}")

            if st.button("Guardar Medición"):
                try:
                    datos_json = json.loads(raw_text)
                except:
                    st.error("JSON inválido")
                    return

                payload = {
                    "timestamp": timestamp,
                    "id_dispositivo": id_disp,
                    "datos_brutos": datos_json
                }

                r = enviar_a_n8n(WEBHOOK_MEDICIONES_CREATE, payload)

                if "error" in r:
                    st.error("❌ " + r["error"])
                else:
                    st.success("📥 Medición registrada")
                    st.rerun()

        # -------------------------
        # Listar mediciones
        # -------------------------
        st.subheader("Mediciones Registradas")

        try:
            mediciones = (
                st.session_state.supabase
                .table("mediciones_crudas")
                .select("*")
                .order("timestamp", desc=True)
                .limit(50)
                .execute()
                .data
            )
        except:
            mediciones = []

        if mediciones:
            for m in mediciones:
                col1, col2, col3, col4 = st.columns([2,2,3,1])

                with col1: st.write(m["timestamp"])
                with col2: st.write(m["id_dispositivo"])
                with col3: st.json(m["datos_brutos"])

                with col4:
                    if st.button("❌", key=f"del_med_{m['id']}"):
                        payload = {"id": m["id"]}
                        r = enviar_a_n8n(WEBHOOK_MEDICIONES_DELETE, payload)

                        if "error" in r:
                            st.error("❌ " + r["error"])
                        else:
                            st.success("🗑 Medición eliminada")
                            st.rerun()

        else:
            st.info("No hay mediciones registradas.")


# =====================================================

# =====================================================
# ✏ PANTALLA DE EDICIÓN DE OPERADORES (UPDATE via N8N)
# =====================================================
def editar_operador():
    operador = st.session_state.get("operador_editar", None)

    if not operador:
        st.error("No se encontró el operador a editar.")
        return

    st.title("✏ Editar Operador")

    nuevo_nombre = st.text_input("Nombre", operador["nombre"], key="editar_nombre")
    nuevo_apellido = st.text_input("Apellido", operador["apellido"], key="editar_apellido")
    nuevo_turno = st.selectbox(
        "Turno",
        ["Mañana", "Tarde", "Noche"],
        index=["Mañana","Tarde","Noche"].index(operador.get("turno_asignado","Mañana")),
        key="editar_turno"
    )

    # Botón guardar cambios
    if st.button("Guardar Cambios"):
        payload = {
            "id": operador["id"],
            "nombre": nuevo_nombre,
            "apellido": nuevo_apellido,
            "turno_asignado": nuevo_turno
        }

        resultado = enviar_a_n8n(WEBHOOK_OPERADORES_UPDATE, payload)

        if "error" in resultado:
            st.error(f"❌ Error al actualizar: {resultado['error']}")
        else:
            st.success("✅ Operador actualizado correctamente")
            st.session_state.pagina_actual = "Mantenimiento de Tablas"
            st.rerun()

    # Botón volver
    if st.button("⬅ Volver"):
        st.session_state.pagina_actual = "Mantenimiento de Tablas"
        st.rerun()
# =====================================================

# =====================================================
# ✏ PANTALLA DE EDICIÓN DE DISPOSITIVOS (UPDATE via N8N)
# =====================================================
def editar_dispositivo():
    dispositivo = st.session_state.get("dispositivo_editar", None)

    if not dispositivo:
        st.error("No se encontró el dispositivo a editar.")
        return

    st.title("✏ Editar Dispositivo")

    # 🔵 Lista completa de tipos (igual que en crear dispositivo)
    tipos_dispositivos = [
        "SmartWatch",
        "Banda",
        "Casco Inteligente",
        "Chaleco Biométrico",
        "GPS Tracker",
        "BodyCam",
        "Tablet Rugged",
        "Smartphone Rugged",
        "Pulsioxímetro IoT",
        "Sensor de Proximidad",
        "Sensor de Vibración Portátil"
    ]

    # Si el tipo guardado no está en la lista, lo agregamos temporalmente
    if dispositivo["tipo"] not in tipos_dispositivos:
        tipos_dispositivos.append(dispositivo["tipo"])

    nuevo_tipo = st.selectbox(
        "Tipo",
        tipos_dispositivos,
        index=tipos_dispositivos.index(dispositivo["tipo"]),
        key="edit_tipo"
    )

    nuevo_modelo = st.text_input("Modelo", dispositivo["modelo"], key="edit_modelo")

    # Operadores disponibles
    try:
        operadores = st.session_state.supabase.table("operadores").select("id,nombre,apellido").execute().data
        map_ops = {f"{o['nombre']} {o['apellido']}": o["id"] for o in operadores}
        lista_ops = list(map_ops.keys())
        actual = [k for k,v in map_ops.items() if v == dispositivo["id_operador_asignado"]]
        index_sel = lista_ops.index(actual[0]) if actual else 0
    except:
        lista_ops = ["Sin operadores"]
        map_ops = {}
        index_sel = 0

    operador_sel = st.selectbox("Asignado a:", lista_ops, index=index_sel)
    operador_id = map_ops.get(operador_sel)

    # Guardar cambios
    if st.button("Guardar Cambios"):
        payload = {
            "id": dispositivo["id"],
            "tipo": nuevo_tipo,
            "modelo": nuevo_modelo,
            "id_operador_asignado": operador_id
        }

        resultado = enviar_a_n8n(WEBHOOK_DISPOSITIVOS_UPDATE, payload)

        if "error" in resultado:
            st.error(f"❌ Error al actualizar: {resultado['error']}")
        else:
            st.success("✅ Dispositivo actualizado correctamente")
            st.session_state.pagina_actual = "Mantenimiento de Tablas"
            st.rerun()

    # Botón volver
    if st.button("⬅ Volver"):
        st.session_state.pagina_actual = "Mantenimiento de Tablas"
        st.rerun()
# =====================================================

# =====================================================
# ✏ PANTALLA DE EDICIÓN DE USUARIOS DEL SISTEMA (UPDATE via N8N)
# =====================================================
def editar_usuario():
    usuario = st.session_state.get("usuario_editar", None)

    if not usuario:
        st.error("No se encontró el usuario a editar.")
        return

    st.title("✏ Editar Usuario del Sistema")

    # Campos editables
    nuevo_nombre_usuario = st.text_input("Nombre de Usuario", usuario["nombre_usuario"], key="edit_usr_username")
    nuevo_nombre = st.text_input("Nombre", usuario["nombre"], key="edit_usr_nombre")
    nuevo_apellido = st.text_input("Apellido", usuario["apellido"], key="edit_usr_apellido")
    nuevo_email = st.text_input("Email", usuario["email"], key="edit_usr_email")

    roles_disponibles = ["administrador", "gerente_seguridad", "supervisor"]

    nuevo_rol = st.selectbox(
        "Rol",
        roles_disponibles,
        index=roles_disponibles.index(usuario["rol"]),
        key="edit_usr_rol"
    )

    # Campo para cambiar contraseña
    nueva_contrasena = st.text_input(
        "Nueva contraseña (opcional)",
        type="password",
        key="edit_usr_pass"
    )

    st.info("Si dejas la contraseña en blanco, se mantendrá la anterior.")

    # Guardar cambios
    if st.button("Guardar Cambios"):
        
        # Construir payload dinámico
        payload = {
            "id": usuario["id"],
            "nombre_usuario": nuevo_nombre_usuario,
            "nombre": nuevo_nombre,
            "apellido": nuevo_apellido,
            "email": nuevo_email,
            "rol": nuevo_rol
        }

        # Solo enviar contraseña si se modificó
        if nueva_contrasena.strip() != "":
            salt = bcrypt.gensalt()
            hashed_pw = bcrypt.hashpw(nueva_contrasena.encode('utf-8'), salt).decode('utf-8')
            payload["contrasena_hash"] = hashed_pw

        resultado = enviar_a_n8n(WEBHOOK_USUARIOS_UPDATE, payload)

        if "error" in resultado:
            st.error(f"❌ Error al actualizar: {resultado['error']}")
        else:
            st.success("✅ Usuario actualizado correctamente")
            st.session_state.pagina_actual = "Mantenimiento de Tablas"
            st.rerun()

    # Botón volver
    if st.button("⬅ Volver"):
        st.session_state.pagina_actual = "Mantenimiento de Tablas"
        st.rerun()
# =====================================================

def editar_metrica():
    m = st.session_state.get("metrica_editar", None)

    if not m:
        st.error("No se encontró la métrica a editar.")
        return

    st.title("✏ Editar Métrica")

    nuevo_indice = st.number_input(
        "Índice de Fatiga",
        value=float(m.get("indice_fatiga") or 0),
        min_value=0.0,
        max_value=100.0
    )

    nueva_clasif = st.selectbox(
        "Clasificación",
        ["Bajo", "Medio", "Alto", "Crítico"],
        index=["Bajo","Medio","Alto","Crítico"].index(m.get("clasificacion_riesgo", "Bajo"))
    )

    nuevo_hrv = st.number_input("HRV", value=float(m.get("hrv") or 0))
    nuevo_spo2 = st.number_input("SpO2 (%)", value=float(m.get("spo2") or 0))
    nuevo_fc = st.number_input("Frecuencia Cardíaca", value=int(m.get("frecuencia_cardiaca") or 0))
    nuevo_temp = st.number_input("Temperatura Piel (°C)", value=float(m.get("temperatura_piel") or 0))

    if st.button("Guardar Cambios"):
        payload = {
            "id": m["id"],
            "indice_fatiga": nuevo_indice,
            "clasificacion_riesgo": nueva_clasif,
            "hrv": nuevo_hrv,
            "spo2": nuevo_spo2,
            "frecuencia_cardiaca": nuevo_fc,
            "temperatura_piel": nuevo_temp
        }

        r = enviar_a_n8n(WEBHOOK_METRICAS_UPDATE, payload)

        if "error" in r:
            st.error("❌ Error: " + r["error"])
        else:
            st.success("✅ Métrica actualizada")
            st.session_state.pagina_actual = "Mantenimiento de Tablas"
            st.rerun()

    if st.button("⬅ Volver"):
        st.session_state.pagina_actual = "Mantenimiento de Tablas"
        st.rerun()
# =====================================================


def generar_pdf_reporte(titulo, descripcion, metricas, operadores, alertas, dispositivos, mediciones):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    estilos = getSampleStyleSheet()
    historia = []

    # ============================
    # TÍTULO
    # ============================
    historia.append(Paragraph(titulo, estilos["Heading1"]))
    historia.append(Spacer(1, 12))
    historia.append(Paragraph(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}", estilos["Normal"]))
    historia.append(Spacer(1, 12))
    historia.append(Paragraph(descripcion, estilos["BodyText"]))
    historia.append(Spacer(1, 18))

    # Función auxiliar para reemplazar None
    def clean(value):
        return value if value not in [None, "", "null"] else "----"

    # =====================================
    # BLOQUE: MÉTRICAS
    # =====================================
    historia.append(Paragraph("📊 Últimas Métricas", estilos["Heading2"]))
    if metricas:
        datos = [["Fecha", "Fatiga", "HRV", "SpO2"]]

        for m in metricas:
            datos.append([
                clean(m.get("timestamp")),
                clean(m.get("indice_fatiga")),
                clean(m.get("hrv")),
                clean(m.get("spo2"))
            ])

        tabla = Table(datos)
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))
        historia.append(tabla)
    else:
        historia.append(Paragraph("Sin datos.", estilos["Normal"]))

    historia.append(Spacer(1, 18))

    # =====================================
    # BLOQUE: OPERADORES
    # =====================================
    historia.append(Paragraph("👷 Operadores Registrados", estilos["Heading2"]))
    if operadores:
        datos = [["Nombre", "Apellido", "Turno"]]
        for o in operadores:
            datos.append([
                clean(o.get("nombre")),
                clean(o.get("apellido")),
                clean(o.get("turno_asignado"))
            ])
        tabla = Table(datos)
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))
        historia.append(tabla)
    else:
        historia.append(Paragraph("Sin datos.", estilos["Normal"]))

    historia.append(Spacer(1, 18))

    # =====================================
    # BLOQUE: ALERTAS
    # =====================================
    historia.append(Paragraph("🚨 Alertas Activas", estilos["Heading2"]))
    if alertas:
        datos = [["Fecha", "Nivel", "Descripción"]]
        for a in alertas:
            datos.append([
                clean(a.get("timestamp")),
                clean(a.get("nivel_alerta")),
                clean(a.get("descripcion"))
            ])
        tabla = Table(datos)
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))
        historia.append(tabla)
    else:
        historia.append(Paragraph("Sin datos.", estilos["Normal"]))

    historia.append(Spacer(1, 18))

    # =====================================
    # BLOQUE: DISPOSITIVOS
    # =====================================
    historia.append(Paragraph("📱 Dispositivos Registrados", estilos["Heading2"]))
    if dispositivos:
        datos = [["Tipo", "Modelo", "ID operador"]]
        for d in dispositivos:
            datos.append([
                clean(d.get("tipo")),
                clean(d.get("modelo")),
                clean(d.get("id_operador_asignado"))
            ])
        tabla = Table(datos)
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))
        historia.append(tabla)
    else:
        historia.append(Paragraph("Sin datos.", estilos["Normal"]))

    historia.append(Spacer(1, 18))

    # =====================================
    # BLOQUE: MEDICIONES CRUDAS
    # =====================================
    historia.append(Paragraph("📡 Mediciones Crudas", estilos["Heading2"]))
    if mediciones:
        datos = [["Fecha", "Dispositivo", "JSON"]]
        for m in mediciones:
            datos.append([
                clean(m.get("timestamp")),
                clean(m.get("id_dispositivo")),
                clean(str(m.get("datos_brutos")))
            ])
        tabla = Table(datos)
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))
        historia.append(tabla)
    else:
        historia.append(Paragraph("Sin datos.", estilos["Normal"]))

    # Finalizar PDF
    doc.build(historia)
    buffer.seek(0)
    return buffer.getvalue()



# =====================================================
# 📄 GENERADOR DE UN SOLO REPORTE (CORREGIDO)
# =====================================================
def generador_reporte_unico():
    st.title("📄 Generar Informe Completo")

    titulo = st.text_input("Título del reporte", "Informe General del Sistema")
    descripcion = "Informe generado automáticamente con los datos más recientes del sistema."

    # ============================
    # OBTENER TODAS LAS TABLAS
    # ============================
    try:
        metricas = st.session_state.supabase.table("metricas_procesadas").select("*").order("timestamp", desc=True).limit(20).execute().data
        operadores = st.session_state.supabase.table("operadores").select("*").order("id").execute().data
        alertas = st.session_state.supabase.table("alertas").select("*").order("timestamp", desc=True).limit(20).execute().data
        dispositivos = st.session_state.supabase.table("dispositivos").select("*").order("id").execute().data
        mediciones = st.session_state.supabase.table("mediciones_crudas").select("*").order("timestamp", desc=True).limit(20).execute().data
    except Exception as e:
        st.error(f"❌ Error cargando datos: {e}")
        return

    if st.button("⚡ Generar y Enviar Informe"):
        pdf_bytes = generar_pdf_reporte(titulo, descripcion, metricas, operadores, alertas, dispositivos, mediciones)
        pdf_b64 = base64.b64encode(pdf_bytes).decode("utf-8")

        payload = {
            "tipo_informe": "general",
            "archivo_pdf_base64": pdf_b64,
            "parametros_filtro": {
                "fecha_generacion": datetime.now().isoformat(),
                "metricas": len(metricas),
                "operadores": len(operadores),
                "alertas": len(alertas),
                "dispositivos": len(dispositivos),
                "mediciones": len(mediciones)
            }
        }

        r = enviar_a_n8n(WEBHOOK_INFORMES_CREATE, payload)

        if "error" in r:
            st.error("❌ Error enviando a n8n: " + r["error"])
        else:
            st.success("✅ Informe enviado correctamente")

        st.download_button(
            "📥 Descargar PDF",
            data=pdf_bytes,
            file_name="informe_general.pdf",
            mime="application/pdf"
        )


# =====================================================
# 📧 PÁGINA PARA ENVIAR ALERTAS POR EMAIL (Webhook)
# =====================================================
def enviar_alertas():
    st.title("📧 Enviar Alerta por Email")

    st.markdown("""
    Aquí puedes **crear una alerta manual** basada en los operadores y métricas registradas en la BD.  
    """)

    # ============================
    # 🔄 CARGAR OPERADORES
    # ============================
    try:
        operadores = (
            st.session_state.supabase
            .table("operadores")
            .select("id, nombre, apellido")
            .order("nombre")
            .execute()
            .data
        )
    except Exception as e:
        st.error(f"❌ Error al obtener operadores: {str(e)}")
        return

    if not operadores:
        st.info("No hay operadores registrados.")
        return

    # Convertir a diccionario {nombre_completo : id}
    map_ops = {
        f"{op['nombre']} {op['apellido']}": op["id"]
        for op in operadores
    }

    st.subheader("Datos de la Alerta")

    operador_sel = st.selectbox("Operador", list(map_ops.keys()))
    id_operador = map_ops.get(operador_sel)

    nivel = st.selectbox(
        "Nivel de Alerta",
        ["Bajo", "Medio", "Alto", "Crítico"]
    )

    descripcion = st.text_area(
        "Descripción de la Alerta",
        "Ingrese la razón de la alerta..."
    )

    # Email destino
    st.subheader("Destino del Email")
    email_destino = st.text_input(
        "Enviar alerta a este correo",
        value=st.session_state.usuario_actual['email']
    )

    if st.button("📨 Enviar Alerta"):
        if not descripcion.strip():
            st.error("⚠ Debe ingresar una descripción.")
            return
        
        payload = {
            "id_operador": id_operador,
            "nivel_alerta": nivel,
            "descripcion": descripcion,
            "email_destino": email_destino,
            "timestamp": datetime.now().isoformat()
        }

        r = enviar_a_n8n(os.getenv("WEBHOOK_ALERTAS_EMAIL"), payload)

        if "error" in r:
            st.error("❌ Error al enviar alerta: " + r["error"])
        else:
            st.success("✅ Alerta enviada correctamente.")

    # Botón para volver
    if st.button("⬅ Volver"):
        st.session_state.pagina_actual = "Panel de Control Principal"
        st.rerun()
# ============================

# Función principal
def principal():
    barra_lateral()
    
    # Verificar si el usuario ha iniciado sesión
    if not st.session_state.usuario_actual:
        st.title("Sistema de Gestión de Fatiga")
        st.markdown("""
        Bienvenido al Sistema de Gestión de Fatiga para Operadores de Maquinaria Pesada.
        
        Este sistema permite:
        - Monitorear en tiempo real los niveles de fatiga de los operadores
        - Predecir estados de fatiga antes de que conduzcan a accidentes
        - Generar alertas automáticas para supervisores
        - Analizar tendencias y patrones de fatiga
        - Generar informes de cumplimiento y gestión
        
        Por favor, inicie sesión para acceder al sistema.
        """)
        return
    
    # Verificar si hay conexión a Supabase
    if not st.session_state.supabase:
        st.error("Por favor conecte a la base de datos Supabase en la configuración")
        return
    
    # Navegación según página actual
    if st.session_state.pagina_actual == "Panel de Control Principal":
        panel_control_principal()
    elif st.session_state.pagina_actual == "Vista de Supervisor":
        vista_supervisor()
    elif st.session_state.pagina_actual == "Detalles Operador":
        vista_detalles_operador()
    elif st.session_state.pagina_actual == "Mantenimiento de Tablas":
        mantenimiento_tablas()
    elif st.session_state.pagina_actual == "Editar Operador":
        editar_operador()
    elif st.session_state.pagina_actual == "Editar Dispositivo":
        editar_dispositivo()
    elif st.session_state.pagina_actual == "Editar Usuario":
        editar_usuario()
    elif st.session_state.pagina_actual == "Editar Métrica":
        editar_metrica()
    elif st.session_state.pagina_actual == "Generador de Reportes":
        generador_reporte_unico()
    elif st.session_state.pagina_actual == "Alertas":
        enviar_alertas()
    else:
        # Página por defecto según rol
        if st.session_state.usuario_actual['rol'] in ['administrador', 'gerente_seguridad']:
            panel_control_principal()
        elif st.session_state.usuario_actual['rol'] == 'supervisor':
            vista_supervisor()
        else:
            st.error("Rol no reconocido")

if __name__ == "__main__":
    principal()
