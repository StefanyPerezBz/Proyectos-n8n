import os
from supabase import create_client, Client
import streamlit as st

class SupabaseClient:
    def __init__(self):
        url = os.getenv("SUPABASE_URL") or st.secrets["SUPABASE_URL"]
        key = os.getenv("SUPABASE_KEY") or st.secrets["SUPABASE_KEY"]
        self.client: Client = create_client(url, key)

    # ---------------- PRODUCTOS ----------------
    def crear_producto(self, data):
        return self.client.table("producto").insert(data).execute()

    def leer_productos(self):
        return self.client.table("producto").select("*").execute().data

    def actualizar_producto(self, codigo, data):
        return self.client.table("producto").update(data).eq("codigo", codigo).execute()

    def eliminar_producto(self, codigo):
        return self.client.table("producto").delete().eq("codigo", codigo).execute()

    # ---------------- LÍNEAS ----------------
    def crear_linea(self, data):
        return self.client.table("linea").insert(data).execute()

    def leer_lineas(self):
        return self.client.table("linea").select("*").execute().data

    def actualizar_linea(self, id_linea, data):
        return self.client.table("linea").update(data).eq("idLinea", id_linea).execute()

    def eliminar_linea(self, id_linea):
        return self.client.table("linea").delete().eq("idLinea", id_linea).execute()
