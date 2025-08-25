# Dashboard Spec (Power BI / Looker)

## Pages
1) Overview
   - KPI cards: #Tracks, #Artists, Avg Popularity, Median Tempo
   - Genre share (Top 10)
   - Popularity vs Danceability scatter

2) Audio DNA
   - Distributions: tempo, energy, valence, danceability
   - Feature correlation heatmap (precomputed in processed/correlations.csv)

3) Artists
   - Bubble chart: Artist Popularity vs Followers (size=track count)
   - Table: Top Artists by Popularity

4) Markets
   - Small multiples or slicers by market (IN, US, GB, Global)
