import streamlit as st
import pandas as pd
import time  # <-- Agrega esta importación

# =====================================================
# CREAR PRODUCTO (con verificación de duplicados)
# =====================================================
def crear_producto(db, n8n):
    st.subheader("➕ Crear Producto")
    
    # Obtener líneas disponibles
    lineas = db.leer_lineas() or []
    opciones_lineas = {l["descripcion"]: l.get("idLinea", l.get("id_linea")) for l in lineas}
    
    descripcion = st.text_input("Descripción del producto").strip()
    precio = st.number_input("Precio (S/.)", min_value=0.0, step=0.1)
    stock = st.number_input("Stock inicial", min_value=0, step=1)
    reorden = st.number_input("Punto de reorden", min_value=0, step=1)
    
    linea_seleccionada = None
    if opciones_lineas:
        linea_nombre = st.selectbox("Línea", ["Sin línea"] + list(opciones_lineas.keys()))
        if linea_nombre != "Sin línea":
            linea_seleccionada = opciones_lineas[linea_nombre]

    if st.button("Guardar"):
        if not descripcion:
            st.error("❌ La descripción no puede estar vacía.")
            return

        # Verificar duplicados
        productos = db.leer_productos() or []
        duplicado = any(
            p.get("descripcion", "").strip().lower() == descripcion.lower()
            for p in productos
        )
        if duplicado:
            st.warning(f"⚠️ Ya existe un producto con la descripción '{descripcion}'.")
            return

        # Registrar nuevo producto
        data = {
            "descripcion": descripcion,
            "precio": precio,
            "stock": stock,
            "reorden": reorden,
            "idLinea": linea_seleccionada
        }
        resultado = n8n.crear_producto(data)

        if resultado.get("ok"):
            st.success(f"✅ Producto '{descripcion}' registrado correctamente (vía webhook).")
            time.sleep(2)
            st.rerun()
        else:
            st.error(f"❌ Error al registrar producto: {resultado.get('error')}")

# =====================================================
# LEER PRODUCTOS (tabla traducida al español)
# =====================================================
def leer_productos(db):
    st.subheader("📖 Productos Registrados")
    productos = db.leer_productos()

    if productos:
        df = pd.DataFrame(productos)
        
        # Renombrar columnas para mejor presentación
        column_mapping = {
            'codigo': 'Código',
            'descripcion': 'Descripción',
            'precio': 'Precio (S/.)',
            'stock': 'Stock',
            'reorden': 'Reorden',
            'idLinea': 'ID Línea'
        }
        df = df.rename(columns=column_mapping)
        
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No hay productos registrados.")

# =====================================================
# ACTUALIZAR PRODUCTO (vía webhook)
# =====================================================
def actualizar_producto(db, n8n):
    st.subheader("✏️ Actualizar Producto")

    productos = db.leer_productos()
    if not productos:
        st.warning("No hay productos disponibles.")
        return

    opciones = {f"{p['codigo']} - {p['descripcion']}": p for p in productos}
    seleccion = st.selectbox("Selecciona un producto:", list(opciones.keys()))
    prod = opciones[seleccion]

    nueva_desc = st.text_input("Nueva descripción", value=prod["descripcion"]).strip()
    nuevo_stock = st.number_input("Nuevo stock", value=prod["stock"])
    nuevo_precio = st.number_input("Nuevo precio (S/.)", value=float(prod["precio"]))
    nuevo_reorden = st.number_input("Nuevo punto de reorden", value=prod["reorden"])

    if st.button("Actualizar"):
        data = {
            "codigo": prod["codigo"],
            "descripcion": nueva_desc,
            "stock": nuevo_stock,
            "precio": nuevo_precio,
            "reorden": nuevo_reorden,
        }
        resultado = n8n.actualizar_producto(data)

        if resultado.get("ok"):
            st.success("✅ Producto actualizado correctamente (vía webhook).")
            time.sleep(2)
            st.rerun()
        else:
            st.error(f"❌ Error al actualizar producto: {resultado.get('error')}")

# =====================================================
# ELIMINAR PRODUCTO (vía webhook, con reinicio limpio)
# =====================================================
def eliminar_producto(db, n8n):
    st.subheader("🗑️ Eliminar Producto")

    # Estado temporal para limpiar tras eliminar
    if "producto_eliminado" not in st.session_state:
        st.session_state.producto_eliminado = False

    productos = db.leer_productos()
    if not productos:
        st.warning("No hay productos disponibles.")
        return

    # Opciones del selectbox
    opciones = {f"{p['codigo']} - {p['descripcion']}": p for p in productos}
    seleccion = st.selectbox("Selecciona un producto:", list(opciones.keys()), key="producto_select")
    prod = opciones[seleccion]

    if st.button("Eliminar permanentemente"):
        data = {"codigo": prod["codigo"]}
        resultado = n8n.eliminar_producto(data)

        if resultado.get("ok"):
            st.session_state.producto_eliminado = True
            st.success(f"🗑️ Producto '{prod['descripcion']}' eliminado correctamente (vía webhook).")
            time.sleep(2)
            st.session_state.producto_select = None  # Limpia selección
            st.rerun()
        else:
            st.error(f"❌ Error al eliminar producto: {resultado.get('error')}")

    # Mostrar mensaje breve tras reinicio
    if st.session_state.producto_eliminado:
        st.info("✅ La lista se ha actualizado después de eliminar el producto.")
        st.session_state.producto_eliminado = False
