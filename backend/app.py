"""
KSRTC Kalaburagi Division - BusPulse Backend API
Flask REST API connecting HTML/JS dashboards with Pandas Analytical Pipeline.
"""
import os
import sys
from datetime import timedelta
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

# Add backend directory to Python path
BACKEND_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BACKEND_DIR))

from data_loader import get_data, update_dataset
from analytics.demand import get_hourly_demand, get_peak_demand_stats
from analytics.stops import get_stop_rankings, get_gis_stops_geojson
from analytics.movement import get_top_corridors, get_corridor_directional_balance
from analytics.fleet import get_fleet_statistics, get_fleet_summary
from analytics.revenue import get_revenue_summary, get_revenue_by_route
from analytics.predictions import get_demand_forecast, simulate_what_if
from services.filters import apply_filters
from services.alerts import get_system_alerts

# Frontend path for optional direct serving
FRONTEND_DIR = BACKEND_DIR.parent / "frontend"

app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="")
is_production = os.getenv('FLASK_ENV', '').lower() == 'production' or os.getenv('RENDER') == 'true'
secret_key = os.environ.get('SECRET_KEY')
if is_production and not secret_key:
    raise RuntimeError('SECRET_KEY must be configured in production.')
app.secret_key = secret_key or 'local-development-only-change-before-deploy'
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=is_production,
    PERMANENT_SESSION_LIFETIME=timedelta(hours=8),
)
CORS(app)  # Enable Cross-Origin Resource Sharing for file:// and localhost

try:
    from .auth import auth_status, login, logout
except ImportError:
    from auth import auth_status, login, logout

@app.route('/api/v1/auth/status', methods=['GET'])
def admin_auth_status():
    return auth_status()

@app.route('/api/v1/auth/login', methods=['POST'])
def admin_login():
    return login()

@app.route('/api/v1/auth/logout', methods=['POST'])
def admin_logout():
    return logout()

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
    return send_from_directory(FRONTEND_DIR, path)

# Helper to slice data via query parameters
def get_filtered_df():
    """Extracts query parameters and returns filtered DataFrame."""
    df = get_data()
    start_hour = request.args.get("start_hour", type=int)
    end_hour = request.args.get("end_hour", type=int)
    bus_id = request.args.get("bus_id") or request.args.get("waybill")
    route_name = request.args.get("route")
    stop_name = request.args.get("stop")
<<<<<<< Updated upstream
    shakti_param = request.args.get("shakti_only")
=======

    shakti_param = request.args.get("shakti", "").lower().strip()
    from_date = request.args.get("from_date")
    to_date = request.args.get("to_date")
    data_status = request.args.get("data_status")
>>>>>>> Stashed changes
    shakti_only = None
    if shakti_param is not None:
        shakti_only = shakti_param.lower() in ("1", "true", "yes")

    return apply_filters(
        df,
        start_hour=start_hour,
        end_hour=end_hour,
        bus_id=bus_id,
        route_name=route_name,
        stop_name=stop_name,
        shakti_only=shakti_only,
        from_date=from_date,
        to_date=to_date,
        data_status=data_status,
    )

# ══════════════════════════════════════════════════════════════════════════
# REST API ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════

@app.route("/api/v1/health", methods=["GET"])
def health():
    df = get_data()
    date_str = "2026-10-20"
    if 'date' in df.columns and not df.empty:
        try:
            date_str = str(df['date'].iloc[0])[:10]
        except Exception:
            pass
    return jsonify({
        "status": "healthy",
        "service": "KSRTC Kalaburagi BusPulse Analytics Engine",
        "division": "Kalaburagi / KKRTC",
<<<<<<< Updated upstream
        "records_loaded": len(df),
        "dataset_date": date_str
=======
        "records_loaded": len(get_data()),
        "date_range": sorted(get_data()['date'].dropna().unique().tolist()),
        "data_status": get_data().get('data_status', pd.Series(['Source sample'] * len(get_data()))).value_counts().to_dict()
>>>>>>> Stashed changes
    })

@app.route("/api/v1/data/upload", methods=["POST"])
def upload_data():
    """
    Upload a new bus ticket dataset (.xlsx, .csv, .json).
    Allows department officials to update the dashboard with new data.
    """
    if "file" not in request.files:
        return jsonify({"error": "No file part in request"}), 400
    file = request.files["file"]
    if not file or file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    filename = file.filename.lower()
    try:
        import pandas as pd
        if filename.endswith(".xlsx") or filename.endswith(".xls"):
            raw_df = pd.read_excel(file)
        elif filename.endswith(".csv"):
            raw_df = pd.read_csv(file)
        elif filename.endswith(".json"):
            import json
            data = json.load(file)
            raw_df = pd.DataFrame(data)
        else:
            return jsonify({"error": "Unsupported file format. Please upload .xlsx, .csv, or .json"}), 400

        updated_df = update_dataset(raw_df)
        total_pax = int(updated_df['passengers'].sum()) if 'passengers' in updated_df.columns else len(updated_df)
        
        return jsonify({
            "message": "Dataset uploaded and analyzed successfully!",
            "records_loaded": len(updated_df),
            "total_passengers": total_pax,
            "buses_count": int(updated_df['waybill_id'].nunique()) if 'waybill_id' in updated_df.columns else 0
        })
    except Exception as e:
        return jsonify({"error": f"Failed to parse dataset: {str(e)}"}), 500

@app.route("/api/v1/kpi/summary", methods=["GET"])
def kpi_summary():
<<<<<<< Updated upstream
    """Returns top-level KPIs for Overview dashboard."""
    df = get_filtered_df()
    total_pax = int(df['passengers'].sum()) if not df.empty else 0
    total_tkts = len(df)
    total_collected = float(df['collected_fare'].sum()) if not df.empty else 0.0
    total_subsidy = float(df['subsidy_fare'].sum()) if not df.empty else 0.0
=======
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
    total_tkts = int(df[['date', 'waybill_id', 'ticket_number']].drop_duplicates().shape[0])
    total_collected = float(df['collected_fare'].sum())
    total_subsidy = float(df['subsidy_fare'].sum())
>>>>>>> Stashed changes
    total_gross = total_collected + total_subsidy
    active_buses = int(df['waybill_id'].nunique()) if not df.empty else 0

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
    df = get_filtered_df()
    return jsonify({
        "hourly": get_hourly_demand(df),
        "peak_stats": get_peak_demand_stats(df)
    })

@app.route("/api/v1/analytics/routes", methods=["GET"])
def routes_analytics():
    """Returns top corridors and directional balance."""
    df = get_filtered_df()
    limit = int(request.args.get("limit", 20))
    return jsonify({
        "top_routes": get_top_corridors(df, limit=limit),
        "directional_balance": get_corridor_directional_balance(df),
        "stops": get_stop_rankings(df, limit=20),
        "revenue_by_route": get_revenue_by_route(df, limit=20)
    })

@app.route("/api/v1/analytics/stops", methods=["GET"])
def stops_analytics():
    """Returns stop rankings and GIS GeoJSON features."""
    df = get_filtered_df()
    limit = int(request.args.get("limit", 20))
    return jsonify({
        "stops": get_stop_rankings(df, limit=limit),
        "geojson": get_gis_stops_geojson(df)
    })

@app.route("/api/v1/analytics/buses", methods=["GET"])
def buses_analytics():
    """Returns 47-bus fleet breakdown by Waybill (Conductor Shifts)."""
    df = get_filtered_df()
    return jsonify({
        "fleet": get_fleet_statistics(df),
        "summary": get_fleet_summary(df)
    })

@app.route("/api/v1/analytics/revenue", methods=["GET"])
def revenue_analytics():
    """Returns cash collections and Shakti state subsidy receivable."""
    df = get_filtered_df()
    return jsonify({
        "summary": get_revenue_summary(df),
        "by_route": get_revenue_by_route(df, limit=20)
    })

@app.route("/api/v1/analytics/alerts", methods=["GET"])
def alerts_analytics():
    """Returns system alerts and diagnostic notices."""
    df = get_filtered_df()
    return jsonify({
        "alerts": get_system_alerts(df)
    })

@app.route("/api/v1/ai/forecast", methods=["GET"])
def ai_forecast():
    """Returns AI predictive demand forecast with confidence intervals."""
    df = _get_filtered_df()
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
    port = int(os.environ.get("PORT", 5000))
    print(f"\n=======================================================")
    print(f"🚌 KSRTC BusPulse Analytics Server running at:")
    print(f"👉 http://127.0.0.1:{port}")
    print(f"=======================================================\n")
    app.run(host="127.0.0.1", port=port, debug=False)

