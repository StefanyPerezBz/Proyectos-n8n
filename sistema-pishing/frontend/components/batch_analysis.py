import streamlit as st
import requests
import io
import time
import pandas as pd

API = "http://localhost:8000"

def show():
    st.title("📁 Análisis por Lote (CSV)")
    st.markdown("Sube un archivo `.csv` que contenga una columna llamada **url**. El sistema analizará cada enlace y guardará los resultados en Supabase.")

    # ==========================================================
    # 📥 Descargar CSV de ejemplo
    # ==========================================================
    st.subheader("📥 Archivo de ejemplo para pruebas")
    st.markdown("Descarga un archivo CSV de ejemplo con URLs legítimas, sospechosas y fraudulentas para probar el sistema.")

    # CSS para hacer el botón más pequeño
    st.markdown("""
        <style>
        div.stDownloadButton > button {
            padding: 0.25rem 0.75rem;
            font-size: 0.85rem;
            border-radius: 8px;
            background-color: #0d6efd;
            color: white;
            border: none;
            transition: 0.3s;
        }
        div.stDownloadButton > button:hover {
            background-color: #0b5ed7;
            transform: scale(1.03);
        }
        </style>
    """, unsafe_allow_html=True)

    data = {
        "url": [
            "https://www.sunat.gob.pe",
            "https://facebook.com",
            "http://paypal-secure-login.com",
            "https://tinyurl.com/2p9e6hxs",
            "http://update-your-bank-info.xyz",
            "https://www.gob.pe",
            "http://secure-login-support.net",
            "https://twitter.com",
            "http://verify-account-paypal.info",
            "https://www.untrujillo.edu.pe"
        ]
    }

    df = pd.DataFrame(data)
    csv_bytes = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Descargar CSV de ejemplo",
        data=csv_bytes,
        file_name="urls_prueba.csv",
        mime="text/csv",
        use_container_width=False  # ❗️ Desactiva ancho completo
    )

    st.divider()

    # ==========================================================
    # 📤 Subir archivo CSV
    # ==========================================================
    uploaded_file = st.file_uploader("Selecciona tu archivo CSV", type=["csv"])

    # 🧠 Campo para analista (opcional)
    analyst_email = st.text_input("📧 Correo del analista:", "analyst@company.com")

    # ==========================================================
    # 🚀 Enviar CSV para análisis
    # ==========================================================
    if uploaded_file and st.button("🚀 Enviar para análisis"):
        try:
            with st.spinner("Analizando URLs, esto puede tardar unos segundos..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
                params = {"created_by": analyst_email}

                res = requests.post(f"{API}/analyze-csv", files=files, params=params, timeout=120)
                
                if res.status_code == 200:
                    data = res.json()
                    total = data.get("total_analyzed", 0)
                    st.success(f"✅ {total} URLs procesadas correctamente")

                    if "results" in data:
                        st.dataframe(data["results"], use_container_width=True)
                else:
                    st.error(f"⚠️ Error {res.status_code}: {res.text}")

            countdown = st.empty()
            for i in range(5, 0, -1):
                countdown.info(f"⏳ Actualizando en {i} segundos…")
                time.sleep(1)
            countdown.empty()
            st.experimental_rerun()

        except requests.exceptions.ConnectionError:
            st.error("❌ No se pudo conectar con el servidor. Verifica que FastAPI esté corriendo.")
        except Exception as e:
            st.error(f"❌ Error inesperado: {e}")

    elif not uploaded_file:
        st.info("📎 Sube un archivo CSV para comenzar el análisis.")
