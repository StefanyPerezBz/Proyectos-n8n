from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from supabase import create_client, Client
from typing import List, Dict, Any
from datetime import datetime
import pandas as pd
import hashlib, os, uuid, logging, requests, re, math, socket
from urllib.parse import urlparse
from weasyprint import HTML 

# ==========================================================
# ⚙️ CONFIGURACIÓN DEL SISTEMA
# ==========================================================
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://dzjamsbehsubgamikryp.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR6amFtc2JlaHN1YmdhbWlrcnlwIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTE3MzkyMywiZXhwIjoyMDc0NzQ5OTIzfQ.6-rXL1utK-FqaXwWj5duwYIoIO0mQAzOiOI_P2D0ao0")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(title="Phishing Detection API", version="3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# ==========================================================
# 🔍 CLASE PHISHING ANALYZER (integrada)
# ==========================================================
class PhishingAnalyzer:
    """Analizador heurístico + validación real HTTP/DNS."""

    @staticmethod
    def extract_features(url: str) -> Dict[str, Any]:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        path = parsed.path.lower()

        suspicious_words = [
            "login","verify","account","update","bank","secure",
            "password","signin","support","billing","security",
            "paypal","credential","reset"
        ]

        url_length = len(url)
        num_dots = url.count(".")
        num_hyphens = url.count("-")
        num_slashes = url.count("/")
        has_at = "@" in url
        has_ip = bool(re.match(r"^(?:http[s]?://)?\d{1,3}(?:\.\d{1,3}){3}", url))
        has_https = url.lower().startswith("https")
        num_params = url.count("=")
        suspicious_word_hits = sum(1 for w in suspicious_words if w in url.lower())

        shorteners = [
            "bit.ly","tinyurl","t.co","goo.gl","is.gd",
            "ow.ly","buff.ly","shorturl","rebrand.ly"
        ]
        uses_shortener = any(s in domain for s in shorteners)

        # Cálculo de entropía
        entropy = 0
        if len(domain) > 0:
            freq = {c: domain.count(c) / len(domain) for c in set(domain)}
            entropy = -sum(p * math.log2(p) for p in freq.values())

        subdomains = domain.split(".")
        num_subdomains = len(subdomains) - 2 if len(subdomains) > 2 else 0

        return {
            "url_length": url_length,
            "num_dots": num_dots,
            "num_hyphens": num_hyphens,
            "num_slashes": num_slashes,
            "has_at": has_at,
            "has_ip": has_ip,
            "has_https": has_https,
            "num_params": num_params,
            "suspicious_word_hits": suspicious_word_hits,
            "uses_shortener": uses_shortener,
            "entropy": round(entropy, 2),
            "num_subdomains": num_subdomains,
            "domain": domain,
            "path": path,
        }

    @staticmethod
    def domain_exists(domain: str) -> bool:
        """Verifica si el dominio resuelve DNS."""
        try:
            socket.gethostbyname(domain)
            return True
        except Exception:
            return False

    @staticmethod
    def url_reachable(url: str) -> tuple[bool, int]:
        """Comprueba si la URL responde HTTP."""
        try:
            resp = requests.head(url, timeout=4, allow_redirects=True)
            if resp.status_code >= 400 or resp.status_code == 0:
                resp = requests.get(url, timeout=4, allow_redirects=True)
            return resp.status_code < 400, resp.status_code
        except Exception:
            return False, 0

    @staticmethod
    def calculate_score(f: Dict[str, Any], reachable: bool) -> float:
        score = 0.0
        if f["url_length"] > 75:
            score += 0.1
        if f["url_length"] > 100:
            score += 0.15

        score += min(f["num_dots"] * 0.05, 0.15)
        score += min(f["num_hyphens"] * 0.05, 0.15)
        score += 0.1 if f["has_at"] else 0
        score += 0.15 if f["has_ip"] else 0
        score += 0.1 if f["uses_shortener"] else 0
        score += min(f["suspicious_word_hits"] * 0.08, 0.25)
        score += min(f["num_subdomains"] * 0.05, 0.15)
        score -= 0.05 if f["has_https"] else 0

        if not reachable:
            score += 0.1
        if f["entropy"] > 3.5:
            score += 0.1
        if f["entropy"] > 4:
            score += 0.15

        return min(max(score, 0), 1.0)

    @staticmethod
    def analyze_url(url: str) -> Dict[str, Any]:
        f = PhishingAnalyzer.extract_features(url)
        domain_ok = PhishingAnalyzer.domain_exists(f["domain"])
        reachable, status_code = PhishingAnalyzer.url_reachable(url)
        score = PhishingAnalyzer.calculate_score(f, reachable)

        if not domain_ok:
            score += 0.2
            f["domain_status"] = "NOT_FOUND"
        else:
            f["domain_status"] = "ACTIVE"

        f["reachable"] = reachable
        f["http_status"] = status_code

        score = min(score, 1.0)

        if score >= 0.85:
            pred, risk = "PHISHING", "HIGH"
        elif score >= 0.6:
            pred, risk = "SUSPICIOUS", "MEDIUM"
        else:
            pred, risk = "LEGITIMATE", "LOW"

        return {
            "url": url,
            "prediction": pred,
            "risk_level": risk,
            "probability": round(score, 2),
            "confidence": "HIGH" if score > 0.9 or score < 0.1 else "MEDIUM",
            "features": f,
        }

# ==========================================================
# 📦 MODELOS FASTAPI
# ==========================================================
class URLRequest(BaseModel):
    url: str
    created_by: str

class BatchAnalysisRequest(BaseModel):
    urls: List[str]
    created_by: str

# ==========================================================
# 🚀 ENDPOINT: ANALIZAR Y REGISTRAR URL
# ==========================================================
@app.post("/analyze")
async def analyze_url(req: URLRequest):
    """
    Analiza cualquier URL (aunque no responda) y la registra en Supabase o n8n.
    """
    try:
        result = PhishingAnalyzer.analyze_url(req.url)

        payload = {
            "url": req.url,
            "created_by": req.created_by,
            "prediction": result["prediction"],
            "risk_level": result["risk_level"],
            "probability": result["probability"],
            "confidence": result["confidence"],
            "reachable": result["features"]["reachable"],
            "http_status": result["features"]["http_status"],
            "domain_status": result["features"]["domain_status"],
            "analysis_result": result,
        }

        try:
            n8n_url = os.getenv("N8N_CREATE_WEBHOOK", "http://localhost:5678/webhook/create-url")
            requests.post(n8n_url, json=payload, timeout=10)
        except Exception:
            supabase.table("url_analysis").insert(payload).execute()

        return {"status": "ok", "data": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analizando URL: {str(e)}")

# ==========================================================
# 📑 ANALIZAR VARIAS URLs (BATCH)
# ==========================================================
@app.post("/analyze-batch")
async def analyze_batch(req: BatchAnalysisRequest):
    results = []
    for url in req.urls:
        try:
            result = PhishingAnalyzer.analyze_url(url)
            supabase.table("url_analysis").insert({
                "url": url,
                "url_hash": hashlib.sha256(url.encode()).hexdigest(),
                "analysis_result": result,
                "risk_level": result["risk_level"],
                "prediction": result["prediction"],
                "probability": result["probability"],
                "created_by": req.created_by
            }).execute()
            results.append({"url": url, "prediction": result["prediction"], "risk": result["risk_level"]})
        except Exception as e:
            results.append({"url": url, "error": str(e)})
    return {"total": len(results), "results": results}

# ==========================================================
# 📂 ANALIZAR CSV (vía n8n)
# ==========================================================
@app.post("/analyze-csv")
async def analyze_csv(file: UploadFile = File(...), created_by: str = "system"):
    """
    Recibe un CSV con columna 'url' y envía cada análisis a n8n para registro.
    """
    try:
        content = await file.read()
        df = pd.read_csv(pd.io.common.BytesIO(content))
        if "url" not in df.columns:
            raise HTTPException(400, "El archivo debe contener una columna 'url'")

        n8n_url = os.getenv("N8N_CSV_WEBHOOK", "http://localhost:5678/webhook/csv-batch")

        urls = df["url"].tolist()
        analyzed = []

        for url in urls:
            result = PhishingAnalyzer.analyze_url(url)
            payload = {
                "url": url,
                "created_by": created_by,
                "prediction": result["prediction"],
                "risk_level": result["risk_level"],
                "probability": result["probability"],
                "confidence": result["confidence"],
                "analysis_result": result
            }

            try:
                # Enviar cada resultado a n8n
                requests.post(n8n_url, json=payload, timeout=10)
            except Exception as e:
                logging.warning(f"⚠️ No se pudo enviar {url} a n8n: {e}")

            analyzed.append(result)

        return {
            "status": "ok",
            "total_analyzed": len(analyzed),
            "message": f"{len(analyzed)} URLs enviadas a n8n correctamente"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando CSV: {e}")

# ==========================================================
# 📊 ESTADÍSTICAS
# ==========================================================
@app.get("/statistics")
def stats():
    try:
        total_res = supabase.table("url_analysis").select("id", count="exact").execute()
        total = getattr(total_res, "count", 0) or 0

        def count(pred):
            r = supabase.table("url_analysis").select("id", count="exact").eq("prediction", pred).execute()
            return getattr(r, "count", 0) or 0

        phishing = count("PHISHING")
        suspicious = count("SUSPICIOUS")
        legitimate = count("LEGITIMATE")

        recent_res = supabase.table("url_analysis").select("*").order("created_at", desc=True).limit(10).execute()
        recent = getattr(recent_res, "data", []) or []

        return {
            "total": total,
            "phishing": phishing,
            "suspicious": suspicious,
            "legitimate": legitimate,
            "recent_activity": recent
        }
    except Exception as e:
        logging.exception("Error obteniendo estadísticas")
        return {"error": str(e)}

# ==========================================================
# 🩺 ESTADO DEL SERVIDOR
# ==========================================================
@app.get("/health")
def health():
    return {"status": "running", "db_connected": bool(supabase)}

# ==========================================================
# 📄 GENERAR REPORTE PDF (solo números, sin gráficos)
# ==========================================================

@app.get("/generate-report")
def generate_report():
    """
    Genera un reporte PDF con solo tablas numéricas (sin gráficos) y lo envía a n8n.
    """
    try:
        # Obtener estadísticas desde el endpoint principal
        stats = requests.get("http://localhost:8000/statistics").json()

        phishing = stats.get("phishing", 0)
        suspicious = stats.get("suspicious", 0)
        legitimate = stats.get("legitimate", 0)
        total = stats.get("total", 0)
        recent = stats.get("recent_activity", [])

        # ================================
        # 🧾 Construir contenido HTML (sin gráficos)
        # ================================
        html = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 30px;
                }}
                h1 {{
                    text-align: center;
                    color: #222;
                }}
                h2 {{
                    color: #333;
                    border-bottom: 1px solid #ddd;
                    margin-top: 25px;
                }}
                p {{
                    font-size: 14px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 10px;
                }}
                th, td {{
                    border: 1px solid #ccc;
                    padding: 8px;
                    text-align: center;
                }}
                th {{
                    background-color: #f2f2f2;
                }}
            </style>
        </head>
        <body>
            <h1>Reporte de Detección de Phishing</h1>
            <p><b>Fecha de generación:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

            <h2>Resumen general</h2>
            <table>
                <tr><th>Categoría</th><th>Cantidad</th></tr>
                <tr><td>Fraudulentos</td><td>{phishing}</td></tr>
                <tr><td>Sospechosos</td><td>{suspicious}</td></tr>
                <tr><td>Legítimos</td><td>{legitimate}</td></tr>
                <tr><td><b>Total</b></td><td><b>{total}</b></td></tr>
            </table>

            <h2>Actividad reciente</h2>
            <table>
                <tr><th>URL</th><th>Predicción</th><th>Nivel de riesgo</th><th>Probabilidad</th><th>Fecha</th></tr>
        """

        # Añadir registros recientes a la tabla
        for r in recent:
            html += f"""
                <tr>
                    <td>{r.get('url','')}</td>
                    <td>{r.get('prediction','')}</td>
                    <td>{r.get('risk_level','')}</td>
                    <td>{r.get('probability','')}</td>
                    <td>{r.get('created_at','')}</td>
                </tr>
            """

        html += """
            </table>
            <p style="margin-top:30px; font-size:12px;">
                Este reporte fue generado automáticamente por el sistema de detección de phishing,
                integrando <b>FastAPI</b>, <b>Supabase</b> y <b>n8n</b> para la gestión de flujos de datos.
            </p>
        </body>
        </html>
        """

        # ================================
        # 🖨️ Generar PDF desde HTML
        # ================================
        os.makedirs("reports", exist_ok=True)
        pdf_path = f"reports/reporte_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        HTML(string=html).write_pdf(pdf_path)

        # ================================
        # 🚀 Enviar PDF al webhook n8n
        # ================================
        n8n_url = os.getenv("N8N_PDF_WEBHOOK", "http://localhost:5678/webhook/generate-pdf")
        try:
            with open(pdf_path, "rb") as f:
                files = {"file": (os.path.basename(pdf_path), f, "application/pdf")}
                requests.post(n8n_url, files=files, timeout=20)
        except Exception as e:
            print(f"⚠️ No se pudo enviar el PDF a n8n: {e}")

        return {"status": "ok", "pdf": pdf_path, "message": "Reporte numérico generado correctamente"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando reporte PDF: {e}")
