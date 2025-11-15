import streamlit as st
from components import dashboard, single_analysis, batch_analysis, reports

st.set_page_config(page_title="🛡️ Detección de Phishing", layout="wide")
st.sidebar.image("assets/logo.png")
menu = st.sidebar.radio("Navegación", ["Dashboard","Analizar URL","Analizar CSV","Reportes"])

if menu == "Dashboard":
    dashboard.show()
elif menu == "Analizar URL":
    single_analysis.show()
elif menu == "Analizar CSV":
    batch_analysis.show()
else:
    reports.show()
