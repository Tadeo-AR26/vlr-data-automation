# 🎮 VLR.gg Data Automation API

An automated data pipeline and RESTful API designed to track the **Valorant competitive ecosystem**. This project scrapes, processes, and serves real-time data from vlr.gg, focusing on teams, professional players, match histories, and tournament brackets like the **Masters Santiago 2026**.

## 🚀 Overview

This repository demonstrates a complete **Backend Engineering** workflow: from robust web scraping with anti-bot bypass to a persistent relational database and a high-performance API. It is designed to be self-sustaining, using internal scheduling to keep the data fresh without manual intervention.

## 🛠️ Tech Stack

* **Language:** Python 3.11+
* **API Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Asynchronous, high-performance).
* **Database:** **SQLite** with persistent volumes for reliable data storage.
* **Scraping:** [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) & [Cloudscraper](https://github.com/VeNoMouS/cloudscraper).
* **Automation:** **APScheduler** integrated into the FastAPI lifespan for background synchronization.
* **Deployment:** [Railway](https://railway.app/) with automated CI/CD from GitHub.

## 📂 Project Structure

```text
vlr-data-automation/
├── api/
│   ├── main.py           # FastAPI entry point & Lifespan logic
│   └── routers/          # Modular API endpoints (matches, players, etc.)
├── src/
│   ├── scrapers/         # Specific logic for each VLR section
│   └── utils/
│       └── database_manager.py  # SQLite connection & CRUD logic
├── data/                 # Persistent SQLite database (Mounted Volume)
├── sync_activity.py      # Core synchronization script (The Scraper)
├── Procfile              # Railway deployment instructions
├── requirements.txt      # Project dependencies
├── runtime.txt           # Python version specification
└── README.md             # This documentation
```

## 📋 Features & Roadmap

* **[x] Persistent Storage:** Migrated from flat JSON files to a relational **SQLite** database for better query performance and data integrity.
* **[x] Internal Automation:** Implemented **APScheduler** to run the `sync_activity` every 12 hours directly from the API.
* **[x] Modular Routing:** Organized using `APIRouter` for clean and scalable code.
* **[x] Cloud Deployment:** Fully functional on **Railway** using persistent volumes and environment variables.
* **[x] Masters Santiago 2026:** Initial support and historical data loading for VCT tournaments.

## 🔌 API Usage Examples

Once the API is running, you can access the interactive documentation at `/docs`.

### Get Recent Matches
```bash
curl -X 'GET' '[https://your-app.railway.app/matches/recent](https://your-app.railway.app/matches/recent)'
```

### Get Team Details
```bash
curl -X 'GET' '[https://tu-app.railway.app/teams/1234](https://tu-app.railway.app/teams/1234)'
```

### Response Format (Example)
```json
{
  "id": "17",
  "name": "Gen.G",
  "tag": "GEN",
  "country": "South Korea",
  "vlr_rank": 4,
  "last_updated": "2026-03-26 14:34:28",
  "roster": [
    {
      "id": "11600",
      "ign": "Foxy9"
    },
    {
      "id": "25017",
      "ign": "Ash"
    },
    {
      "id": "34974",
      "ign": "Karon"
    },
    {
      "id": "4560",
      "ign": "peri"
    },
    {
      "id": "4562",
      "ign": "solo"
    },
    {
      "id": "773",
      "ign": "Lakia"
    },
    {
      "id": "9196",
      "ign": "t3xture"
    }
  ],
  "upcoming_matches": [
    "644652"
  ],
  "recent_matches": [
    "595654",
    "595652",
    "595644",
    "595633",
    "590638"
  ]
}
```

## ⚙️ Installation & Deployment

### Local Setup
1. Clone the repository and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Create a `.env` file in the root directory:
   ```text
   DATABASE_PATH=data/vlr_database.sqlite
   ```
3. Run the API locally:
   ```bash
   uvicorn api.main:app --reload
   ```

### Railway Deployment
1. Connect this repository to **Railway**.
2. Add a **Volume** and mount it at `/data`.
3. Set the variable `DATABASE_PATH=/data/vlr_database.sqlite`.
4. Railway detectará el `Procfile` y arrancará el servicio automáticamente.

## ⚖️ Legal Disclaimer
This project is for educational and personal portfolio purposes only. All data is sourced from vlr.gg. The scraping logic respects the site's structure and aims to minimize server load by using cached data and background updates.