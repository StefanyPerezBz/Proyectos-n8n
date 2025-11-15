import streamlit as st
import requests
import os
import time

API = "http://localhost:8000"

def show():
    st.title("📄 Generar Reporte PDF con Gráficos")
    st.markdown("Genera un **reporte detallado** con estadísticas, gráficos y registros recientes de las URLs analizadas.")

    # 🎨 Estilo CSS global para botones pequeños y elegantes
    st.markdown("""
        <style>
        div.stButton > button, div.stDownloadButton > button {
            padding: 0.35rem 0.9rem;
            font-size: 0.9rem;
            border-radius: 8px;
            background-color: #0d6efd;
            color: white;
            border: none;
            transition: 0.25s;
        }
        div.stButton > button:hover, div.stDownloadButton > button:hover {
            background-color: #0b5ed7;
            transform: scale(1.03);
        }
        div.stButton, div.stDownloadButton { margin-bottom: 0.5rem; }
        </style>
    """, unsafe_allow_html=True)

    # ==============================================================
    # 🧾 Botón para generar el reporte PDF
    # ==============================================================
    if st.button("Generar Reporte PDF"):
        try:
            with st.spinner("Generando el reporte, por favor espera..."):
                res = requests.get(f"{API}/generate-report", timeout=90)
                if res.status_code == 200:
                    data = res.json()
                    pdf_path = data.get("pdf")

                    st.success("✅ Reporte generado correctamente")
                    st.info(f"Archivo: {pdf_path}")

                    # 📥 Botón de descarga pequeño
                    if os.path.exists(pdf_path):
                        with open(pdf_path, "rb") as f:
                            st.download_button(
                                label="⬇️ Descargar PDF",
                                data=f,
                                file_name=os.path.basename(pdf_path),
                                mime="application/pdf",
                                use_container_width=False  # ❗️ Más compacto
                            )
                else:
                    st.error(f"⚠️ Error {res.status_code}: {res.text}")

        except requests.exceptions.ConnectionError:
            st.error("❌ No se pudo conectar con el servidor FastAPI.")
        except Exception as e:
            st.error(f"❌ Error inesperado: {e}")
