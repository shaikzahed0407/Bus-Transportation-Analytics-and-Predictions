"""
KSRTC Kalaburagi Division - Bus Stop Intelligence & GIS
Aggregates stop boardings, revenue generation, and coordinates for GIS mapping.
"""
import pandas as pd
from typing import List, Dict, Any

# Verified GIS Coordinates & Roles for Kalaburagi Urban & Sub-urban Hubs
KALABURAGI_GIS_HUBS = {
    "CBS (Central Bus Stand)": {"lat": 17.3368, "lng": 76.8285, "role": "Intercity & Urban Terminal Hub", "color": "#8B5CF6"},
    "Central Bus Stand": {"lat": 17.3368, "lng": 76.8285, "role": "Intercity & Urban Terminal Hub", "color": "#8B5CF6"},
    "Budhavihar": {"lat": 17.3620, "lng": 76.8710, "role": "Major Residential & Tourist Terminal", "color": "#10B981"},
    "Supermarket": {"lat": 17.3328, "lng": 76.8340, "role": "Central Commercial & Retail Centre", "color": "#F59E0B"},
    "Sedam Road": {"lat": 17.3160, "lng": 76.8530, "role": "Industrial & Institutional Corridor", "color": "#3B82F6"},
    "Ruknuddin Dargah": {"lat": 17.3450, "lng": 76.8420, "role": "Pilgrimage & Heritage Transit Hub", "color": "#EC4899"},
    "SVP Circle": {"lat": 17.3340, "lng": 76.8385, "role": "Central Business District Junction", "color": "#6366F1"},
    "Madiwala Vritta": {"lat": 17.3290, "lng": 76.8210, "role": "Dense Residential Connector", "color": "#14B8A6"},
    "Railway Station": {"lat": 17.3305, "lng": 76.8412, "role": "Intermodal Rail-Bus Interchange", "color": "#EF4444"},
    "High Court Bench": {"lat": 17.3680, "lng": 76.8600, "role": "Judicial Complex Link", "color": "#8B5CF6"},
    "Gulbarga University": {"lat": 17.2950, "lng": 76.8580, "role": "Higher Education Campus", "color": "#10B981"},
    "Ram Mandir Circle": {"lat": 17.3410, "lng": 76.8310, "role": "Urban Neighborhood Node", "color": "#F59E0B"},
    "Aland Check Post": {"lat": 17.3710, "lng": 76.8120, "role": "Northern Suburban Gateway", "color": "#06B6D4"},
    "Old Hospital": {"lat": 17.3280, "lng": 76.8360, "role": "Civic & Healthcare Node", "color": "#8B5CF6"},
    "Rashtrapati Chowk": {"lat": 17.3350, "lng": 76.8320, "role": "City Central Traffic Circle", "color": "#F59E0B"},
    "Jagat Circle": {"lat": 17.3315, "lng": 76.8370, "role": "Commercial Arterial Junction", "color": "#10B981"},
    "KBN Dargah": {"lat": 17.3480, "lng": 76.8450, "role": "Heritage & University Corridor", "color": "#EC4899"},
    "Nehru Gunj": {"lat": 17.3390, "lng": 76.8460, "role": "Wholesale Commercial Market", "color": "#F59E0B"},
    "Taj Sultanpur": {"lat": 17.2910, "lng": 76.8290, "role": "Southern Industrial Fringe", "color": "#3B82F6"}
}

def get_stop_rankings(df: pd.DataFrame, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Ranks bus stops by passenger boardings and ticket fare collected.
    """
    grouped = df.groupby('from_stop_clean').agg(
        boardings=('passengers', 'sum'),
        tickets=('ticket_number', 'count'),
        collected=('collected_fare', 'sum'),
        subsidy=('subsidy_fare', 'sum'),
        totalFare=('total_fare', 'sum')
    ).reset_index()

    grouped = grouped.sort_values('boardings', ascending=False)
    if limit:
        grouped = grouped.head(limit)

    results = []
    for _, row in grouped.iterrows():
        name = row['from_stop_clean']
        gis_info = KALABURAGI_GIS_HUBS.get(name, {
            "lat": 17.3370,
            "lng": 76.8380,
            "role": "Local Stop",
            "color": "#71717A"
        })

        results.append({
            "stop": name,
            "boardings": int(row['boardings']),
            "tickets": int(row['tickets']),
            "collected": float(round(row['collected'], 2)),
            "subsidy": float(round(row['subsidy'], 2)),
            "totalFare": float(round(row['totalFare'], 2)),
            "lat": gis_info["lat"],
            "lng": gis_info["lng"],
            "role": gis_info["role"],
            "color": gis_info["color"]
        })

    return results

def get_gis_stops_geojson(df: pd.DataFrame) -> Dict[str, Any]:
    """Returns GeoJSON FeatureCollection for Leaflet map integration."""
    stops = get_stop_rankings(df, limit=30)
    features = []

    for s in stops:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [s["lng"], s["lat"]]
            },
            "properties": {
                "name": s["stop"],
                "boardings": s["boardings"],
                "collected": s["collected"],
                "role": s["role"],
                "color": s["color"]
            }
        })

    return {
        "type": "FeatureCollection",
        "features": features
    }

