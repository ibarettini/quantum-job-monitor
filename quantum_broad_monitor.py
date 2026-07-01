#!/usr/bin/env python3
"""
Broad Tech Job Monitor v2
Semiconductors, Security, Cryptography, Identity, Payments, Deep Tech + Quantum BD
"""

import requests
import smtplib
import os
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from bs4 import BeautifulSoup

# ============================================================
# CONFIGURACIÓN
# ============================================================

EMAIL_FROM = "inakibarettini@gmail.com"
EMAIL_TO   = "inakibarettini@gmail.com"
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_PASSWORD", "")

ROLE_KEYWORDS = [
    "business development", "commercial partnerships", "market development",
    "application manager", "innovation manager", "tech transfer",
    "ip licensing", "licensing management", "bd manager", "head of commercial",
    "product strategy", "gtm manager", "partnership manager", "ecosystem manager",
    "solutions architect", "commercial director", "quantum applications",
    "quantum solutions", "quantum ecosystem", "quantum commercialization",
    "quantum partnerships", "exploitation manager", "valorisation",
    "knowledge transfer", "alliance manager", "channel manager",
    "product line manager", "segment manager",
]

SECTOR_KEYWORDS = [
    # Quantum
    "quantum", "qkd", "post-quantum",
    # Semiconductors
    "semiconductor", "microelectronics", "chip", "soc", "microcontroller",
    "fpga", "asic", "embedded security", "secure element", "nfc", "ble",
    # Security & Cryptography
    "cybersecurity", "cryptography", "pki", "hsm", "encryption",
    "security electronics", "hardware security", "post-quantum cryptography",
    # Identity & Payments
    "digital identity", "authentication", "identity management",
    "payment systems", "fintech", "smart card", "emv", "contactless",
    "biometrics", "access control", "physical security",
    # Photonics & Deep Tech
    "photonics", "optics", "deep tech", "iot", "iiot",
    # Defense & Dual Use
    "defense tech", "dual use", "sovereign", "critical infrastructure",
    # Companies as sector signals
    "nxp", "infineon", "stmicroelectronics", "st micro",
    "ams-osram", "ams osram", "bosch semiconductor",
    "nordic semiconductor", "melexis", "elmos", "trumpf",
    "jenoptik", "aixtron", "thales", "gemalto", "idemia",
    "hid global", "dormakaba", "allegro micro",
]

COUNTRY_KEYWORDS = [
    "germany", "deutschland", "munich", "berlin", "hamburg", "frankfurt",
    "switzerland", "zurich", "zürich", "geneva", "basel",
    "austria", "vienna", "wien",
    "netherlands", "amsterdam", "eindhoven", "delft",
    "france", "paris", "grenoble", "sophia antipolis",
    "uk", "london", "oxford", "cambridge", "reading",
    "belgium", "leuven",
    "finland", "espoo",
    "remote", "hybrid", "europe", "european", "emea",
]

EXCLUDE_KEYWORDS = [
    "phd position", "postdoc", "research scientist", "software engineer",
    "hardware engineer", "lab technician", "internship", "praktikum",
    "process engineer", "design engineer", "test engineer", "layout engineer",
    "verification engineer", "rtl designer",
]

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# ============================================================
# FUENTES
# ============================================================

def fetch_linkedin():
    jobs = []
    searches = [
        "semiconductor+business+development&location=Germany",
        "semiconductor+business+development&location=Netherlands",
        "cybersecurity+business+development&location=DACH",
        "digital+identity+business+development&location=Europe",
        "payment+systems+business+development&location=Europe",
        "photonics+innovation+manager&location=Europe",
        "deep+tech+partnership+manager&location=Europe",
        "quantum+applications+manager&location=Europe",
        "security+electronics+business+development&location=Europe",
        "cryptography+product+manager&location=Europe",
    ]
    for s in searches:
        try:
            url = f"https://www.linkedin.com/jobs/search/?keywords={s}&f_WT=2%2C3"
            r = requests.get(url, headers=HEADERS, timeout=10)
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


def fetch_fraunhofer():
    jobs = []
    keywords = ["business development", "tech transfer", "innovation manager",
                "licensing", "exploitation", "partnership", "commercialization"]
    for kw in keywords:
        try:
            url = f"https://jobs.fraunhofer.de/suche?q={requests.utils.quote(kw)}"
            r = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            for card in soup.find_all(["div", "li", "article"], class_=re.compile("job|result|item")):
                title = card.find(["h2", "h3", "h4", "a"])
                link = card.find("a", href=True)
                location = card.find(class_=re.compile("location|ort"))
                if title:
                    jobs.append({
                        "title": title.get_text(strip=True),
                        "company": "Fraunhofer",
                        "location": location.get_text(strip=True) if location else "Germany",
                        "url": "https://jobs.fraunhofer.de" + link["href"] if link and link["href"].startswith("/") else (link["href"] if link else ""),
                        "source": "Fraunhofer"
                    })
        except Exception as e:
            print(f"Fraunhofer error: {e}")
    return jobs


def fetch_imec():
    jobs = []
    try:
        url = "https://www.imec-int.com/en/careers/job-opportunities"
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        for card in soup.find_all(["div", "li", "article"], class_=re.compile("job|vacancy|card")):
            title = card.find(["h2", "h3", "h4", "a"])
            link = card.find("a", href=True)
            if title:
                jobs.append({
                    "title": title.get_text(strip=True),
                    "company": "imec",
                    "location": "Belgium / Europe",
                    "url": link["href"] if link else "https://www.imec-int.com/en/careers",
                    "source": "imec"
                })
    except Exception as e:
        print(f"imec error: {e}")
    return jobs


def fetch_eth_zurich():
    jobs = []
    try:
        url = "https://jobs.ethz.ch/job/search?q=business+development"
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        for card in soup.find_all(["div", "li", "article"], class_=re.compile("job|result|item")):
            title = card.find(["h2", "h3", "h4", "a"])
            link = card.find("a", href=True)
            if title:
                jobs.append({
                    "title": title.get_text(strip=True),
                    "company": "ETH Zurich",
                    "location": "Zurich, Switzerland",
                    "url": "https://jobs.ethz.ch" + link["href"] if link and link["href"].startswith("/") else (link["href"] if link else ""),
                    "source": "ETH Zurich"
                })
    except Exception as e:
        print(f"ETH Zurich error: {e}")
    return jobs


def fetch_nxp():
    jobs = []
    try:
        url = "https://www.nxp.com/company/careers/search-and-apply:CAREERS#q=business+development&t=Jobs"
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        for card in soup.find_all(["div", "li", "article"], class_=re.compile("job|result|card")):
            title = card.find(["h2", "h3", "h4", "a"])
            link = card.find("a", href=True)
            location = card.find(class_=re.compile("location"))
            if title:
                jobs.append({
                    "title": title.get_text(strip=True),
                    "company": "NXP Semiconductors",
                    "location": location.get_text(strip=True) if location else "Europe",
                    "url": link["href"] if link else "https://www.nxp.com/careers",
                    "source": "NXP"
                })
    except Exception as e:
        print(f"NXP error: {e}")
    return jobs


def fetch_infineon():
    jobs = []
    try:
        url = "https://jobs.infineon.com/careers?q=business+development&domain=infineon.com"
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        for card in soup.find_all(["div", "li", "article"], class_=re.compile("job|result|card")):
            title = card.find(["h2", "h3", "h4", "a"])
            link = card.find("a", href=True)
            location = card.find(class_=re.compile("location"))
            if title:
                jobs.append({
                    "title": title.get_text(strip=True),
                    "company": "Infineon Technologies",
                    "location": location.get_text(strip=True) if location else "Europe",
                    "url": link["href"] if link else "https://jobs.infineon.com",
                    "source": "Infineon"
                })
    except Exception as e:
        print(f"Infineon error: {e}")
    return jobs


# ============================================================
# FILTRADO
# ============================================================

def is_relevant(job):
    text = f"{job['title']} {job['company']} {job['location']}".lower()

    for kw in EXCLUDE_KEYWORDS:
        if kw in text:
            return False

    has_sector = any(kw in text for kw in SECTOR_KEYWORDS)
    if not has_sector:
        return False

    has_role = any(kw in text for kw in ROLE_KEYWORDS)
    if not has_role:
        return False

    has_location = any(kw in text for kw in COUNTRY_KEYWORDS)
    if not has_location:
        return False

    return True


def is_relevant_institutional(job):
    text = f"{job['title']} {job['company']}".lower()

    for kw in EXCLUDE_KEYWORDS:
        if kw in text:
            return False

    has_role = any(kw in text for kw in ROLE_KEYWORDS)
    return has_role


# ============================================================
# EMAIL
# ============================================================

def send_email(jobs):
    today = datetime.now().strftime("%d/%m/%Y")

    if not jobs:
        subject = f"🔍 Broad Tech Monitor – {today} – Sin novedades"
        body_html = f"""
        <h2>Broad Tech Job Monitor – {today}</h2>
        <p>No se han encontrado ofertas nuevas relevantes hoy.</p>
        <p><i>Sectores: Semiconductores | Seguridad | Criptografía | Identidad Digital | Pagos | Fotónica | Deep Tech | Quantum BD</i></p>
        """
    else:
        subject = f"⚡ Broad Tech Monitor – {today} – {len(jobs)} oferta(s) encontrada(s)"
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
        <h2 style="color:#e8871a;">⚡ Broad Tech Job Monitor – {today}</h2>
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
            Sectores: Semiconductores | Seguridad | Criptografía | Identidad Digital | Pagos | Fotónica | Deep Tech | Quantum BD |
            DE / CH / AT / NL / FR / UK / BE / Remote
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
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Iniciando búsqueda broad tech...")

    all_jobs = []
    all_jobs += fetch_linkedin()

    institutional = []
    institutional += fetch_fraunhofer()
    institutional += fetch_imec()
    institutional += fetch_eth_zurich()
    institutional += fetch_nxp()
    institutional += fetch_infineon()

    relevant_general = [j for j in all_jobs if is_relevant(j)]
    relevant_institutional = [j for j in institutional if is_relevant_institutional(j)]

    all_relevant = relevant_general + relevant_institutional

    seen = set()
    unique = []
    for j in all_relevant:
        key = f"{j['title'].lower()}|{j['company'].lower()}"
        if key not in seen:
            seen.add(key)
            unique.append(j)

    print(f"Total antes de filtrar: {len(all_jobs) + len(institutional)}")
    print(f"Ofertas relevantes: {len(unique)}")

    send_email(unique)
    print("¡Listo!")
