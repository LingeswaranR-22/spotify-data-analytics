import argparse
import os
import pandas as pd
from utils import write_parquet

def main():
    parser = argparse.ArgumentParser(description="Load processed data to target format")
    parser.add_argument("--to", choices=["csv","parquet"], default="csv")
    args = parser.parse_args()

    df = pd.read_csv("data/processed/spotify_analytics_dataset.csv")

    if args.to == "parquet":
        write_parquet(df, "data/processed/spotify_analytics_dataset.parquet")
        print("Saved parquet to data/processed/spotify_analytics_dataset.parquet")
    else:
        # already CSV
        print("CSV already present at data/processed/spotify_analytics_dataset.csv")

if __name__ == "__main__":
    main()
