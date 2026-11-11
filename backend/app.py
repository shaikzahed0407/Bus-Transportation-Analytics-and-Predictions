"""
KSRTC Kalaburagi Division - BusPulse Backend API
Flask REST API connecting HTML/JS dashboards with Pandas Analytical Pipeline.
"""
import os
import sys
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
# Import data management blueprint (upload, backup, history)
from backend.routes.data import bp as data_bp

# Add backend directory to Python path
BACKEND_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BACKEND_DIR))

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
    """Returns top-level KPIs for Overview dashboard."""
    df = get_data()
    total_pax = int(df['passengers'].sum())
    total_tkts = len(df)
    total_collected = float(df['collected_fare'].sum())
    total_subsidy = float(df['subsidy_fare'].sum())
    total_gross = total_collected + total_subsidy
    active_buses = int(df['waybill_id'].nunique())

    return jsonify({
        "total_passengers": total_pax,
        "total_tickets": total_tkts,
        "cash_collected": round(total_collected, 2),
        "shakti_subsidy_claim": round(total_subsidy, 2),
        "total_gross_fare": round(total_gross, 2),
        "active_fleet_buses": active_buses,
        "shakti_share_pct": round((total_subsidy / total_gross * 100), 1) if total_gross > 0 else 0,
        "peak_hour": "12:00 PM",
        "busiest_corridor": "Budhavihar ↔ CBS"
    })

@app.route("/api/v1/analytics/hourly", methods=["GET"])
def hourly_analytics():
    """Returns hourly ridership, trips, and revenue."""
    df = get_data()
    return jsonify({
        "hourly": get_hourly_demand(df),
        "peak_stats": get_peak_demand_stats(df)
    })

@app.route("/api/v1/analytics/routes", methods=["GET"])
def routes_analytics():
    """Returns top corridors and directional balance."""
    df = get_data()
    limit = int(request.args.get("limit", 20))
    return jsonify({
        "top_routes": get_top_corridors(df, limit=limit),
        "directional_balance": get_corridor_directional_balance(df)
    })

@app.route("/api/v1/analytics/stops", methods=["GET"])
def stops_analytics():
    """Returns stop rankings and GIS GeoJSON features."""
    df = get_data()
    limit = int(request.args.get("limit", 20))
    return jsonify({
        "stops": get_stop_rankings(df, limit=limit),
        "geojson": get_gis_stops_geojson(df)
    })

@app.route("/api/v1/analytics/buses", methods=["GET"])
def buses_analytics():
    """Returns 47-bus fleet breakdown by Waybill."""
    df = get_data()
    return jsonify({
        "fleet": get_fleet_statistics(df),
        "summary": get_fleet_summary(df)
    })

@app.route("/api/v1/analytics/revenue", methods=["GET"])
def revenue_analytics():
    """Returns cash collections and Shakti state subsidy receivable."""
    df = get_data()
    return jsonify({
        "summary": get_revenue_summary(df),
        "by_route": get_revenue_by_route(df, limit=20)
    })

@app.route("/api/v1/analytics/alerts", methods=["GET"])
def alerts_analytics():
    """Returns system alerts and diagnostic notices."""
    df = get_data()
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

