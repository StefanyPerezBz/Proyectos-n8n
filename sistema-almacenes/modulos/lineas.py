import streamlit as st
import pandas as pd

# =====================================================
# CREAR LÍNEA (con verificación de duplicados)
# =====================================================
def crear_linea(db, n8n):
    st.subheader("➕ Crear Línea")
    descripcion = st.text_input("Descripción de la línea").strip()

    if st.button("Guardar"):
        if not descripcion:
            st.error("❌ La descripción no puede estar vacía.")
            return

        # Leer líneas existentes
        lineas = db.leer_lineas() or []

        # Verificar si ya existe una línea con esa descripción
        duplicado = any(
            l.get("descripcion", "").strip().lower() == descripcion.lower()
            for l in lineas
        )
        if duplicado:
            st.warning(f"⚠️ Ya existe una línea con la descripción '{descripcion}'.")
            return

        # Registrar nueva línea vía webhook
        data = {"descripcion": descripcion}
        resultado = n8n.crear_linea(data)

        if resultado.get("ok"):
            st.success(f"✅ Línea '{descripcion}' registrada correctamente (vía webhook).")
        else:
            st.error(f"❌ Error al registrar línea: {resultado.get('error')}")


# =====================================================
# LEER LÍNEAS (tabla traducida al español)
# =====================================================
def leer_lineas(db):
    st.subheader("📖 Líneas Registradas")
    lineas = db.leer_lineas()

    if lineas:
        df = pd.DataFrame(lineas)
        if "idLinea" in df.columns:
            df = df.rename(columns={"idLinea": "ID de Línea", "descripcion": "Descripción"})
        elif "id_linea" in df.columns:
            df = df.rename(columns={"id_linea": "ID de Línea", "descripcion": "Descripción"})
        else:
            df.columns = ["ID de Línea" if "id" in c.lower() else "Descripción" for c in df.columns]
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No hay líneas registradas.")


# =====================================================
# ACTUALIZAR LÍNEA (vía webhook)
# =====================================================
def actualizar_linea(db, n8n):
    st.subheader("✏️ Actualizar Línea")
    lineas = db.leer_lineas()
    if not lineas:
        st.warning("No hay líneas disponibles.")
        return

    # Normaliza la clave de ID
    opciones = {
        f"{l.get('idLinea', l.get('id_linea'))} - {l['descripcion']}": l
        for l in lineas
    }
    seleccion = st.selectbox("Selecciona una línea:", list(opciones.keys()))
    linea = opciones[seleccion]

    id_linea = linea.get("idLinea", linea.get("id_linea"))
    nueva_desc = st.text_input("Nueva descripción", value=linea["descripcion"]).strip()

    if st.button("Actualizar"):
        # Verificar duplicados
        duplicado = any(
            l.get("descripcion", "").strip().lower() == nueva_desc.lower()
            and l.get("idLinea", l.get("id_linea")) != id_linea
            for l in lineas
        )
        if duplicado:
            st.warning(f"⚠️ Ya existe una línea con la descripción '{nueva_desc}'.")
            return

        # Enviar actualización vía webhook de n8n
        data = {"idLinea": id_linea, "descripcion": nueva_desc}
        resultado = n8n.actualizar_linea(data)

        if resultado.get("ok"):
            st.success(f"✅ Línea actualizada correctamente (vía webhook).")
        else:
            st.error(f"❌ Error al actualizar línea: {resultado.get('error')}")


import streamlit as st
import pandas as pd
import time

# =====================================================
# ELIMINAR LÍNEA (vía webhook)
# =====================================================
def eliminar_linea(db, n8n):
    st.subheader("🗑️ Eliminar Línea")

    lineas = db.leer_lineas()
    if not lineas:
        st.warning("No hay líneas disponibles.")
        return

    opciones = {
        f"{l.get('idLinea', l.get('id_linea'))} - {l['descripcion']}": l
        for l in lineas
    }
    seleccion = st.selectbox("Selecciona una línea:", list(opciones.keys()))
    linea = opciones[seleccion]
    id_linea = linea.get("idLinea", linea.get("id_linea"))

    if st.button("Eliminar permanentemente"):
        data = {"idLinea": id_linea}
        resultado = n8n.eliminar_linea(data)

        if resultado.get("ok"):
            st.success(f"🗑️ Línea '{linea['descripcion']}' eliminada correctamente (vía webhook).")
            time.sleep(2)  # Espera 2 segundos para mostrar el mensaje
            st.rerun()  # Recarga la página para actualizar la lista
        else:
            st.error(f"❌ Error al eliminar línea: {resultado.get('error')}")
