import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ============================================================
# DASHBOARD GENERAL DEL ALMACÉN
# ============================================================
def mostrar_dashboard(db):
    st.title("📊 Panel de Estadísticas del Almacén")
    st.markdown("Visualización general de **productos**, **líneas** y **rendimiento del inventario**.")

    # ======================================================
    # Cargar datos
    # ======================================================
    productos = db.leer_productos() or []
    lineas = db.leer_lineas() or []

    if not productos:
        st.warning("No hay productos registrados aún.")
        return

    df = pd.DataFrame(productos)
    # Normaliza campos
    if "idLinea" not in df.columns and "id_linea" in df.columns:
        df["idLinea"] = df["id_linea"]

    # ======================================================
    # Sección: Métricas globales
    # ======================================================
    col1, col2, col3, col4 = st.columns(4)
    total_productos = len(df)
    total_stock = df["stock"].sum()
    valor_total = (df["stock"] * df["precio"]).sum()
    productos_bajo_stock = len(df[df["stock"] <= df["reorden"]])

    col1.metric("📦 Total de Productos", f"{total_productos}")
    col2.metric("📊 Stock Total", f"{total_stock}")
    col3.metric("💰 Valor Total del Inventario", f"S/ {valor_total:,.2f}")
    col4.metric("⚠️ Productos en Reorden", f"{productos_bajo_stock}")

    st.divider()

    # ======================================================
    # Sección: Estadísticas descriptivas
    # ======================================================
    st.subheader("📈 Estadísticas Descriptivas")
    stats = df[["precio", "stock", "reorden"]].describe().T
    stats["media"] = stats["mean"].round(2)
    stats["desviación estándar"] = stats["std"].round(2)
    stats = stats[["count", "min", "max", "media", "desviación estándar"]]
    stats.columns = ["N° datos", "Mínimo", "Máximo", "Media", "Desviación estándar"]
    st.dataframe(stats, use_container_width=True)

    st.divider()

    # ======================================================
    # Gráficos — Distribuciones y comparaciones
    # ======================================================

    # Stock por producto
    st.subheader("📦 Stock por Producto")
    fig_stock = px.bar(
        df,
        x="descripcion",
        y="stock",
        color="stock",
        color_continuous_scale="Bluered",
        title="Nivel de Stock de Cada Producto",
    )
    fig_stock.update_layout(xaxis_title="Producto", yaxis_title="Stock", template="plotly_white")
    st.plotly_chart(fig_stock, use_container_width=True)

    # Valor total por producto
    st.subheader("💰 Valor Económico por Producto")
    df["valor_total"] = df["precio"] * df["stock"]
    fig_valor = px.bar(
        df,
        x="descripcion",
        y="valor_total",
        color="valor_total",
        color_continuous_scale="Viridis",
        title="Valor Económico por Producto (Precio x Stock)",
    )
    fig_valor.update_layout(xaxis_title="Producto", yaxis_title="Valor (S/.)")
    st.plotly_chart(fig_valor, use_container_width=True)

    # Relación Precio vs Stock
    st.subheader("📊 Relación entre Precio y Stock")
    fig_dispersion = px.scatter(
        df,
        x="precio",
        y="stock",
        color="reorden",
        size="precio",
        hover_data=["descripcion"],
        title="Relación entre Precio y Stock (coloreado por nivel de reorden)",
        color_continuous_scale="Rainbow"
    )
    fig_dispersion.update_layout(xaxis_title="Precio (S/.)", yaxis_title="Stock disponible")
    st.plotly_chart(fig_dispersion, use_container_width=True)

    # ======================================================
    # Comparación entre líneas
    # ======================================================
    if lineas:
        st.subheader("🏷️ Comparativa entre Líneas de Producto")

        df_lineas = pd.DataFrame(lineas)
        # Unir productos con sus líneas
        merged = pd.merge(df, df_lineas, left_on="idLinea", right_on="idLinea", how="left")
        resumen_linea = (
            merged.groupby("descripcion_y")
            .agg(
                total_productos=("descripcion_x", "count"),
                stock_total=("stock", "sum"),
                valor_total=("valor_total", "sum"),
            )
            .reset_index()
            .rename(columns={"descripcion_y": "Línea"})
        )

        # Pie chart del total de stock por línea
        fig_pie = px.pie(
            resumen_linea,
            names="Línea",
            values="stock_total",
            color_discrete_sequence=px.colors.qualitative.Set3,
            title="Distribución del Stock por Línea de Producto"
        )
        st.plotly_chart(fig_pie, use_container_width=True)

        # Gráfico de barras comparativo
        fig_bar_lineas = px.bar(
            resumen_linea,
            x="Línea",
            y="valor_total",
            color="valor_total",
            color_continuous_scale="Turbo",
            title="Valor Económico Total por Línea de Producto",
        )
        st.plotly_chart(fig_bar_lineas, use_container_width=True)

    st.divider()

    # ======================================================
    # Evolución temporal
    # ======================================================
    if "created_at" in df.columns:
        st.subheader("🕒 Evolución de Registro de Productos")
        df["fecha"] = pd.to_datetime(df["created_at"]).dt.date
        conteo_fechas = df.groupby("fecha").size().reset_index(name="registros")
        fig_linea_tiempo = px.line(
            conteo_fechas,
            x="fecha",
            y="registros",
            markers=True,
            color_discrete_sequence=["#00CC96"],
            title="Evolución del Número de Productos Registrados",
        )
        st.plotly_chart(fig_linea_tiempo, use_container_width=True)

    # ======================================================
    # Dashboard resumen
    # ======================================================
    st.markdown("## 🧭 Dashboard General del Almacén")
    st.info("Resumen visual de métricas clave y comportamiento del inventario.")

    colA, colB = st.columns(2)

    with colA:
        fig_box = px.box(df, y="precio", points="all", color_discrete_sequence=["#FF6692"])
        fig_box.update_layout(title="Distribución de Precios", yaxis_title="Precio (S/.)")
        st.plotly_chart(fig_box, use_container_width=True)

    with colB:
        fig_hist = px.histogram(
            df,
            x="stock",
            nbins=10,
            color_discrete_sequence=["#636EFA"],
            title="Distribución del Stock por Producto"
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    st.caption("📊 Todos los gráficos son interactivos: pasa el mouse o selecciona rangos para explorar.")
