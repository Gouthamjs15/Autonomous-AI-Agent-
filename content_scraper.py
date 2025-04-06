from bs4 import BeautifulSoup
import re
import os
import hashlib
import requests

def download_image(img_url, base_url, save_dir="images"):
    try:
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        if img_url.startswith("//"):
            img_url = "https:" + img_url
        elif img_url.startswith("/"):
            from urllib.parse import urljoin
            img_url = urljoin(base_url, img_url)

        img_ext = os.path.splitext(img_url)[-1]
        if not img_ext or len(img_ext) > 5:
            img_ext = ".jpg"

        img_name = hashlib.md5(img_url.encode()).hexdigest() + img_ext
        img_path = os.path.join(save_dir, img_name)

        response = requests.get(img_url, timeout=5)
        if response.status_code == 200:
            with open(img_path, "wb") as f:
                f.write(response.content)
            return img_path
    except Exception as e:
        print(f"[⚠️] Failed to download {img_url}: {e}")
    return None

def extract_pros_cons(soup):
    pros, cons = [], []
    for header in soup.find_all(['h2', 'h3', 'strong']):
        text = header.get_text(strip=True).lower()
        if "pros" in text:
            ul = header.find_next_sibling('ul')
            if ul:
                pros.extend([li.get_text(strip=True) for li in ul.find_all('li')])
        if "cons" in text:
            ul = header.find_next_sibling('ul')
            if ul:
                cons.extend([li.get_text(strip=True) for li in ul.find_all('li')])
    return pros, cons

def scrape_content(html, base_url):
    soup = BeautifulSoup(html, "html.parser")

    # Extract main readable text
    paragraphs = soup.find_all("p")
    main_text = "\n".join([p.get_text(strip=True) for p in paragraphs if len(p.get_text()) > 50])

    # Extract and download images
    images = []
    for img in soup.find_all("img"):
        img_url = img.get("src") or img.get("data-src")
        if img_url and any(ext in img_url for ext in [".jpg", ".jpeg", ".png", ".webp"]):
            img_path = download_image(img_url, base_url)
            if img_path:
                images.append(img_path)

    # Extract tables
    tables = []
    for table in soup.find_all("table"):
        tables.append(str(table))

    # Detect chart-type elements
    svg_charts = soup.find_all("svg")
    canvas_charts = soup.find_all("canvas")
    if svg_charts or canvas_charts:
        chart_note = f"[Charts Detected: {len(svg_charts)} SVG, {len(canvas_charts)} Canvas]"
        main_text += f"\n\n{chart_note}"

    # Pros/Cons
    pros, cons = extract_pros_cons(soup)

    return {
        "text": main_text,
        "images": images,
        "tables": tables,
        "pros": pros,
        "cons": cons
    }


# content_scraper.py

from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

def extract_structured_content(html, base_url):
    soup = BeautifulSoup(html, "html.parser")

    # Extract images
    images = []
    for img in soup.find_all("img", src=True):
        img_url = urljoin(base_url, img['src'])
        images.append(img_url)

    # Extract tables (HTML only, no visual charts unless embedded)
    tables = []
    for table in soup.find_all("table"):
        tables.append(str(table))

    return {
        "images": images,
        "tables": tables
    }
