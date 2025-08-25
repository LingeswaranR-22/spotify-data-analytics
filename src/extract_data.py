import os
import argparse
import logging
from typing import List, Dict
import pandas as pd
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth

from utils import ensure_dir, ts, write_csv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def get_spotify_client(user_auth: bool=False) -> spotipy.Spotify:
    load_dotenv()
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:9090/callback")
    if not client_id or not client_secret:
        raise RuntimeError("Missing SPOTIFY_CLIENT_ID or SPOTIFY_CLIENT_SECRET in environment/.env")

    if user_auth:
        scope = "playlist-read-private playlist-read-collaborative"
        auth_manager = SpotifyOAuth(client_id=client_id, client_secret=client_secret,
                                    redirect_uri=redirect_uri, scope=scope, open_browser=True,
                                    cache_path=".cache-spotify")
    else:
        auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)

    return spotipy.Spotify(auth_manager=auth_manager)

def search_playlist_id(sp: spotipy.Spotify, query: str) -> str:
    results = sp.search(q=query, type="playlist", limit=1)
    items = results.get("playlists", {}).get("items", [])
    if not items:
        raise RuntimeError(f"No playlist found for query: {query}")
    return items[0]["id"]

def fetch_playlist_tracks(sp: spotipy.Spotify, playlist_id: str) -> pd.DataFrame:
    tracks = []
    results = sp.playlist_items(playlist_id, additional_types=["track"], limit=100)
    while results:
        for item in results["items"]:
            track = item.get("track") or {}
            if not track:
                continue
            tracks.append({
                "track_id": track.get("id"),
                "track_name": track.get("name"),
                "track_popularity": track.get("popularity"),
                "album_id": (track.get("album") or {}).get("id"),
                "album_name": (track.get("album") or {}).get("name"),
                "album_release_date": (track.get("album") or {}).get("release_date"),
                "artist_ids": ",".join([a.get("id") for a in (track.get("artists") or []) if a.get("id")]),
                "artist_names": ", ".join([a.get("name") for a in (track.get("artists") or []) if a.get("name")]),
            })
        if results.get("next"):
            results = sp.next(results)
        else:
            results = None
    return pd.DataFrame(tracks).drop_duplicates(subset=["track_id"]).reset_index(drop=True)

def fetch_audio_features(sp: spotipy.Spotify, track_ids: List[str]) -> pd.DataFrame:
    feats = []
    BATCH = 100
    for i in range(0, len(track_ids), BATCH):
        batch = track_ids[i:i+BATCH]
        af = sp.audio_features(batch)
        for f in af:
            if not f or not f.get("id"):
                continue
            feats.append({
                "track_id": f["id"],
                "danceability": f.get("danceability"),
                "energy": f.get("energy"),
                "key": f.get("key"),
                "loudness": f.get("loudness"),
                "mode": f.get("mode"),
                "speechiness": f.get("speechiness"),
                "acousticness": f.get("acousticness"),
                "instrumentalness": f.get("instrumentalness"),
                "liveness": f.get("liveness"),
                "valence": f.get("valence"),
                "tempo": f.get("tempo"),
                "duration_ms": f.get("duration_ms"),
                "time_signature": f.get("time_signature"),
            })
    return pd.DataFrame(feats)

def fetch_artists(sp: spotipy.Spotify, artist_ids: List[str]) -> pd.DataFrame:
    seen = set()
    ids = [a for a in artist_ids if a and a not in seen and not seen.add(a)]
    rows = []
    BATCH = 50
    for i in range(0, len(ids), BATCH):
        batch = ids[i:i+BATCH]
        res = sp.artists(batch)
        for a in res.get("artists", []):
            rows.append({
                "artist_id": a.get("id"),
                "artist_name": a.get("name"),
                "artist_popularity": a.get("popularity"),
                "artist_followers": (a.get("followers") or {}).get("total"),
                "artist_genres": ", ".join(a.get("genres") or []),
            })
    return pd.DataFrame(rows)

def main():
    parser = argparse.ArgumentParser(description="Extract Spotify data to CSV")
    parser.add_argument("--markets", nargs="*", default=["Global"], help="Market tags for labeling (no API filter)")
    parser.add_argument("--playlists", nargs="+", default=["Top 50 - Global", "Viral 50 - Global"], help="Playlist names to search & extract")
    parser.add_argument("--user-auth", action="store_true", help="Use user OAuth (needed for private user playlists)")
    args = parser.parse_args()

    sp = get_spotify_client(user_auth=args.user_auth)

    all_tracks = []
    all_audio = []
    all_artists = []

    for market in args.markets:
        for pl_name in args.playlists:
            logging.info(f"Resolving playlist id for '{pl_name}'")
            pl_id = search_playlist_id(sp, pl_name)
            logging.info(f"Fetching tracks for {pl_name} ({pl_id})")
            df_tracks = fetch_playlist_tracks(sp, pl_id)
            df_tracks["market"] = market
            df_tracks["source_playlist"] = pl_name
            all_tracks.append(df_tracks)

            if not df_tracks.empty:
                df_audio = fetch_audio_features(sp, df_tracks["track_id"].dropna().tolist())
                all_audio.append(df_audio)

                artist_ids = []
                for ids in df_tracks["artist_ids"].dropna().tolist():
                    artist_ids.extend(ids.split(","))
                if artist_ids:
                    df_artists = fetch_artists(sp, artist_ids)
                    all_artists.append(df_artists)

    tracks = pd.concat(all_tracks, ignore_index=True) if all_tracks else pd.DataFrame()
    audio = pd.concat(all_audio, ignore_index=True) if all_audio else pd.DataFrame()
    artists = pd.concat(all_artists, ignore_index=True) if all_artists else pd.DataFrame()

    ensure_dir("data/raw")
    ts_suffix = ts()
    if not tracks.empty:
        write_csv(tracks, f"data/raw/tracks_{ts_suffix}.csv")
    if not audio.empty:
        write_csv(audio, f"data/raw/audio_features_{ts_suffix}.csv")
    if not artists.empty:
        write_csv(artists, f"data/raw/artists_{ts_suffix}.csv")

    logging.info("Extraction complete. Files saved under data/raw")

if __name__ == "__main__":
    main()
