import os
import requests
import streamlit as st

class N8NClient:
    def __init__(self):
        """
        Inicializa las URLs de los webhooks desde variables de entorno o secrets.toml
        """
        self.alerts_webhook = os.getenv("N8N_ALERTS_WEBHOOK") or st.secrets.get("N8N_ALERTS_WEBHOOK")
        self.reports_webhook = os.getenv("N8N_REPORTS_WEBHOOK") or st.secrets.get("N8N_REPORTS_WEBHOOK")
        self.create_product_webhook = os.getenv("N8N_CREATE_PRODUCT_WEBHOOK") or st.secrets.get("N8N_CREATE_PRODUCT_WEBHOOK")
        self.create_linea_webhook = os.getenv("N8N_CREATE_LINEA_WEBHOOK") or st.secrets.get("N8N_CREATE_LINEA_WEBHOOK")
        self.update_linea_webhook = os.getenv("N8N_UPDATE_LINEA_WEBHOOK") or st.secrets.get("N8N_UPDATE_LINEA_WEBHOOK")
        self.delete_linea_webhook = os.getenv("N8N_DELETE_LINEA_WEBHOOK") or st.secrets.get("N8N_DELETE_LINEA_WEBHOOK")
        self.update_product_webhook = os.getenv("N8N_UPDATE_PRODUCT_WEBHOOK") or st.secrets.get("N8N_UPDATE_PRODUCT_WEBHOOK")
        self.delete_product_webhook = os.getenv("N8N_DELETE_PRODUCT_WEBHOOK") or st.secrets.get("N8N_DELETE_PRODUCT_WEBHOOK")

    # ===================================================
    # 🧩 1. CREAR PRODUCTO
    # ===================================================
    def crear_producto(self, data: dict):
        if not self.create_product_webhook:
            return {"ok": False, "error": "Webhook de creación de producto no configurado."}
        try:
            response = requests.post(self.create_product_webhook, json=data, timeout=15)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # ===================================================
    # ✏️ 2. ACTUALIZAR PRODUCTO - MÉTODO FALTANTE
    # ===================================================
    def actualizar_producto(self, data: dict):
        """
        Envía los datos de actualización del producto al webhook de n8n
        """
        if not self.update_product_webhook:
            return {"ok": False, "error": "Webhook de actualización de producto no configurado."}
        try:
            response = requests.post(self.update_product_webhook, json=data, timeout=10)
            response.raise_for_status()
            return {"ok": response.status_code == 200, "data": response.json() if response.ok else None}
        except Exception as e:
            return {"ok": False, "error": str(e)}


    # ===================================================
    # 🗑️ 3. ELIMINAR PRODUCTO
    # ===================================================
    def eliminar_producto(self, data: dict):
        if not self.delete_product_webhook:
            return {"ok": False, "error": "Webhook de eliminación de producto no configurado."}
        try:
            response = requests.post(self.delete_product_webhook, json=data, timeout=10)
            response.raise_for_status()
            return {"ok": response.status_code == 200, "data": response.json() if response.ok else None}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # ===================================================
    # 🏷️ 4. CREAR LÍNEA
    # ===================================================
    def crear_linea(self, data: dict):
        if not self.create_linea_webhook:
            return {"ok": False, "error": "Webhook de creación de línea no configurado."}
        try:
            response = requests.post(self.create_linea_webhook, json=data, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # ===================================================
    # ✏️ 5. ACTUALIZAR LÍNEA
    # ===================================================
    def actualizar_linea(self, data: dict):
        if not self.update_linea_webhook:
            return {"ok": False, "error": "Webhook de actualización de línea no configurado."}
        try:
            response = requests.post(self.update_linea_webhook, json=data, timeout=10)
            response.raise_for_status()
            return {"ok": response.status_code == 200, "data": response.json() if response.ok else None}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # ===================================================
    # 🗑️ 6. ELIMINAR LÍNEA
    # ===================================================
    def eliminar_linea(self, data: dict):
        if not self.delete_linea_webhook:
            return {"ok": False, "error": "Webhook de eliminación de línea no configurado."}
        try:
            response = requests.post(self.delete_linea_webhook, json=data, timeout=10)
            response.raise_for_status()
            return {"ok": response.status_code == 200, "data": response.json() if response.ok else None}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # ===================================================
    # 🚨 7. ENVIAR ALERTAS
    # ===================================================
    def enviar_alerta(self, payload: dict):
        if not self.alerts_webhook:
            return {"ok": False, "error": "Webhook de alertas no configurado."}
        try:
            response = requests.post(self.alerts_webhook, json=payload, timeout=15)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # ===================================================
    # 🧾 8. GENERAR REPORTES
    # ===================================================
    def generar_reporte(self, payload: dict):
        if not self.reports_webhook:
            return {"ok": False, "error": "Webhook de reportes no configurado."}
        try:
            response = requests.post(self.reports_webhook, json=payload, timeout=25)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"ok": False, "error": str(e)}