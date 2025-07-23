import numpy as np
import pandas as pd
from datetime import datetime, timedelta

NUM_USERS = 100
start_time = datetime(2023, 1, 1)
end_time = datetime(2023, 1, 2)

# timestamps every 10 minutes
timestamps = [start_time + timedelta(minutes=10*i) for i in range(int((end_time - start_time).total_seconds() // 600))]

# approximate location clusters within Panama City
home_clusters = [
    {"lat": (8.95, 8.98), "lon": (-79.55, -79.50)},
    {"lat": (8.99, 9.02), "lon": (-79.55, -79.50)},
    {"lat": (8.98, 9.03), "lon": (-79.60, -79.55)},
]

job_cluster = {"lat": (9.05, 9.10), "lon": (-79.55, -79.45)}

records = []

for user_id in range(1, NUM_USERS + 1):
    home_c = np.random.choice(home_clusters)
    home_lat = np.random.uniform(*home_c["lat"])
    home_lon = np.random.uniform(*home_c["lon"])

    job_lat = np.random.uniform(*job_cluster["lat"])
    job_lon = np.random.uniform(*job_cluster["lon"])

    morning_commute_start = start_time + timedelta(hours=5)
    morning_commute_end = start_time + timedelta(hours=7)
    evening_commute_start = start_time + timedelta(hours=17)
    evening_commute_end = start_time + timedelta(hours=19)

    for ts in timestamps:
        if ts < morning_commute_start:
            lat = home_lat + np.random.normal(scale=0.0005)
            lon = home_lon + np.random.normal(scale=0.0005)
        elif morning_commute_start <= ts < morning_commute_end:
            frac = (ts - morning_commute_start) / (morning_commute_end - morning_commute_start)
            lat = home_lat + frac * (job_lat - home_lat)
            lon = home_lon + frac * (job_lon - home_lon)
        elif morning_commute_end <= ts < evening_commute_start:
            lat = job_lat + np.random.normal(scale=0.0005)
            lon = job_lon + np.random.normal(scale=0.0005)
        elif evening_commute_start <= ts < evening_commute_end:
            frac = (ts - evening_commute_start) / (evening_commute_end - evening_commute_start)
            lat = job_lat + frac * (home_lat - job_lat)
            lon = job_lon + frac * (home_lon - job_lon)
        else:
            lat = home_lat + np.random.normal(scale=0.0005)
            lon = home_lon + np.random.normal(scale=0.0005)

        records.append({
            "user_id": user_id,
            "timestamp": ts,
            "latitude": lat,
            "longitude": lon,
        })

trace_df = pd.DataFrame(records)
print(trace_df.head())

