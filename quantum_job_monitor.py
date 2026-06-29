#!/usr/bin/env python3
"""
Quantum Job Monitor
Busca ofertas de trabajo relevantes y envía un resumen diario por email.
"""

import requests
import smtplib
import json
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from bs4 import BeautifulSoup

# ============================================================
# CONFIGURACIÓN - Edita estos valores
# ============================================================

EMAIL_FROM = "inakibarettini@gmail.com"        # Tu Gmail
EMAIL_TO   = "inakibarettini@gmail.com"        # Donde recibes el resumen
import os
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_PASSWORD", "")  # App Password de Gmail (sin espacios internos)

# Palabras clave para roles (cualquiera de estas)
ROLE_KEYWORDS = [
    "business development",
    "commercial partnerships",
    "market development",
    "application manager",
    "innovation manager",
    "tech transfer",
    "ip licensing",
    "licensing management",
    "bd manager",
    "head of commercial",
]

# Palabras clave de sector (al menos una debe aparecer)
SECTOR_KEYWORDS = [
    "quantum",
    "qkd",
    "post-quantum",
    "deep tech",
    "photonics",
    "cryptography",
]

# Palabras que indican nivel senior
SENIORITY_KEYWORDS = [
    "senior", "director", "head of", "lead", "principal", "manager", "vp", "chief"
]

# Países objetivo
COUNTRY_KEYWORDS = [
    "germany", "deutschland", "munich", "berlin", "hamburg", "frankfurt",
    "switzerland", "zurich", "zürich", "geneva", "basel",
    "austria", "vienna", "wien",
    "netherlands", "amsterdam", "eindhoven", "delft",
    "remote", "hybrid", "europe"
]

# Palabras que excluyen la oferta (roles puramente técnicos)
EXCLUDE_KEYWORDS = [
    "phd position", "postdoc", "research scientist", "software engineer",
    "hardware engineer", "physicist", "lab technician", "internship", "praktikum"
]

# ============================================================
# FUENTES DE BÚSQUEDA
# ============================================================

def fetch_quantum_jobs():
    """Busca en quantum.jobs via RSS o API pública"""
    jobs = []
    try:
        url = "https://quantum.jobs/jobs.json?category=business"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            for job in data.get("jobs", []):
                jobs.append({
                    "title": job.get("title", ""),
                    "company": job.get("company", ""),
                    "location": job.get("location", ""),
                    "url": job.get("url", ""),
                    "source": "quantum.jobs"
                })
    except Exception as e:
        print(f"quantum.jobs error: {e}")
    return jobs


def fetch_google_jobs_rss():
    """Busca via Google Jobs RSS (no requiere API key)"""
    jobs = []
    queries = [
        "quantum business development Germany Switzerland Austria Netherlands",
        "quantum tech transfer innovation manager Europe remote",
        "QKD quantum cryptography business development Europe",
    ]
    headers = {"User-Agent": "Mozilla/5.0"}
    for query in queries:
        try:
            encoded = requests.utils.quote(query)
            url = f"https://www.google.com/search?q={encoded}+jobs&tbm=jobs&hl=en"
            r = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            for card in soup.find_all("div", class_=re.compile("job")):
                title = card.find("h3")
                company = card.find("div", class_=re.compile("company"))
                location = card.find("div", class_=re.compile("location"))
                link = card.find("a", href=True)
                if title:
                    jobs.append({
                        "title": title.get_text(strip=True),
                        "company": company.get_text(strip=True) if company else "",
                        "location": location.get_text(strip=True) if location else "",
                        "url": "https://www.google.com" + link["href"] if link else "",
                        "source": "Google Jobs"
                    })
        except Exception as e:
            print(f"Google Jobs error: {e}")
    return jobs


def fetch_linkedin_rss():
    """Busca via LinkedIn Jobs RSS público"""
    jobs = []
    searches = [
        "quantum+business+development&location=Germany",
        "quantum+business+development&location=Switzerland",
        "quantum+innovation+manager&location=Europe",
        "tech+transfer+quantum&location=Europe",
    ]
    headers = {"User-Agent": "Mozilla/5.0"}
    for s in searches:
        try:
            url = f"https://www.linkedin.com/jobs/search/?keywords={s}&f_WT=2%2C3"
            r = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            for card in soup.find_all("div", class_=re.compile("job-search-card")):
                title = card.find("h3")
                company = card.find("h4")
                location = card.find("span", class_=re.compile("location"))
                link = card.find("a", href=True)
                if title:
                    jobs.append({
                        "title": title.get_text(strip=True),
                        "company": company.get_text(strip=True) if company else "",
                        "location": location.get_text(strip=True) if location else "",
                        "url": link["href"] if link else "",
                        "source": "LinkedIn"
                    })
        except Exception as e:
            print(f"LinkedIn error: {e}")
    return jobs


# ============================================================
# FILTRADO
# ============================================================

def is_relevant(job):
    text = f"{job['title']} {job['company']} {job['location']}".lower()

    # Excluir si contiene keywords de exclusión
    for kw in EXCLUDE_KEYWORDS:
        if kw in text:
            return False

    # Debe tener al menos una keyword de sector
    has_sector = any(kw in text for kw in SECTOR_KEYWORDS)
    if not has_sector:
        return False

    # Debe tener al menos una keyword de rol
    has_role = any(kw in text for kw in ROLE_KEYWORDS)
    if not has_role:
        return False

    # Debe tener al menos una keyword de país o modalidad
    has_location = any(kw in text for kw in COUNTRY_KEYWORDS)
    if not has_location:
        return False

    return True


# ============================================================
# EMAIL
# ============================================================

def send_email(jobs):
    today = datetime.now().strftime("%d/%m/%Y")

    if not jobs:
        subject = f"🔍 Quantum Jobs Monitor – {today} – Sin novedades"
        body_html = f"""
        <h2>Quantum Job Monitor – {today}</h2>
        <p>No se han encontrado ofertas nuevas relevantes hoy.</p>
        <p><i>Fuentes revisadas: quantum.jobs, LinkedIn, Google Jobs</i></p>
        """
    else:
        subject = f"🚀 Quantum Jobs Monitor – {today} – {len(jobs)} oferta(s) encontrada(s)"
        rows = ""
        for j in jobs:
            rows += f"""
            <tr>
                <td style="padding:8px;border-bottom:1px solid #eee;">
                    <a href="{j['url']}" style="color:#1a73e8;font-weight:bold;">{j['title']}</a>
                </td>
                <td style="padding:8px;border-bottom:1px solid #eee;">{j['company']}</td>
                <td style="padding:8px;border-bottom:1px solid #eee;">{j['location']}</td>
                <td style="padding:8px;border-bottom:1px solid #eee;color:#888;">{j['source']}</td>
            </tr>
            """
        body_html = f"""
        <html><body style="font-family:Arial,sans-serif;max-width:800px;margin:auto;">
        <h2 style="color:#1a73e8;">🚀 Quantum Job Monitor – {today}</h2>
        <p>Se han encontrado <b>{len(jobs)}</b> oferta(s) relevante(s):</p>
        <table style="width:100%;border-collapse:collapse;">
            <thead>
                <tr style="background:#f1f3f4;">
                    <th style="padding:8px;text-align:left;">Posición</th>
                    <th style="padding:8px;text-align:left;">Empresa</th>
                    <th style="padding:8px;text-align:left;">Ubicación</th>
                    <th style="padding:8px;text-align:left;">Fuente</th>
                </tr>
            </thead>
            <tbody>{rows}</tbody>
        </table>
        <br>
        <p style="color:#888;font-size:12px;">
            Criterios: quantum / QKD / deep tech | BD / Innovation / Tech Transfer | 
            DE / CH / AT / NL / Remote | Senior+
        </p>
        </body></html>
        """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    msg.attach(MIMEText(body_html, "html"))

    password = GMAIL_APP_PASSWORD.replace(" ", "")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_FROM, password)
        server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())

    print(f"Email enviado: {subject}")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Iniciando búsqueda...")

    all_jobs = []
    all_jobs += fetch_quantum_jobs()
    all_jobs += fetch_google_jobs_rss()
    all_jobs += fetch_linkedin_rss()

    print(f"Total ofertas encontradas antes de filtrar: {len(all_jobs)}")

    # Filtrar relevantes
    relevant = [j for j in all_jobs if is_relevant(j)]

    # Deduplicar por título + empresa
    seen = set()
    unique = []
    for j in relevant:
        key = f"{j['title'].lower()}|{j['company'].lower()}"
        if key not in seen:
            seen.add(key)
            unique.append(j)

    print(f"Ofertas relevantes tras filtrar: {len(unique)}")

    send_email(unique)
    print("¡Listo!")
