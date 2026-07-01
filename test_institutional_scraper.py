#!/usr/bin/env python3
"""
Test scraper v6 - imec deep dive + BSC confirmation
"""

import requests
from bs4 import BeautifulSoup
import re

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

ROLE_KEYWORDS = [
    "business development", "tech transfer", "innovation manager",
    "licensing", "exploitation", "partnership", "commercialization",
    "knowledge transfer", "valorisation", "market development",
    "bd manager", "commercial", "ecosystem", "ip manager",
    "chief of staff", "director", "manager", "head of",
    "project manager", "sales", "support services",
]

EXCLUDE_KEYWORDS = [
    "phd", "postdoc", "research scientist", "software engineer",
    "hardware engineer", "lab technician", "internship", "professor",
    "postdoctoral", "becario", "undergraduate", "student", "r1", "r0", "r2",
]

def test_imec_jobs():
    print("\n=== IMEC - Job opportunities deep dive ===")
    urls = [
        "https://www.imec-int.com/en/work-at-imec/job-opportunities",
        "https://www.imec-int.com/en/careers/sales-management-support-services",
    ]
    for url in urls:
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            print(f"\nURL: {url}")
            print(f"Status: {r.status_code}")
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, "html.parser")
                title = soup.find("title")
                print(f"Page title: {title.get_text(strip=True)[:80] if title else 'N/A'}")
                
                all_links = soup.find_all("a", href=True)
                print(f"Total links: {len(all_links)}")
                
                # Job links with numeric IDs
                job_links = [l for l in all_links if re.search(r'\d{4,}|/job/|/vacancy/', l.get('href', ''))]
                print(f"Job links: {len(job_links)}")
                for l in job_links[:10]:
                    print(f"  -> {l.get_text(strip=True)[:80]} | {l['href']}")
                
                # Headings
                for tag in ["h2", "h3", "h4"]:
                    headings = soup.find_all(tag)
                    if headings and len(headings) < 20:
                        print(f"{tag} headings ({len(headings)}):")
                        for h in headings[:8]:
                            print(f"  -> {h.get_text(strip=True)[:80]}")
                            
                # Look for any text containing job titles
                relevant_links = [l for l in all_links 
                                  if any(kw in l.get_text(strip=True).lower() for kw in ROLE_KEYWORDS)
                                  and not any(kw in l.get_text(strip=True).lower() for kw in EXCLUDE_KEYWORDS)
                                  and len(l.get_text(strip=True)) > 10]
                print(f"\nRelevant links by keyword: {len(relevant_links)}")
                for l in relevant_links[:10]:
                    print(f"  -> {l.get_text(strip=True)[:80]} | {l['href']}")
                    
        except Exception as e:
            print(f"imec error ({url}): {e}")


def test_bsc_confirmation():
    print("\n=== BSC - Confirmation run ===")
    try:
        url = "https://www.bsc.es/join-us/job-opportunities"
        r = requests.get(url, headers=HEADERS, timeout=10)
        print(f"Status: {r.status_code}")
        soup = BeautifulSoup(r.text, "html.parser")
        
        all_links = soup.find_all("a", href=True)
        job_links = [l for l in all_links if "/job-opportunities/" in l.get('href', '')
                     and l.get_text(strip=True)
                     and len(l.get_text(strip=True)) > 10]
        
        relevant = []
        for l in job_links:
            title = l.get_text(strip=True)
            title_lower = title.lower()
            if any(kw in title_lower for kw in ROLE_KEYWORDS) and not any(kw in title_lower for kw in EXCLUDE_KEYWORDS):
                relevant.append({"title": title, "url": l['href']})
        
        print(f"Total jobs: {len(job_links)}, Relevant: {len(relevant)}")
        for j in relevant:
            print(f"  -> {j['title']}")
            print(f"     {j['url']}")
            
    except Exception as e:
        print(f"BSC error: {e}")


if __name__ == "__main__":
    print("Testing imec and BSC v6...")
    test_imec_jobs()
    test_bsc_confirmation()
    print("\nDone!")
