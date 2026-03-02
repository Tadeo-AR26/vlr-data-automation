# VLR.gg Data Automation API

An automated data pipeline and API designed to track the **Valorant competitive ecosystem** by scraping data from vlr.gg. This project focuses on gathering insights into teams, professional players, match histories, and regional rankings.

## 🚀 Overview

This repository serves as a portfolio project that demonstrates the integration of **web scraping**, **data automation**, and **API development**. It is built with a focus on clean architecture and sustainable data collection practices, tailored for the high-frequency updates typical of the Valorant Champions Tour (VCT) and regional Challengers scenes.

## 🛠️ Tech Stack

* **Language:** Python 3.12+
* **Scraping:** [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) & [Cloudscraper](https://github.com/VeNoMouS/cloudscraper) (handling SSR content and Cloudflare challenges).
* **API Framework:** [FastAPI](https://fastapi.tiangolo.com/) for high-performance data delivery.
* **Automation:** GitHub Actions for scheduled "Flat Data" updates.
* **Storage:** JSON-based data storage for lightweight, serverless operation.

## 📂 Project Structure

```text
vlr-data-automation/
├── .github/workflows/    # Automated scraping schedules
├── src/                  # Core logic: Scrapers and HTML parsers
├── data/                 # Auto-generated JSON datasets
├── api/                  # FastAPI implementation
├── requirements.txt      # Project dependencies
└── README.md             # Project documentation
```

## 📋 Features & Roadmap
```text
[x] Initial Research: Identified URL patterns for matches, players, and rankings.

[x] Project Scaffolding: Environment setup and repository architecture.

[ ] Core Scraper: Implementing robust extraction logic for player stats (e.g., 90d/60d/30d timespans).

[ ] Tournament Logic: Parsing complex bracket metadata (Middle Round, Lower Round, etc.).

[ ] Automation: Deploying GitHub Actions to refresh datasets every 6-12 hours.

[ ] API Layer: Creating endpoints to serve local JSON data as a RESTful service.
```

## ⚖️ Legal Disclaimer
This project is for educational and personal portfolio purposes only. All data is sourced from vlr.gg. The scraping logic respects the site's structure and aims to minimize server load by using cached data and scheduled updates rather than real-time requests.