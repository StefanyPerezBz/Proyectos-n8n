import streamlit as st
import requests
import base64

def generar_reportes(db, n8n):
    st.subheader("🧾 Reportes Automáticos")

    tipo = st.selectbox(
        "Selecciona tipo de reporte",
        ["Inventario", "Bajo stock", "Valorizado"]
    )

    if st.button("Generar PDF"):
        st.info("⏳ Generando reporte, por favor espere...")

        try:
            # Llamar directamente al webhook de n8n
            response = requests.post(
                n8n.reports_webhook,
                json={"report_type": tipo.lower()},
                timeout=30
            )

            # Verificar si la respuesta fue un PDF binario
            if (
                response.status_code == 200 and
                "application/pdf" in response.headers.get("Content-Type", "")
            ):
                pdf_bytes = response.content

                # ✅ Mostrar mensaje y opciones
                st.success("✅ Reporte generado correctamente.")

                # 📥 Botón de descarga
                st.download_button(
                    label="📄 Descargar PDF",
                    data=pdf_bytes,
                    file_name=f"reporte_{tipo.lower()}.pdf",
                    mime="application/pdf"
                )

                # 👁️ Vista previa en línea
                pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")
                st.markdown("### 👁️ Vista previa del PDF")
                st.markdown(
                    f'<iframe src="data:application/pdf;base64,{pdf_base64}" width="100%" height="600px"></iframe>',
                    unsafe_allow_html=True
                )

            else:
                st.error(f"❌ Error: respuesta inesperada del webhook. Código: {response.status_code}")
                st.text(response.text)

        except Exception as e:
            st.error(f"⚠️ Error al generar el reporte: {e}")
