#!/usr/bin/env python3
"""
Unified Job Monitor v1
Single daily email with two sections: Quantum and Broad Tech
No duplicates between sections
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

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# ============================================================
# KEYWORDS
# ============================================================

QUANTUM_SECTOR_KEYWORDS = [
    "quantum", "qkd", "post-quantum cryptography", "quantum computing",
    "quantum sensing", "quantum communication", "quantum network",
]

BROAD_SECTOR_KEYWORDS = [
    "semiconductor", "microelectronics", "chip", "soc", "microcontroller",
    "fpga", "asic", "embedded security", "secure element", "nfc", "ble",
    "cybersecurity", "cryptography", "pki", "hsm", "encryption",
    "security electronics", "hardware security",
    "digital identity", "authentication", "identity management",
    "payment systems", "fintech", "smart card", "emv", "contactless",
    "biometrics", "access control", "physical security",
    "photonics", "optics", "deep tech", "iot", "iiot",
    "defense tech", "dual use", "sovereign", "critical infrastructure",
    "nxp", "infineon", "stmicroelectronics", "st micro",
    "ams-osram", "bosch semiconductor", "nordic semiconductor",
    "melexis", "elmos", "trumpf", "jenoptik", "aixtron",
    "thales", "gemalto", "idemia", "hid global", "dormakaba",
    "giesecke", "devrient",
]

ROLE_KEYWORDS = [
    "business development", "commercial partnerships", "market development",
    "application manager", "innovation manager", "tech transfer",
    "ip licensing", "licensing management", "bd manager", "head of commercial",
    "product strategy", "gtm manager", "partnership manager", "ecosystem manager",
    "commercial director", "quantum applications", "quantum solutions",
    "quantum ecosystem", "quantum commercialization", "quantum partnerships",
    "exploitation manager", "valorisation", "knowledge transfer",
    "alliance manager", "product line manager", "segment manager",
    "chief of staff", "project manager", "programme manager", "program manager",
    "coordinator", "director", "head of", "roadmap manager",
    "sales manager", "account manager", "key account", "product manager",
    "solutions architect", "applications engineer", "senior manager",
    "executive director", "departementsmanager",
]

COUNTRY_KEYWORDS = [
    "germany", "deutschland", "munich", "berlin", "hamburg", "frankfurt",
    "switzerland", "zurich", "zürich", "geneva", "basel", "neuchâtel",
    "austria", "vienna", "wien",
    "netherlands", "amsterdam", "eindhoven", "delft",
    "france", "paris", "grenoble", "palaiseau",
    "uk", "london", "oxford", "cambridge", "reading", "teddington",
    "belgium", "leuven", "brussels", "tubize",
    "finland", "espoo",
    "spain", "barcelona", "madrid",
    "denmark", "europe", "european", "emea", "remote", "hybrid",
]

# Excluir estas empresas
EXCLUDE_COMPANIES = [
    "quantum systems",
]

# Excluir estos tipos de rol
EXCLUDE_ROLE_KEYWORDS = [
    "risk manager", "business continuity", "situation monitoring",
    "sales manager automotive", "sales manager apac", "sales manager japan",
    "sales manager korea", "air quality", "earth science", "forecast",
    "phd", "postdoc", "postdoctoral", "research scientist",
    "software engineer", "hardware engineer", "lab technician",
    "internship", "praktikum", "undergraduate", "student",
    "process engineer", "design engineer", "test engineer",
    "layout engineer", "verification engineer", "rtl designer",
    "office manager", "data manager fair", "r1)", "r0)", "r2)",
]

# ============================================================
# FUENTES
# ============================================================

def fetch_linkedin_quantum():
    jobs = []
    searches = [
        "quantum+business+development&location=Germany",
        "quantum+business+development&location=Switzerland",
        "quantum+innovation+manager&location=Europe",
        "tech+transfer+quantum&location=Europe",
        "quantum+ecosystem+manager&location=Europe",
        "quantum+partnerships&location=Europe",
        "quantum+programme+manager&location=Europe",
        "quantum+project+manager&location=Europe",
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
            print(f"LinkedIn quantum error: {e}")
    return jobs


def fetch_linkedin_broad():
    jobs = []
    searches = [
        "semiconductor+business+development&location=Germany",
        "semiconductor+business+development&location=Netherlands",
        "cybersecurity+business+development&location=DACH",
        "digital+identity+business+development&location=Europe",
        "payment+systems+business+development&location=Europe",
        "photonics+innovation+manager&location=Europe",
        "deep+tech+partnership+manager&location=Europe",
        "security+electronics+business+development&location=Europe",
        "cryptography+product+manager&location=Europe",
        "semiconductor+product+manager&location=Europe",
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
            print(f"LinkedIn broad error: {e}")
    return jobs


def fetch_eth_zurich():
    jobs = []
    try:
        url = "https://jobs.ethz.ch/site/index"
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        all_links = soup.find_all("a", href=True)
        job_links = [l for l in all_links if "/job/view/" in l.get('href', '')]
        for link in job_links:
            title = link.get_text(strip=True)
            title_clean = title.split("100%")[0].split("80%")[0].split("60%")[0].strip()
            href = link['href']
            full_url = f"https://jobs.ethz.ch{href}" if href.startswith('/') else href
            jobs.append({
                "title": title_clean,
                "company": "ETH Zurich",
                "location": "Zurich, Switzerland",
                "url": full_url,
                "source": "ETH Zurich"
            })
    except Exception as e:
        print(f"ETH Zurich error: {e}")
    return jobs


def fetch_bsc():
    jobs = []
    try:
        url = "https://www.bsc.es/join-us/job-opportunities"
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        all_links = soup.find_all("a", href=True)
        job_links = [l for l in all_links if "/job-opportunities/" in l.get('href', '')
                     and l.get_text(strip=True)
                     and len(l.get_text(strip=True)) > 10]
        for link in job_links:
            jobs.append({
                "title": link.get_text(strip=True),
                "company": "BSC Barcelona Supercomputing Center",
                "location": "Barcelona, Spain",
                "url": link['href'],
                "source": "BSC"
            })
    except Exception as e:
        print(f"BSC error: {e}")
    return jobs


def fetch_qutech():
    jobs = []
    try:
        url = "https://qutech.nl/careers/job-opportunities/"
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        all_links = soup.find_all("a", href=True)
        job_links = [l for l in all_links if "/vacancy/" in l.get('href', '')
                     and l.get_text(strip=True)
                     and len(l.get_text(strip=True)) > 5]
        seen = set()
        for link in job_links:
            if link['href'] not in seen:
                seen.add(link['href'])
                jobs.append({
                    "title": link.get_text(strip=True),
                    "company": "QuTech / TU Delft",
                    "location": "Delft, Netherlands",
                    "url": link['href'],
                    "source": "QuTech"
                })
    except Exception as e:
        print(f"QuTech error: {e}")
    return jobs


def fetch_quantumjobs_portals():
    jobs = []
    portals = [
        ("https://www.quantumjobs.us/jobs", "quantumjobs.us"),
        ("https://quantumcomputingjobs.co.uk/jobs/", "quantumcomputingjobs.co.uk"),
        ("https://quantumconsortium.org/quantum-jobs/", "quantumconsortium.org"),
    ]
    for url, source in portals:
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            for card in soup.find_all(["div", "li", "article"], class_=re.compile("job|posting|listing")):
                title = card.find(["h2", "h3", "h4", "a"])
                link = card.find("a", href=True)
                location = card.find(class_=re.compile("location|place"))
                company = card.find(class_=re.compile("company|employer"))
                if title and title.get_text(strip=True):
                    jobs.append({
                        "title": title.get_text(strip=True),
                        "company": company.get_text(strip=True) if company else "",
                        "location": location.get_text(strip=True) if location else "",
                        "url": link["href"] if link else url,
                        "source": source
                    })
        except Exception as e:
            print(f"{source} error: {e}")
    return jobs


# ============================================================
# FILTRADO
# ============================================================

def is_excluded(job):
    title = job['title'].lower()
    company = job['company'].lower()

    # Excluir empresas
    if any(exc in company for exc in EXCLUDE_COMPANIES):
        return True

    # Excluir roles
    if any(kw in title for kw in EXCLUDE_ROLE_KEYWORDS):
        return True

    return False


def is_quantum(job):
    text = f"{job['title']} {job['company']} {job['location']}".lower()
    if is_excluded(job):
        return False
    has_quantum = any(kw in text for kw in QUANTUM_SECTOR_KEYWORDS)
    has_role = any(kw in text for kw in ROLE_KEYWORDS)
    has_location = any(kw in text for kw in COUNTRY_KEYWORDS)
    return has_quantum and has_role and has_location


def is_broad(job):
    text = f"{job['title']} {job['company']} {job['location']}".lower()
    if is_excluded(job):
        return False
    has_sector = any(kw in text for kw in BROAD_SECTOR_KEYWORDS)
    has_role = any(kw in text for kw in ROLE_KEYWORDS)
    has_location = any(kw in text for kw in COUNTRY_KEYWORDS)
    return has_sector and has_role and has_location


def is_institutional_relevant(job):
    text = job['title'].lower()
    if is_excluded(job):
        return False
    return any(kw in text for kw in ROLE_KEYWORDS)


def dedup(jobs):
    seen = set()
    unique = []
    for j in jobs:
        key = f"{j['title'].lower()}|{j['company'].lower()}"
        if key not in seen:
            seen.add(key)
            unique.append(j)
    return unique


# ============================================================
# EMAIL
# ============================================================

def build_table(jobs):
    if not jobs:
        return "<p><i>No se han encontrado ofertas hoy.</i></p>"
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
    return f"""
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
    """


def send_email(quantum_jobs, broad_jobs):
    today = datetime.now().strftime("%d/%m/%Y")
    total = len(quantum_jobs) + len(broad_jobs)

    subject = f"🔭 Job Monitor – {today} – {total} oferta(s) encontrada(s)"

    body_html = f"""
    <html><body style="font-family:Arial,sans-serif;max-width:900px;margin:auto;">

    <h2 style="color:#333;">🔭 Job Monitor – {today}</h2>
    <p>Total: <b>{total} oferta(s)</b> — 
       🔵 Quantum: {len(quantum_jobs)} | 
       🟠 Broad Tech: {len(broad_jobs)}</p>

    <hr style="border:2px solid #1a73e8;margin:20px 0;">
    <h3 style="color:#1a73e8;">🔵 QUANTUM ({len(quantum_jobs)} ofertas)</h3>
    {build_table(quantum_jobs)}

    <hr style="border:2px solid #e8871a;margin:20px 0;">
    <h3 style="color:#e8871a;">🟠 BROAD TECH ({len(broad_jobs)} ofertas)</h3>
    <p style="color:#888;font-size:12px;">Semiconductores | Seguridad | Criptografía | Identidad Digital | Pagos | Fotónica | Deep Tech</p>
    {build_table(broad_jobs)}

    <hr style="margin:20px 0;">
    <p style="color:#aaa;font-size:11px;">
        Fuentes: LinkedIn | ETH Zurich | BSC | QuTech | quantumjobs.us | quantumcomputingjobs.co.uk | quantumconsortium.org
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
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Iniciando Job Monitor unificado...")

    # Fetch all sources
    linkedin_quantum = fetch_linkedin_quantum()
    linkedin_broad = fetch_linkedin_broad()
    institutional = fetch_eth_zurich() + fetch_bsc() + fetch_qutech()
    portals = fetch_quantumjobs_portals()

    print(f"LinkedIn quantum: {len(linkedin_quantum)}")
    print(f"LinkedIn broad: {len(linkedin_broad)}")
    print(f"Institutional: {len(institutional)}")
    print(f"Portals: {len(portals)}")

    # Classify quantum jobs
    quantum_candidates = linkedin_quantum + portals + institutional
    quantum_jobs = dedup([j for j in quantum_candidates if is_quantum(j)] +
                         [j for j in institutional if is_institutional_relevant(j) and "quantum" in f"{j['title']} {j['company']}".lower()])

    # Classify broad jobs (exclude what's already in quantum)
    quantum_keys = {f"{j['title'].lower()}|{j['company'].lower()}" for j in quantum_jobs}
    broad_candidates = linkedin_broad + institutional
    broad_jobs_raw = [j for j in broad_candidates if is_broad(j)]
    broad_jobs = dedup([j for j in broad_jobs_raw
                        if f"{j['title'].lower()}|{j['company'].lower()}" not in quantum_keys])

    print(f"Quantum jobs: {len(quantum_jobs)}")
    print(f"Broad jobs: {len(broad_jobs)}")

    send_email(quantum_jobs, broad_jobs)
    print("¡Listo!")
