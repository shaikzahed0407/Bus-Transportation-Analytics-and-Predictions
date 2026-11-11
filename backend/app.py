"""
KSRTC Kalaburagi Division - BusPulse Backend API
Flask REST API connecting HTML/JS dashboards with Pandas Analytical Pipeline.
"""
import os
import sys
from pathlib import Path
import pandas as pd
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
# Add project root and backend directory to Python path
BACKEND_DIR = Path(__file__).resolve().parent
ROOT_DIR = BACKEND_DIR.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Import data management blueprint (upload, backup, history)
try:
    from backend.routes.data import bp as data_bp
except ImportError:
    from routes.data import bp as data_bp

try:
    from .data_loader import get_data, update_dataset
    from .analytics.demand import get_hourly_demand, get_peak_demand_stats
    from .analytics.stops import get_stop_rankings, get_gis_stops_geojson
    from .analytics.movement import get_top_corridors, get_corridor_directional_balance
    from .analytics.fleet import get_fleet_statistics, get_fleet_summary
    from .analytics.revenue import get_revenue_summary, get_revenue_by_route
    from .analytics.predictions import get_demand_forecast, simulate_what_if
    from .services.filters import apply_filters
    from .services.alerts import get_system_alerts
except ImportError:
    from data_loader import get_data, update_dataset
    from analytics.demand import get_hourly_demand, get_peak_demand_stats
    from analytics.stops import get_stop_rankings, get_gis_stops_geojson
    from analytics.movement import get_top_corridors, get_corridor_directional_balance
    from analytics.fleet import get_fleet_statistics, get_fleet_summary
    from analytics.revenue import get_revenue_summary, get_revenue_by_route
    from analytics.predictions import get_demand_forecast, simulate_what_if
    from services.filters import apply_filters
    from services.alerts import get_system_alerts

# Frontend path for serving dashboard
FRONTEND_DIR = BACKEND_DIR.parent / "frontend"
if not (FRONTEND_DIR / "index.html").exists():
    FRONTEND_DIR = BACKEND_DIR.parent

app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="")
CORS(app)  # Enable Cross-Origin Resource Sharing for file:// and localhost
app.register_blueprint(data_bp)

# Warm up data cache immediately when server starts
with app.app_context():
    print("Warming up KSRTC ticket cache in memory...")
    get_data()
    print("KSRTC Analytics Engine ready!")

@app.route("/")
def index():
    """Serves the dashboard index page."""
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/<path:path>")
def static_proxy(path):
    """Serves static files (HTML, CSS, JS)."""
    if (FRONTEND_DIR / path).exists():
        return send_from_directory(FRONTEND_DIR, path)
    if (BACKEND_DIR.parent / path).exists():
        return send_from_directory(BACKEND_DIR.parent, path)
    if not path.endswith(".html") and (FRONTEND_DIR / f"{path}.html").exists():
        return send_from_directory(FRONTEND_DIR, f"{path}.html")
    return send_from_directory(FRONTEND_DIR, "index.html")

# ══════════════════════════════════════════════════════════════════════════
# REST API ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════

def _get_filtered_df():
    """Extracts query parameters and applies unified slicing to the dataset."""
    df = get_data()
    window = request.args.get("window", "").lower().strip()
    start_hour = request.args.get("start_hour", type=int)
    end_hour = request.args.get("end_hour", type=int)

    # Map named transit windows
    if window == "morning":
        start_hour, end_hour = 6, 11
    elif window == "midday":
        start_hour, end_hour = 12, 16
    elif window == "evening":
        start_hour, end_hour = 17, 21
    elif window == "night":
        start_hour, end_hour = 22, 23

    bus_id = request.args.get("bus_id")
    route_name = request.args.get("route")
    stop_name = request.args.get("stop")

    shakti_param = request.args.get("shakti", "").lower().strip()
    shakti_only = None
    if shakti_param in ("true", "1", "yes", "shakti"):
        shakti_only = True
    elif shakti_param in ("false", "0", "no", "cash"):
        shakti_only = False

    return apply_filters(
        df,
        start_hour=start_hour,
        end_hour=end_hour,
        bus_id=bus_id,
        route_name=route_name,
        stop_name=stop_name,
        shakti_only=shakti_only
    )

@app.route("/api/v1/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "service": "KSRTC Kalaburagi BusPulse Analytics Engine",
        "division": "Kalaburagi / KKRTC",
        "records_loaded": len(get_data())
    })

@app.route("/api/v1/kpi/summary", methods=["GET"])
def kpi_summary():
    """Returns dynamic top-level KPIs based on active filters."""
    df = _get_filtered_df()
    if df.empty:
        return jsonify({
            "total_passengers": 0,
            "total_tickets": 0,
            "cash_collected": 0.0,
            "shakti_subsidy_claim": 0.0,
            "total_gross_fare": 0.0,
            "active_fleet_buses": 0,
            "shakti_share_pct": 0.0,
            "active_stops": 0,
            "avg_pax_per_trip": 0.0,
            "avg_fare_per_trip": 0.0,
            "collection_rate_pct": 0.0,
            "peak_hour": "—",
            "peak_hour_pax": 0,
            "busiest_corridor": "—",
            "busiest_origin": "—",
            "busiest_origin_pax": 0,
            "busiest_dest": "—",
            "busiest_dest_pax": 0
        })

    total_pax = int(df['passengers'].sum())
    total_tkts = len(df)
    total_collected = float(df['collected_fare'].sum())
    total_subsidy = float(df['subsidy_fare'].sum())
    total_gross = total_collected + total_subsidy
    active_buses = int(df['waybill_id'].nunique())

    # Active stops in filtered slice
    all_stops = pd.concat([df['from_stop_clean'], df['to_stop_clean']]).dropna()
    active_stops = int(all_stops.nunique())

    # Dynamic peak hour & corridors
    hourly_pax = df.groupby('hour')['passengers'].sum()
    peak_hr_val = int(hourly_pax.idxmax()) if not hourly_pax.empty else 12
    peak_pax_val = int(hourly_pax.max()) if not hourly_pax.empty else 0
    period = "AM" if peak_hr_val < 12 else "PM"
    display_hr = 12 if peak_hr_val in [0, 12] else peak_hr_val % 12
    peak_label = f"{display_hr}:00 {period}"

    top_corridors = df.groupby('route')['passengers'].sum().sort_values(ascending=False)
    busiest_corridor = str(top_corridors.index[0]) if not top_corridors.empty else "—"

    top_origins = df.groupby('from_stop_clean')['passengers'].sum().sort_values(ascending=False)
    busiest_origin = str(top_origins.index[0]) if not top_origins.empty else "—"
    busiest_origin_pax = int(top_origins.iloc[0]) if not top_origins.empty else 0

    top_dests = df.groupby('to_stop_clean')['passengers'].sum().sort_values(ascending=False)
    busiest_dest = str(top_dests.index[0]) if not top_dests.empty else "—"
    busiest_dest_pax = int(top_dests.iloc[0]) if not top_dests.empty else 0

    avg_pax_trip = round(total_pax / active_buses, 1) if active_buses > 0 else 0
    avg_fare_trip = round(total_collected / active_buses, 1) if active_buses > 0 else 0
    collection_rate = round((total_collected / total_gross * 100), 1) if total_gross > 0 else 0
    shakti_share = round((total_subsidy / total_gross * 100), 1) if total_gross > 0 else 0

    return jsonify({
        "total_passengers": total_pax,
        "total_tickets": total_tkts,
        "cash_collected": round(total_collected, 2),
        "shakti_subsidy_claim": round(total_subsidy, 2),
        "total_gross_fare": round(total_gross, 2),
        "active_fleet_buses": active_buses,
        "active_stops": active_stops,
        "avg_pax_per_trip": avg_pax_trip,
        "avg_fare_per_trip": avg_fare_trip,
        "collection_rate_pct": collection_rate,
        "shakti_share_pct": shakti_share,
        "peak_hour": peak_label,
        "peak_hour_pax": peak_pax_val,
        "busiest_corridor": busiest_corridor,
        "busiest_origin": busiest_origin,
        "busiest_origin_pax": busiest_origin_pax,
        "busiest_dest": busiest_dest,
        "busiest_dest_pax": busiest_dest_pax
    })

@app.route("/api/v1/analytics/hourly", methods=["GET"])
def hourly_analytics():
    """Returns hourly ridership, trips, and revenue."""
    df = _get_filtered_df()
    return jsonify({
        "hourly": get_hourly_demand(df),
        "peak_stats": get_peak_demand_stats(df)
    })

@app.route("/api/v1/analytics/routes", methods=["GET"])
def routes_analytics():
    """Returns top corridors and directional balance."""
    df = _get_filtered_df()
    limit = int(request.args.get("limit", 20))
    return jsonify({
        "top_routes": get_top_corridors(df, limit=limit),
        "directional_balance": get_corridor_directional_balance(df)
    })

@app.route("/api/v1/analytics/stops", methods=["GET"])
def stops_analytics():
    """Returns stop rankings and GIS GeoJSON features."""
    df = _get_filtered_df()
    limit = int(request.args.get("limit", 20))
    return jsonify({
        "stops": get_stop_rankings(df, limit=limit),
        "geojson": get_gis_stops_geojson(df)
    })

@app.route("/api/v1/analytics/buses", methods=["GET"])
def buses_analytics():
    """Returns 47-bus fleet breakdown by Waybill."""
    df = _get_filtered_df()
    return jsonify({
        "fleet": get_fleet_statistics(df),
        "summary": get_fleet_summary(df)
    })

@app.route("/api/v1/analytics/revenue", methods=["GET"])
def revenue_analytics():
    """Returns cash collections and Shakti state subsidy receivable."""
    df = _get_filtered_df()
    return jsonify({
        "summary": get_revenue_summary(df),
        "by_route": get_revenue_by_route(df, limit=20)
    })

@app.route("/api/v1/analytics/alerts", methods=["GET"])
def alerts_analytics():
    """Returns system alerts and diagnostic notices."""
    df = _get_filtered_df()
    return jsonify({
        "alerts": get_system_alerts(df)
    })

@app.route("/api/v1/ai/forecast", methods=["GET"])
def ai_forecast():
    """Returns AI predictive demand forecast with confidence intervals."""
    df = get_data()
    return jsonify(get_demand_forecast(df))

@app.route("/api/v1/ai/simulate", methods=["POST"])
def ai_simulate():
    """
    Simulates What-If scenario based on parameters.
    JSON Body: {"growth_pct": float, "shakti_pct": float, "tariff_pct": float}
    """
    df = get_data()
    data = request.get_json(silent=True) or {}
    growth = float(data.get("growth_pct", 0.0))
    shakti = float(data.get("shakti_pct", 75.0))
    tariff = float(data.get("tariff_pct", 0.0))

    simulation_result = simulate_what_if(
        df,
        ridership_growth_pct=growth,
        shakti_share_pct=shakti,
        tariff_adj_pct=tariff
    )
    return jsonify(simulation_result)

if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 5000))
    print(f"\n=======================================================")
    print(f"🚌 KSRTC BusPulse Analytics Server running at:")
    print(f"👉 http://{host}:{port}")
    print(f"=======================================================\n")
    app.run(host=host, port=port, debug=False)

