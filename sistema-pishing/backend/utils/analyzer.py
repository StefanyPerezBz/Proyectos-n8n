import re
import math
import socket
import requests
from urllib.parse import urlparse
from typing import Dict, Any

class PhishingAnalyzer:
    """
    🔍 Analizador heurístico + validación de existencia real del dominio.
    Detecta URLs sospechosas o phishing basándose en estructura, palabras clave,
    entropía del dominio y respuesta HTTP.
    """

    # --------------------------------------------------------
    # EXTRACCIÓN DE CARACTERÍSTICAS
    # --------------------------------------------------------
    @staticmethod
    def extract_features(url: str) -> Dict[str, Any]:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        path = parsed.path.lower()

        suspicious_words = [
            "login", "verify", "account", "update", "bank",
            "secure", "password", "signin", "support", "billing",
            "security", "paypal", "credential", "reset"
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
            "bit.ly", "tinyurl", "t.co", "goo.gl", "is.gd",
            "ow.ly", "buff.ly", "shorturl", "rebrand.ly"
        ]
        uses_shortener = any(s in domain for s in shorteners)

        # Entropía del dominio (nivel de aleatoriedad)
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

    # --------------------------------------------------------
    # COMPROBACIÓN DE EXISTENCIA REAL
    # --------------------------------------------------------
    @staticmethod
    def domain_exists(domain: str) -> bool:
        """Comprueba si el dominio tiene registro DNS."""
        try:
            socket.gethostbyname(domain)
            return True
        except Exception:
            return False

    @staticmethod
    def url_reachable(url: str) -> tuple[bool, int]:
        """Comprueba si la URL responde (HEAD/GET)."""
        try:
            resp = requests.head(url, timeout=4, allow_redirects=True)
            if resp.status_code >= 400 or resp.status_code == 0:
                resp = requests.get(url, timeout=4, allow_redirects=True)
            return resp.status_code < 400, resp.status_code
        except Exception:
            return False, 0

    # --------------------------------------------------------
    # CÁLCULO DE RIESGO
    # --------------------------------------------------------
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

        # penaliza URLs que no responden
        if not reachable:
            score += 0.1
        if f["entropy"] > 3.5:
            score += 0.1
        if f["entropy"] > 4:
            score += 0.15

        return min(max(score, 0), 1.0)

    # --------------------------------------------------------
    # ANÁLISIS GENERAL
    # --------------------------------------------------------
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


# ======================================================
# 🔍 PRUEBA DE URLs
# ======================================================
if __name__ == "__main__":
    test_urls = [
        "https://facebook.com",  # legítima
        "https://example.com/login",  # dominio real, ruta falsa sospechosa
        "https://faceb00k-login.com",  # phishing
        "https://paypal.com.security-check.info",  # phishing
        "https://banco-de-credito.pe.verify-login.info",  # phishing
        "https://secure-update-info.net/account",  # phishing típico
        "https://login.microsoftonline.com",  # legítima
        "https://m1crosoftonline.com-login.co",  # phishing con typo
    ]

    print("\n=== 🔍 ANÁLISIS DE URLs (Legítimas / Sospechosas / Phishing) ===\n")

    for url in test_urls:
        result = PhishingAnalyzer.analyze_url(url)
        color = {
            "HIGH": "\033[91m",
            "MEDIUM": "\033[93m",
            "LOW": "\033[92m",
        }[result["risk_level"]]
        reset = "\033[0m"

        print(f"🌐 URL: {url}")
        print(f"{color}🧩 Predicción: {result['prediction']}{reset}")
        print(f"{color}⚠️ Nivel de riesgo: {result['risk_level']}{reset}")
        print(f"🎯 Probabilidad: {result['probability']}")
        print(f"🌎 Dominio: {result['features']['domain']} ({result['features']['domain_status']})")
        print(f"📶 Responde HTTP: {result['features']['reachable']} ({result['features']['http_status']})")
        print(f"🔢 Entropía: {result['features']['entropy']}")
        print("-" * 100)
