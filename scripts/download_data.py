#!/usr/bin/env python3
"""
scripts/download_data.py
========================
Automated dataset acquisition script for the Electric Vehicle Market Analysis project.
Downloads authentic public EV datasets from established sources into data/raw/.

Sources:
1. OpenEV Data canonical specifications (v1.24.0):
   URL: https://github.com/open-ev-data/open-ev-data-dataset/releases/download/v1.24.0/open-ev-data-v1.24.0.csv
   License: CC-BY-4.0
   Coverage: Vehicle models, variants, battery capacity (gross/net), battery chemistry (LFP, NMC, NCA),
             system power, torque, range (WLTP/EPA), charging specs.

2. Electric Car Pricing & Efficiency Dataset (EV Database mirror):
   URL: https://raw.githubusercontent.com/bhavyapandya/EV-Market-Segmentation-Analysis/main/ElectricCarData_Clean.csv
   License: CC0 Public Domain
   Coverage: Vehicle brand, model, price in EUR, energy efficiency (Wh/km), acceleration, body style.

3. International Energy Agency (IEA) Global EV Data 2024:
   URL: https://raw.githubusercontent.com/Shahbaz123456-ai/Global-EV-Sales/main/IEA%20Global%20EV%20Data%202024.csv
   License: Creative Commons Attribution (CC BY 4.0)
   Coverage: Historical EV sales, stock, and charging infrastructure by region/country, vehicle mode, and year.
"""

import os
import sys
import urllib.request
import urllib.error
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

RAW_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "raw")

DATASETS = [
    {
        "name": "OpenEV Technical Specifications",
        "filename": "open_ev_data_specs.csv",
        "url": "https://github.com/open-ev-data/open-ev-data-dataset/releases/download/v1.24.0/open-ev-data-v1.24.0.csv",
        "source": "OpenEV Data Canonical Repository (v1.24.0)",
        "license": "CC-BY-4.0"
    },
    {
        "name": "Electric Car Pricing & Efficiency",
        "filename": "ev_specs_pricing_efficiency.csv",
        "url": "https://raw.githubusercontent.com/bhavyapandya/EV-Market-Segmentation-Analysis/main/ElectricCarData_Clean.csv",
        "source": "EV-Database / Kaggle CC0 Public Mirror",
        "license": "CC0: Public Domain"
    },
    {
        "name": "IEA Global EV Sales & Market Share 2024",
        "filename": "iea_global_ev_sales_2024.csv",
        "url": "https://raw.githubusercontent.com/Shahbaz123456-ai/Global-EV-Sales/main/IEA%20Global%20EV%20Data%202024.csv",
        "source": "International Energy Agency (IEA) Global EV Outlook",
        "license": "CC BY 4.0"
    }
]


def download_file(url: str, dest_path: str) -> bool:
    """Download a file with SSL verification via certifi or fallback to curl."""
    logger.info(f"Downloading from {url} to {dest_path}...")
    try:
        import ssl
        try:
            import certifi
            context = ssl.create_default_context(cafile=certifi.where())
        except Exception:
            context = ssl._create_unverified_context()
        
        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=context, timeout=30) as response, open(dest_path, "wb") as out_file:
            data = response.read()
            out_file.write(data)
        size_kb = os.path.getsize(dest_path) / 1024
        logger.info(f"Successfully downloaded {dest_path} ({size_kb:.1f} KB)")
        return True
    except Exception as e:
        logger.warning(f"Python download failed ({e}), falling back to curl...")
        import subprocess
        res = subprocess.run(["curl", "-sL", "-A", "Mozilla/5.0", url, "-o", dest_path])
        if res.returncode == 0 and os.path.exists(dest_path) and os.path.getsize(dest_path) > 100:
            size_kb = os.path.getsize(dest_path) / 1024
            logger.info(f"Successfully downloaded via curl: {dest_path} ({size_kb:.1f} KB)")
            return True
        logger.error(f"Both urllib and curl failed for {url}")
        return False


def main():
    os.makedirs(RAW_DIR, exist_ok=True)
    all_success = True
    for item in DATASETS:
        dest = os.path.join(RAW_DIR, item["filename"])
        if os.path.exists(dest) and os.path.getsize(dest) > 100:
            logger.info(f"File {item['filename']} already exists ({os.path.getsize(dest)} bytes). Skipping download.")
            continue
        success = download_file(item["url"], dest)
        if not success:
            all_success = False

    if not all_success:
        logger.warning("One or more downloads failed. Please check network permissions.")
        sys.exit(1)
    else:
        logger.info("All raw datasets downloaded successfully.")


if __name__ == "__main__":
    main()
