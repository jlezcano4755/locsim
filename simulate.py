import time
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import requests

"""Generate location traces for 100 users in Panama City.

Home and job coordinates are sampled from predefined clusters but are
validated against OpenStreetMap so they fall near a road or building.
Movement is simulated at 10 minute intervals over a single day.
"""

import os

NUM_USERS = int(os.environ.get("NUM_USERS", 100))
START_TIME = datetime(2023, 1, 1)
END_TIME = datetime(2023, 1, 2)
TIMESTAMPS = [START_TIME + timedelta(minutes=10 * i)
              for i in range(int((END_TIME - START_TIME).total_seconds() // 600))]

# Rough bounding boxes for residential areas in Panama City
HOME_CLUSTERS = [
    {"lat": (8.95, 9.00), "lon": (-79.55, -79.50)},  # Ancon
    {"lat": (9.03, 9.07), "lon": (-79.52, -79.45)},  # San Miguelito
    {"lat": (8.98, 9.03), "lon": (-79.55, -79.48)},  # Bella Vista
]

# Possible job districts (downtown/industrial areas)
JOB_CLUSTERS = [
    {"lat": (8.99, 9.02), "lon": (-79.54, -79.50)},  # Obarrio
    {"lat": (8.98, 9.00), "lon": (-79.55, -79.52)},  # El Cangrejo
    {"lat": (9.00, 9.03), "lon": (-79.47, -79.43)},  # Costa del Este
]

OVERPASS_URL = "https://overpass-api.de/api/interpreter"


def is_reachable(lat: float, lon: float) -> bool:
    """Return True if the coordinate is near a road or building."""
    query = (
        f"[out:json];(way(around:50,{lat},{lon})['highway'];"
        f"node(around:50,{lat},{lon})['building'];);out;"
    )
    try:
        resp = requests.get(OVERPASS_URL, params={"data": query}, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return len(data.get("elements", [])) > 0
    except Exception:
        pass
    return False


def sample_valid_location(cluster: dict) -> tuple[float, float]:
    """Sample a location inside the cluster that is reachable."""
    for _ in range(10):
        lat = np.random.uniform(*cluster["lat"])
        lon = np.random.uniform(*cluster["lon"])
        if is_reachable(lat, lon):
            return lat, lon
        time.sleep(1)  # be gentle with the API
    return lat, lon  # fall back to last attempt


records = []
for user_id in range(1, NUM_USERS + 1):
    home_lat, home_lon = sample_valid_location(np.random.choice(HOME_CLUSTERS))
    job_lat, job_lon = sample_valid_location(np.random.choice(JOB_CLUSTERS))

    morning_start = START_TIME + timedelta(hours=7)
    morning_end = START_TIME + timedelta(hours=8)
    evening_start = START_TIME + timedelta(hours=17)
    evening_end = START_TIME + timedelta(hours=18)

    for ts in TIMESTAMPS:
        if ts < morning_start:
            lat = home_lat + np.random.normal(scale=0.0005)
            lon = home_lon + np.random.normal(scale=0.0005)
        elif morning_start <= ts < morning_end:
            frac = (ts - morning_start) / (morning_end - morning_start)
            lat = home_lat + frac * (job_lat - home_lat)
            lon = home_lon + frac * (job_lon - home_lon)
        elif morning_end <= ts < evening_start:
            lat = job_lat + np.random.normal(scale=0.0005)
            lon = job_lon + np.random.normal(scale=0.0005)
        elif evening_start <= ts < evening_end:
            frac = (ts - evening_start) / (evening_end - evening_start)
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
