import streamlit as st
import pandas as pd
import time

# =====================================================
# 🚨 ENVIAR ALERTAS DE STOCK BAJO (vía webhook Gmail)
# =====================================================
def disparar_alertas(db, n8n):
    st.subheader("🚨 Enviar Alertas de Stock Bajo")

    # Obtener productos
    productos = db.leer_productos()
    if not productos:
        st.warning("⚠️ No hay productos registrados.")
        return

    # Filtrar los de bajo stock
    bajos = [p for p in productos if p["stock"] <= p["reorden"]]
    if not bajos:
        st.success("🎉 Todos los productos tienen stock suficiente.")
        return

    st.markdown("### 📉 Productos con stock bajo")
    df = pd.DataFrame(bajos)
    traducciones = {
        "codigo": "Código",
        "descripcion": "Descripción",
        "stock": "Stock Actual",
        "reorden": "Punto de Reorden",
        "idLinea": "Línea Asociada",
    }
    df = df.rename(columns={k: v for k, v in traducciones.items() if k in df.columns})
    st.dataframe(df, use_container_width=True)

    # Seleccionar canal (solo email por ahora)
    st.markdown("### ✉️ Configuración de Alerta")
    canal = "email"  # solo email
    destinatario = st.text_input("Correo electrónico del destinatario", "ejemplo@gmail.com")

    # Botón de envío
    if st.button("Enviar alerta por correo"):
        if not destinatario or "@" not in destinatario:
            st.error("❌ Ingrese un correo electrónico válido.")
            return

        # Construir payload
        payload = {
            "canales": [canal],
            "destinatarios": [destinatario.strip()],
            "items": bajos,
        }

        # Enviar vía webhook n8n
        st.info("📤 Enviando alerta, por favor espere...")
        resultado = n8n.enviar_alerta(payload)

        if resultado.get("ok"):
            st.success(f"✅ Alerta enviada correctamente a {destinatario}.")
            time.sleep(2)
            st.rerun()
        else:
            st.error(f"❌ Error al enviar la alerta: {resultado.get('error')}")
