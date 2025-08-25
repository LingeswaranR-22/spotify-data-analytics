import glob
import os
import logging
import pandas as pd
import numpy as np
from utils import ensure_dir, write_csv, write_parquet

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

RAW_DIR = "data/raw"
PROC_DIR = "data/processed"

def latest(pattern: str) -> str:
    files = sorted(glob.glob(pattern))
    if not files:
        raise FileNotFoundError(f"No files matched: {pattern}")
    return files[-1]

def clean_and_join(tracks_path: str, audio_path: str, artists_path: str) -> pd.DataFrame:
    tracks = pd.read_csv(tracks_path)
    audio = pd.read_csv(audio_path)
    artists = pd.read_csv(artists_path)

    df = tracks.merge(audio, on="track_id", how="left")

    # Expand artists (first artist only for simplicity) and join artist attributes
    first_artist = tracks["artist_ids"].fillna("").str.split(",").str[0]
    df["primary_artist_id"] = first_artist
    df = df.merge(artists.rename(columns={
        "artist_id": "primary_artist_id"
    }), on="primary_artist_id", how="left")

    # Basic cleaning
    df["album_release_year"] = pd.to_datetime(df["album_release_date"], errors="coerce").dt.year
    num_cols = ["danceability","energy","loudness","speechiness","acousticness",
                "instrumentalness","liveness","valence","tempo","duration_ms","track_popularity"]
    for c in num_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # Feature engineering
    df["duration_min"] = df["duration_ms"] / 60000.0
    df["energy_valence_sum"] = df["energy"].fillna(0) + df["valence"].fillna(0)
    df["is_upbeat"] = (df["danceability"].fillna(0) > 0.65) & (df["energy"].fillna(0) > 0.65)
    df["genre_primary"] = df["artist_genres"].fillna("").str.split(",").str[0].str.strip().str.title()

    # Write
    ensure_dir(PROC_DIR)
    write_csv(df, os.path.join(PROC_DIR, "spotify_analytics_dataset.csv"))
    try:
        write_parquet(df, os.path.join(PROC_DIR, "spotify_analytics_dataset.parquet"))
    except Exception as e:
        logging.warning(f"Parquet write failed: {e}")

    return df

def compute_correlations(df: pd.DataFrame) -> pd.DataFrame:
    cols = ["danceability","energy","speechiness","acousticness","instrumentalness",
            "liveness","valence","tempo","duration_ms","track_popularity"]
    c = df[cols].corr(numeric_only=True)
    c = c.round(3)
    return c

def aggregates(df: pd.DataFrame) -> dict:
    by_genre = df.groupby("genre_primary", dropna=False)["track_id"].nunique().reset_index(name="track_count")                  .sort_values("track_count", ascending=False)
    feat_cols = ["danceability","energy","valence","tempo","track_popularity"]
    by_genre_feat = df.groupby("genre_primary", dropna=False)[feat_cols].mean(numeric_only=True).reset_index()
    by_artist = df.groupby(["primary_artist_id","artist_name"], dropna=False).agg(
        tracks=("track_id","nunique"),
        avg_popularity=("track_popularity","mean"),
        followers=("artist_followers","max"),
    ).reset_index().sort_values(["tracks","avg_popularity"], ascending=[False,False])
    return {
        "by_genre": by_genre,
        "by_genre_features": by_genre_feat,
        "by_artist": by_artist
    }

def main():
    tracks_path = latest(os.path.join(RAW_DIR, "tracks_*.csv"))
    audio_path = latest(os.path.join(RAW_DIR, "audio_features_*.csv"))
    artists_path = latest(os.path.join(RAW_DIR, "artists_*.csv"))
    df = clean_and_join(tracks_path, audio_path, artists_path)

    corr = compute_correlations(df)
    aggs = aggregates(df)

    corr_path = os.path.join(PROC_DIR, "correlations.csv")
    agg_genre_path = os.path.join(PROC_DIR, "genre_popularity.csv")
    agg_genre_feat_path = os.path.join(PROC_DIR, "genre_features_mean.csv")
    by_artist_path = os.path.join(PROC_DIR, "artist_summary.csv")

    corr.to_csv(corr_path)
    aggs["by_genre"].to_csv(agg_genre_path, index=False)
    aggs["by_genre_features"].to_csv(agg_genre_feat_path, index=False)
    aggs["by_artist"].to_csv(by_artist_path, index=False)

    print("Wrote:")
    print(" -", corr_path)
    print(" -", agg_genre_path)
    print(" -", agg_genre_feat_path)
    print(" -", by_artist_path)

if __name__ == "__main__":
    main()
