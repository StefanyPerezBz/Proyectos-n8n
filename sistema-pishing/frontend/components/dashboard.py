import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import numpy as np

API = "http://localhost:8000"

def show():
    st.title("📊 Dashboard Avanzado de Seguridad y Detección de Phishing")
    st.markdown("""
    Bienvenido al panel de **inteligencia de seguridad** del sistema de detección de sitios fraudulentos.  
    Aquí podrás explorar tendencias, métricas y análisis visuales para comprender mejor el comportamiento de URLs maliciosas.
    """)

    # ==========================================================
    # Conexión con la API
    # ==========================================================
    try:
        stats = requests.get(f"{API}/statistics", timeout=15).json()
    except Exception as e:
        st.error(f"❌ Error al conectar con el servidor: {e}")
        return

    # ==========================================================
    # PALETA GLOBAL
    # ==========================================================
    color_map = {
        "Fraudulentos": "#e74c3c",  # rojo
        "Sospechosos": "#f39c12",   # ámbar
        "Legítimos": "#27ae60"      # verde
    }
    line_colors = {
        "Fraudulento": "#e74c3c",
        "Sospechoso": "#f39c12",
        "Legítimo": "#27ae60"
    }

    # ==========================================================
    # MÉTRICAS PRINCIPALES
    # ==========================================================
    st.markdown("### 📈 Resumen General")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total analizado", stats.get("total", 0))
    col2.metric("Fraudulentos", stats.get("phishing", 0))
    col3.metric("Sospechosos", stats.get("suspicious", 0))
    col4.metric("Legítimos", stats.get("legitimate", 0))

    total = max(stats.get("total", 1), 1)
    phishing_pct = (stats.get("phishing", 0) / total) * 100
    suspicious_pct = (stats.get("suspicious", 0) / total) * 100
    legit_pct = (stats.get("legitimate", 0) / total) * 100

    st.markdown(f"""
    **Distribución porcentual actual:**
    - 🔴 **Fraudulentos:** {phishing_pct:.1f} %
    - 🟠 **Sospechosos:** {suspicious_pct:.1f} %
    - 🟢 **Legítimos:** {legit_pct:.1f} %
    """)

    st.divider()

    # ==========================================================
    # DISTRIBUCIÓN GENERAL
    # ==========================================================
    st.subheader("🥧 Distribución General de Análisis")

    df_dist = pd.DataFrame({
        "Categoría": ["Fraudulentos", "Sospechosos", "Legítimos"],
        "Cantidad": [stats["phishing"], stats["suspicious"], stats["legitimate"]]
    })

    fig_pie = px.pie(
        df_dist,
        names="Categoría",
        values="Cantidad",
        color="Categoría",
        color_discrete_map=color_map,
        hole=0.35
    )
    fig_pie.update_traces(
        textinfo="percent+label",
        pull=[0.05, 0.05, 0.05],
        marker=dict(line=dict(color="#fff", width=2))
    )
    st.plotly_chart(fig_pie, use_container_width=True)

    # ==========================================================
    # COMPARACIÓN DE CATEGORÍAS
    # ==========================================================
    st.subheader("📊 Comparación entre Categorías")

    fig_bar = px.bar(
        df_dist,
        x="Categoría",
        y="Cantidad",
        color="Categoría",
        text_auto=True,
        color_discrete_map=color_map,
        title="Número de URLs por categoría"
    )
    fig_bar.update_traces(marker_line_color="#2f2f2f", marker_line_width=1.2)
    st.plotly_chart(fig_bar, use_container_width=True)

    # ==========================================================
    # NUEVO: BARRAS HORIZONTALES
    # ==========================================================
    st.subheader("📏 Proporciones visuales (comparación directa)")

    fig_hbar = px.bar(
        df_dist.sort_values("Cantidad", ascending=True),
        y="Categoría",
        x="Cantidad",
        orientation="h",
        text_auto=True,
        color="Categoría",
        color_discrete_map=color_map
    )
    fig_hbar.update_layout(title="Distribución horizontal por tipo de sitio")
    st.plotly_chart(fig_hbar, use_container_width=True)

    # ==========================================================
    # NUEVO: GAUGE — PORCENTAJE DE LEGITIMIDAD
    # ==========================================================
    st.subheader("🧭 Nivel general de legitimidad del sistema")

    legit_score = round((stats.get("legitimate", 0) / total) * 100, 1)
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=legit_score,
        title={'text': "Porcentaje de URLs legítimas"},
        delta={'reference': 50, 'increasing': {'color': "#27ae60"}},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "#27ae60"},
            'steps': [
                {'range': [0, 30], 'color': "#e74c3c"},
                {'range': [30, 60], 'color': "#f39c12"},
                {'range': [60, 100], 'color': "#27ae60"}
            ],
            'threshold': {'line': {'color': "black", 'width': 3}, 'thickness': 0.8, 'value': legit_score}
        }
    ))
    st.plotly_chart(fig_gauge, use_container_width=True)

    # ==========================================================
    # TENDENCIAS TEMPORALES
    # ==========================================================
    st.subheader("📅 Tendencia temporal de detecciones")

    recent = stats.get("recent_activity", [])
    if recent:
        df_recent = pd.DataFrame(recent)
        df_recent["created_at"] = pd.to_datetime(df_recent["created_at"], errors="coerce")
        df_recent = df_recent.dropna(subset=["created_at"])
        df_recent["prediction"] = df_recent["prediction"].map({
            "PHISHING": "Fraudulento",
            "SUSPICIOUS": "Sospechoso",
            "LEGITIMATE": "Legítimo"
        })

        df_recent["Fecha"] = df_recent["created_at"].dt.date
        trend = df_recent.groupby("Fecha")["prediction"].value_counts().unstack(fill_value=0).reset_index()

        fig_trend = go.Figure()
        for col in [c for c in trend.columns if c != "Fecha"]:
            fig_trend.add_trace(go.Scatter(
                x=trend["Fecha"],
                y=trend[col],
                mode="lines+markers",
                name=col,
                line=dict(width=3, color=line_colors.get(col, "#888")),
                marker=dict(size=7)
            ))
        fig_trend.update_layout(
            title="Evolución diaria de detecciones",
            xaxis_title="Fecha",
            yaxis_title="Cantidad",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_trend, use_container_width=True)

        # ======================================================
        # NUEVO: MAPA DE CALOR — ACTIVIDAD POR DÍA / HORA
        # ======================================================
        st.subheader("🔥 Mapa de calor de actividad (por hora del día)")
        df_recent["Hora"] = df_recent["created_at"].dt.hour
        heatmap = df_recent.groupby(["Fecha", "Hora"]).size().reset_index(name="Conteo")

        pivot = heatmap.pivot(index="Hora", columns="Fecha", values="Conteo").fillna(0)
        fig_heatmap = px.imshow(
            pivot,
            color_continuous_scale=["#fef0d9", "#fdcc8a", "#fc8d59", "#e34a33", "#b30000"],
            labels=dict(x="Fecha", y="Hora del día", color="Detecciones"),
            title="Frecuencia de análisis por hora y fecha"
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)
    else:
        st.info("ℹ️ No hay actividad reciente disponible.")

    # ==========================================================
    # ESTADÍSTICAS DESCRIPTIVAS
    # ==========================================================
    st.subheader("📋 Estadísticas descriptivas de las detecciones")

    try:
        df_stats = pd.DataFrame({
            "Categoría": ["Fraudulentos", "Sospechosos", "Legítimos"],
            "Cantidad": [stats["phishing"], stats["suspicious"], stats["legitimate"]]
        })
        desc = df_stats["Cantidad"].describe().to_frame().T.rename(index={"Cantidad": "Estadísticas"})
        desc = desc.rename(columns={
            "count": "N° categorías", "mean": "Promedio", "std": "Desv. estándar",
            "min": "Mínimo", "25%": "Cuartil 25%", "50%": "Mediana", "75%": "Cuartil 75%", "max": "Máximo"
        })
        st.dataframe(desc, use_container_width=True)
    except Exception:
        st.warning("⚠️ No se pudieron generar estadísticas descriptivas.")
