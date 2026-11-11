import os
import json
import datetime
import math
from pathlib import Path
from flask import Blueprint, request, jsonify, send_file, abort
import pandas as pd
from ..supabase_client import supabase, exec_sql, is_supabase_configured
from ..data_cleaner import clean_ticket_data
from ..data_loader import update_dataset

bp = Blueprint('data', __name__, url_prefix='/api/v1/data')

def _save_to_supabase(cleaned_df: pd.DataFrame, mode: str):
    """Saves cleaned DataFrame into Supabase tickets table safely."""
    if not is_supabase_configured():
        return len(cleaned_df)

    try:
        cols_to_insert = [
            'waybill_number', 'waybill_id', 'ticket_number', 'from_stop', 'to_stop',
            'from_stop_clean', 'to_stop_clean', 'route', 'date', 'time', 'hour',
            'passengers', 'collected_fare', 'subsidy_fare', 'total_fare', 'is_shakti_scheme'
        ]
        avail = [c for c in cols_to_insert if c in cleaned_df.columns]
        upload_df = cleaned_df[avail].copy()
        upload_df['date'] = upload_df['date'].astype(str)
        upload_df['time'] = upload_df['time'].astype(str)
        
        # Coerce ticket_number if present
        if 'ticket_number' in upload_df.columns:
            upload_df['ticket_number'] = pd.to_numeric(upload_df['ticket_number'], errors='coerce').fillna(0).astype(int)

        upload_df = upload_df.where(pd.notnull(upload_df), None)

        records = upload_df.to_dict(orient='records')
        for r in records:
            for k, v in r.items():
                if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
                    r[k] = None

        if mode == 'replace':
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_table = f'tickets_backup_{timestamp}'
            try:
                exec_sql(f"CREATE TABLE {backup_table} AS TABLE tickets;")
            except Exception as e:
                print(f"Supabase backup notice: {e}")

            # Delete previous records
            try:
                supabase.table('tickets').delete().neq('id', 0).execute()
            except Exception as e:
                print(f"Supabase delete notice: {e}")

        # Batch insert
        for i in range(0, len(records), 1000):
            batch = records[i:i + 1000]
            supabase.table('tickets').insert(batch).execute()

        return len(records)
    except Exception as e:
        print(f"⚠️ Supabase sync skipped/notice: {e}")
        return len(cleaned_df)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
BACKUP_DIR = BASE_DIR / "data" / "backups"
HISTORY_FILE = BACKUP_DIR / "data_history.json"

@bp.route('/status', methods=['GET'])
def dataset_status():
    """Returns current active dataset metrics for the settings page."""
    try:
        from ..data_loader import get_data
        df = get_data()
        if df is None or df.empty:
            return jsonify({'loaded': False, 'records': 0})
        
        routes_count = int(df['route'].nunique()) if 'route' in df.columns else 0
        buses_count = int(df['waybill_id'].nunique()) if 'waybill_id' in df.columns else 0
        total_pax = int(df['passengers'].sum()) if 'passengers' in df.columns else len(df)
        
        dates = []
        if 'date' in df.columns:
            dates = [str(d) for d in df['date'].dropna().unique() if str(d).strip()]
        
        return jsonify({
            'loaded': True,
            'records': len(df),
            'buses': buses_count,
            'routes': routes_count,
            'passengers': total_pax,
            'dates': dates[:5]
        })
    except Exception as e:
        return jsonify({'loaded': False, 'error': str(e)}), 500

@bp.route('/upload', methods=['POST'])
def upload():
    mode = request.args.get('mode', 'merge').lower()  # merge or replace
    if mode not in ['merge', 'replace']:
        mode = 'merge'

    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    filename = file.filename.lower()

    try:
        if filename.endswith('.xlsx') or filename.endswith('.xls'):
            raw_df = pd.read_excel(file)
        elif filename.endswith('.csv'):
            try:
                raw_df = pd.read_csv(file)
            except UnicodeDecodeError:
                file.seek(0)
                raw_df = pd.read_csv(file, encoding='latin1')
        elif filename.endswith('.json'):
            raw_df = pd.DataFrame(json.load(file))
        else:
            return jsonify({"error": "Unsupported file format. Please upload .xlsx, .xls, .csv, or .json"}), 400

        # Update in-memory and disk cache with specified mode
        cleaned_df = update_dataset(raw_df, mode=mode)

        # Sync to Supabase if configured
        _save_to_supabase(cleaned_df, mode)

        total_pax = int(cleaned_df['passengers'].sum()) if 'passengers' in cleaned_df.columns else len(cleaned_df)
        buses_count = int(cleaned_df['waybill_id'].nunique()) if 'waybill_id' in cleaned_df.columns else 0

        # Record upload in history
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        history_entry = {
            'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'mode': mode.upper(),
            'filename': file.filename,
            'records_loaded': len(cleaned_df),
            'status': 'Success'
        }
        history_list = []
        if HISTORY_FILE.exists():
            try:
                with open(HISTORY_FILE, 'r', encoding='utf-8') as hf:
                    history_list = json.load(hf)
            except Exception:
                history_list = []
        history_list.insert(0, history_entry)
        with open(HISTORY_FILE, 'w', encoding='utf-8') as hf:
            json.dump(history_list[:50], hf, indent=2)

        return jsonify({
            'message': f"Dataset {mode} successful! Cleaned & cached.",
            'mode': mode,
            'records_loaded': len(cleaned_df),
            'total_passengers': total_pax,
            'buses_count': buses_count,
            'timestamp': history_entry['timestamp']
        })
    except Exception as e:
        return jsonify({"error": f"Failed processing dataset: {str(e)}"}), 500

@bp.route('/backups', methods=['GET'])
def list_backups():
    backups = []
    # 1. Local backups from data/backups/
    if BACKUP_DIR.exists():
        for f in sorted(BACKUP_DIR.glob('tickets_backup_*.csv'), key=lambda p: p.stat().st_mtime, reverse=True):
            stat = f.stat()
            backups.append({
                'name': f.name,
                'type': 'Local CSV Snapshot',
                'size_kb': round(stat.st_size / 1024, 1),
                'created_at': datetime.datetime.fromtimestamp(stat.st_mtime, datetime.timezone.utc).isoformat()
            })

    # 2. Supabase backups if configured
    if is_supabase_configured():
        try:
            result = supabase.from_('information_schema.tables').select('table_name, create_time').eq('table_schema', 'public').like('table_name', 'tickets_backup_%').execute()
            for r in (result.data or []):
                backups.append({
                    'name': r['table_name'],
                    'type': 'Supabase Cloud Table',
                    'size_kb': '-',
                    'created_at': r.get('create_time')
                })
        except Exception:
            pass

    return jsonify(backups)

@bp.route('/backups/<filename>', methods=['GET'])
def download_backup(filename):
    # Sanitize filename
    safe_name = os.path.basename(filename)
    if not safe_name.endswith('.csv'):
        abort(400, "Only CSV backups can be downloaded.")
    file_path = BACKUP_DIR / safe_name
    if not file_path.exists():
        abort(404, "Backup file not found.")
    return send_file(file_path, as_attachment=True, download_name=safe_name)

@bp.route('/history', methods=['GET'])
def history():
    if not HISTORY_FILE.exists():
        # Fallback check older location
        old_path = Path(__file__).resolve().parent / 'data_history.json'
        if old_path.exists():
            try:
                with open(old_path, 'r', encoding='utf-8') as f:
                    return jsonify(json.load(f))
            except Exception:
                return jsonify([])
        return jsonify([])
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    except Exception:
        return jsonify([])
