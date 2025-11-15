from supabase import create_client
import bcrypt
import os
from dotenv import load_dotenv

# Cargar variables de entorno (.env)
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

usuarios = [
    ("admin", "Administrador", "General", "admin@zai.com", "admin123", "administrador"),
    ("supervisor", "Carlos", "Ramos", "supervisor@zai.com", "supervisor123", "supervisor"),
    ("seguridad", "María", "Fernández", "seguridad@zai.com", "seguridad123", "gerente_seguridad"),
]

for username, nombre, apellido, email, contrasena, rol in usuarios:
    contrasena_hash = bcrypt.hashpw(contrasena.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    supabase.table("usuarios_sistema").insert({
        "nombre_usuario": username,
        "nombre": nombre,
        "apellido": apellido,
        "email": email,
        "contrasena_hash": contrasena_hash,
        "rol": rol
    }).execute()
    print(f"✅ Usuario {username} creado correctamente.")
