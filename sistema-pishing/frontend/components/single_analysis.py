import streamlit as st
import requests
import pandas as pd
from supabase import create_client, Client

# ----------------------------------------------------
# CONFIGURACIÓN GENERAL
# ----------------------------------------------------
API = "http://localhost:8000"
N8N_CREATE_WEBHOOK = "http://localhost:5678/webhook/create-url"
N8N_UPDATE = "http://localhost:5678/webhook/update-url"
N8N_DELETE = "http://localhost:5678/webhook/delete-url"

SUPABASE_URL = "https://dzjamsbehsubgamikryp.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR6amFtc2JlaHN1YmdhbWlrcnlwIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTE3MzkyMywiZXhwIjoyMDc0NzQ5OTIzfQ.6-rXL1utK-FqaXwWj5duwYIoIO0mQAzOiOI_P2D0ao0"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def show():
    st.title("🔍 Análisis Individual y Gestión de URLs")

    # Estilo CSS para botones pequeños
    st.markdown("""
        <style>
        div.stButton > button {
            padding: 0.35rem 0.9rem;
            font-size: 0.9rem;
            border-radius: 8px;
            background-color: #0d6efd;
            color: white;
            border: none;
            transition: 0.25s;
        }
        div.stButton > button:hover {
            background-color: #0b5ed7;
            transform: scale(1.03);
        }
        div.stButton { margin-bottom: 0.5rem; }
        </style>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🔎 Analizar URL", "📋 Gestionar URLs"])

    # ========================================================
    # TAB 1 — ANÁLISIS INDIVIDUAL
    # ========================================================
    with tab1:
        st.subheader("Analizar una URL en tiempo real")
        email = st.text_input("Correo del analista", "analyst@company.com")
        url = st.text_input("URL a analizar", "https://example.com/login")

        if st.button("🚀 Analizar URL"):
            if not url.startswith(("http://", "https://")):
                st.warning("⚠️ Incluye http:// o https:// en la URL.")
            else:
                try:
                    import hashlib
                    url_hash = hashlib.sha256(url.encode()).hexdigest()
                    existing = (
                        supabase.table("url_analysis")
                        .select("id, prediction, risk_level, probability, created_at")
                        .eq("url_hash", url_hash)
                        .execute()
                    )
                    if existing.data and len(existing.data) > 0:
                        registro = existing.data[0]
                        traduccion_pred = {
                            "PHISHING": "Phishing (fraudulenta)",
                            "SUSPICIOUS": "Sospechosa",
                            "LEGITIMATE": "Legítima",
                        }
                        traduccion_riesgo = {
                            "LOW": "Bajo",
                            "MEDIUM": "Medio",
                            "HIGH": "Alto",
                            "CRITICAL": "Crítico",
                        }
                        pred_esp = traduccion_pred.get(registro["prediction"], registro["prediction"])
                        riesgo_esp = traduccion_riesgo.get(registro["risk_level"], registro["risk_level"])
                        st.warning(
                            f"⚠️ Esta URL ya fue analizada anteriormente.\n\n"
                            f"**Resultado previo:** {pred_esp} — Riesgo {riesgo_esp} ({registro['probability']*100:.1f}%)\n\n"
                            f"📅 Fecha: {registro['created_at']}"
                        )
                        st.stop()

                    res = requests.post(f"{API}/analyze", json={"url": url, "created_by": email}, timeout=15)

                    if res.status_code == 200:
                        data = res.json()
                        result = data.get("data", {})
                        traduccion_pred = {
                            "PHISHING": "Phishing (fraudulenta)",
                            "SUSPICIOUS": "Sospechosa",
                            "LEGITIMATE": "Legítima",
                        }
                        traduccion_riesgo = {
                            "LOW": "Bajo",
                            "MEDIUM": "Medio",
                            "HIGH": "Alto",
                            "CRITICAL": "Crítico",
                        }
                        pred_esp = traduccion_pred.get(result.get("prediction"), result.get("prediction"))
                        riesgo_esp = traduccion_riesgo.get(result.get("risk_level"), result.get("risk_level"))
                        prob = result.get("probability", 0) * 100
                        st.success(f"✅ Resultado: **{pred_esp}** — Riesgo **{riesgo_esp} ({prob:.1f}%)**")
                    else:
                        st.error(f"⚠️ Error {res.status_code}: {res.text}")
                except Exception as e:
                    st.error(f"Error al analizar: {e}")

    # ========================================================
    # TAB 2 — GESTIÓN DE URLs
    # ========================================================
    with tab2:
        st.subheader("📋 Listado de URLs analizadas")

        analyst_email_main = st.text_input("📧 Correo del analista:", "analyst@company.com", key="correo_principal_tab2")

        # Botón para cargar los registros
        if st.button("🔄 Actualizar listado", key="btn_actualizar_listado"):
            try:
                res = (
                    supabase.table("url_analysis")
                    .select("id, url, prediction, risk_level, probability, created_at")
                    .order("created_at", desc=True)
                    .limit(50)
                    .execute()
                )
                data = res.data or []
                if data:
                    df = pd.DataFrame(data)

                    traduccion_pred = {
                        "PHISHING": "Phishing (fraudulenta)",
                        "SUSPICIOUS": "Sospechosa",
                        "LEGITIMATE": "Legítima",
                    }
                    traduccion_riesgo = {
                        "LOW": "Bajo",
                        "MEDIUM": "Medio",
                        "HIGH": "Alto",
                        "CRITICAL": "Crítico",
                    }

                    df["prediction"] = df["prediction"].map(traduccion_pred).fillna(df["prediction"])
                    df["risk_level"] = df["risk_level"].map(traduccion_riesgo).fillna(df["risk_level"])
                    df["probability"] = (df["probability"] * 100).round(1).astype(str) + " %"

                    df = df.rename(columns={
                        "id": "ID",
                        "url": "URL",
                        "prediction": "Predicción",
                        "risk_level": "Nivel de riesgo",
                        "probability": "Probabilidad",
                        "created_at": "Fecha de creación"
                    })

                    st.session_state["urls_df"] = df
                    st.success(f"✅ Se cargaron {len(df)} registros correctamente.")
                else:
                    st.info("ℹ️ No hay registros disponibles todavía.")
            except Exception as e:
                st.error(f"❌ Error al obtener datos desde Supabase: {e}")

        if "urls_df" in st.session_state:
            st.dataframe(st.session_state["urls_df"], use_container_width=True)

        # =====================================================
        # CREAR / EDITAR / ELIMINAR
        # =====================================================
        st.divider()
        st.markdown("### ⚙️ URLs")

        crud_tabs = st.tabs(["Crear nueva URL", "Editar / Reanalizar", "Eliminar"])

        # CREAR
        with crud_tabs[0]:
            st.subheader("Registrar y analizar nueva URL")
            new_url = st.text_input("🌐 Ingresar URL nueva:", key="nueva_url")
            email_crear = st.text_input("📧 Correo del analista:", analyst_email_main, key="correo_crear")
            if st.button("🚀 Analizar y registrar", key="btn_crear"):
                try:
                    res = requests.post(f"{API}/analyze", json={"url": new_url, "created_by": email_crear}, timeout=15)
                    if res.status_code == 200:
                        st.success("✅ URL registrada y analizada correctamente.")
                        st.experimental_rerun()
                    else:
                        st.error(f"⚠️ Error {res.status_code}: {res.text}")
                except Exception as e:
                    st.error(f"❌ Error al crear URL: {e}")

        # EDITAR
        with crud_tabs[1]:
            st.subheader("Editar o reanalizar una URL existente")
            if "urls_df" in st.session_state and not st.session_state["urls_df"].empty:
                selected_id = st.selectbox("Selecciona una URL por ID:", st.session_state["urls_df"]["ID"])
                updated_url = st.text_input("🔗 Nueva URL actualizada:", key="edit_url")
                email_editar = st.text_input("📧 Correo del analista:", analyst_email_main, key="correo_editar")
                if st.button("💾 Guardar cambios", key="btn_editar"):
                    try:
                        payload = {"id": selected_id, "url": updated_url, "updated_by": email_editar}
                        res = requests.post(N8N_UPDATE, json=payload, timeout=20)
                        if res.status_code == 200:
                            st.success("✅ URL actualizada correctamente.")
                            st.experimental_rerun()
                        else:
                            st.error(f"⚠️ Error {res.status_code}: {res.text}")
                    except Exception as e:
                        st.error(f"❌ Error al conectar con webhook UPDATE: {e}")
            else:
                st.info("ℹ️ No hay datos cargados para editar.")

        # ELIMINAR
        with crud_tabs[2]:
            st.subheader("Eliminar una URL")
            if "urls_df" in st.session_state and not st.session_state["urls_df"].empty:
                selected_del = st.selectbox("Selecciona la URL a eliminar:", st.session_state["urls_df"]["ID"])
                email_eliminar = st.text_input("📧 Correo del analista:", analyst_email_main, key="correo_eliminar")
                if st.button("❌ Eliminar URL", key="btn_eliminar"):
                    try:
                        payload = {"id": selected_del, "deleted_by": email_eliminar}
                        res = requests.post(N8N_DELETE, json=payload, timeout=15)
                        if res.status_code == 200:
                            st.success("✅ URL eliminada correctamente.")
                            st.experimental_rerun()
                        else:
                            st.error(f"⚠️ Error {res.status_code}: {res.text}")
                    except Exception as e:
                        st.error(f"❌ Error al conectar con webhook DELETE: {e}")
            else:
                st.info("ℹ️ No hay datos cargados para eliminar.")
