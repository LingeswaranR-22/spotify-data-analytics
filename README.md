# 🎵 Spotify Data Analytics (by Lingeswaran R)

End-to-end Spotify Data Analytics project using Python, Spotify Web API, and Power BI. Includes ETL pipeline, data cleaning, feature engineering, and insights on music trends & audio features.
#data-engineering #data-analytics #spotify #python #ETL

## ✨ What you get
- **Python ETL** using Spotipy (Spotify Web API)
- Cleaned **analytics-ready datasets** (CSV/Parquet)
- Feature engineering & **correlations** to explain what makes a hit
- Ready-made **notebook** for quick exploration
- **Dashboard spec** and sample visuals to replicate in Power BI

## 🧱 Project structure
```
spotify-data-analytics/
├─ README.md
├─ requirements.txt
├─ LICENSE
├─ .gitignore
├─ .env.example
├─ src/
│  ├─ extract_data.py
│  ├─ transform_data.py
│  ├─ load_data.py
│  └─ utils.py
├─ notebooks/
│  └─ spotify_exploration.ipynb
├─ data/
│  ├─ raw/
│  └─ processed/
├─ reports/
│  └─ dashboard_spec.md
└─ .github/workflows/
   └─ ci.yml
```

## 🚀 Setup

1) **Create a Spotify app**
- Go to https://developer.spotify.com/dashboard
- Create an app, copy **Client ID** and **Client Secret**
- Add a Redirect URI: `http://localhost:9090/callback` (Settings → Redirect URIs)

2) **Clone & install**
```bash
git clone https://github.com/LingeswaranR-22/spotify-data-analytics.git
cd spotify-data-analytics
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

3) **Set environment**
```bash
cp .env.example .env
# Fill SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET
```

## ▶️ Run the pipeline
**Extract (API → CSV):**
```bash
python src/extract_data.py --markets IN US GB --playlists "Top 50 - Global" "Viral 50 - Global"
```

**Transform (clean, join, features):**
```bash
python src/transform_data.py
```

**Load (optional—parquet, sample Snowflake stub):**
```bash
python src/load_data.py --to parquet
```

Data will appear under `data/raw` and `data/processed`.

## 🔎 What it pulls
- Tracks from curated playlists (e.g., *Top 50 - Global*, *Viral 50 - Global*).
- Track **audio features** (danceability, energy, valence, tempo, acousticness, etc.).
- Artist details (name, popularity, genres).

## 📈 Example questions answered
- Which **audio features** correlate with popularity?
- What **genres** dominate top charts?
- Which artists are **breaking out** across markets?
- What **tempo/energy** ranges are most common among hits?

## 🗺️ Dashboard (Power BI / Looker)
Create visuals on `data/processed/` outputs:
- **Genre Popularity** (bar/treemap)
- **Audio Features vs Popularity** (scatter)
- **Artist Popularity vs Followers** (bubble)
- **Tempo distributions** (histogram)

A dashboard plan is in `reports/dashboard_spec.md`.

## 🧪 CI (lightweight)
A tiny GitHub Action runs flake checks & unit smoke tests on push.

## 📝 Notes on auth
- Most public playlist/track data works with **Client Credentials** (no user login).
- If you need **user** playlists, flip the `--user-auth` flag and complete the browser login once.

---

**Author:** Lingeswaran R  
**License:** MIT
