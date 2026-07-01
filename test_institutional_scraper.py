#!/usr/bin/env python3
"""
Test scraper for institutional job portals v3
ETH Zurich, Fraunhofer, Max Planck
"""

import requests
from bs4 import BeautifulSoup
import re

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def test_eth_zurich():
    print("\n=== ETH ZURICH ===")
    try:
        # Try the index page first
        url = "https://jobs.ethz.ch/site/index"
        r = requests.get(url, headers=HEADERS, timeout=10)
        print(f"Index page status: {r.status_code}")
        soup = BeautifulSoup(r.text, "html.parser")
        
        # Print page title to understand structure
        title = soup.find("title")
        print(f"Page title: {title.get_text() if title else 'N/A'}")
        
        # Find all links to understand structure
        all_links = soup.find_all("a", href=True)
        print(f"Total links on page: {len(all_links)}")
        
        # Look for search or job related links
        relevant = [l for l in all_links if re.search(r'job|search|career|position|vacancy', l.get('href','').lower())]
        print(f"Job-related links: {len(relevant)}")
        for l in relevant[:10]:
            print(f"  -> {l.get_text(strip=True)} | {l['href']}")
            
        # Try search
        search_url = "https://jobs.ethz.ch/site/search?q=business+development"
        r2 = requests.get(search_url, headers=HEADERS, timeout=10)
        print(f"\nSearch page status: {r2.status_code}")
        if r2.status_code == 200:
            soup2 = BeautifulSoup(r2.text, "html.parser")
            links2 = soup2.find_all("a", href=True)
            job_links = [l for l in links2 if re.search(r'/job/|/position/|/vacancy/', l.get('href',''))]
            print(f"Job links in search: {len(job_links)}")
            for l in job_links[:5]:
                print(f"  -> {l.get_text(strip=True)} | {l['href']}")
                
    except Exception as e:
        print(f"ETH error: {e}")


def test_fraunhofer():
    print("\n=== FRAUNHOFER ===")
    try:
        url = "https://jobs.fraunhofer.de/?locale=en_US"
        r = requests.get(url, headers=HEADERS, timeout=10)
        print(f"Status: {r.status_code}")
        soup = BeautifulSoup(r.text, "html.parser")
        
        title = soup.find("title")
        print(f"Page title: {title.get_text() if title else 'N/A'}")
        
        # Look for all links with job-specific patterns
        all_links = soup.find_all("a", href=True)
        print(f"Total links: {len(all_links)}")
        
        # Job links usually have numeric IDs
        job_links = [l for l in all_links if re.search(r'\d{4,}', l.get('href',''))]
        print(f"Links with numeric IDs (likely jobs): {len(job_links)}")
        for l in job_links[:10]:
            print(f"  -> {l.get_text(strip=True)[:60]} | {l['href']}")
            
    except Exception as e:
        print(f"Fraunhofer error: {e}")


def test_max_planck():
    print("\n=== MAX PLANCK ===")
    try:
        url = "https://www.mpg.de/jobboard"
        r = requests.get(url, headers=HEADERS, timeout=10)
        print(f"Status: {r.status_code}")
        soup = BeautifulSoup(r.text, "html.parser")
        
        title = soup.find("title")
        print(f"Page title: {title.get_text() if title else 'N/A'}")
        
        # Find all links with numeric IDs (job postings)
        all_links = soup.find_all("a", href=True)
        job_links = [l for l in all_links if re.search(r'/jobboard/\d+', l.get('href',''))]
        print(f"Job links: {len(job_links)}")
        for l in job_links[:10]:
            print(f"  -> {l.get_text(strip=True)[:80]} | {l['href']}")
            
        # Also try to find job titles directly
        for tag in ["h2", "h3", "h4"]:
            headings = soup.find_all(tag)
            if headings:
                print(f"\n{tag} headings ({len(headings)}):")
                for h in headings[:5]:
                    print(f"  -> {h.get_text(strip=True)[:80]}")
                    
    except Exception as e:
        print(f"Max Planck error: {e}")


if __name__ == "__main__":
    print("Testing institutional job portals v3...")
    test_eth_zurich()
    test_fraunhofer()
    test_max_planck()
    print("\nDone!")
