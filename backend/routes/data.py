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
    """Saves cleaned DataFrame into Supabase tickets table."""
    if not is_supabase_configured():
        return len(cleaned_df)

    cols_to_insert = [
        'waybill_number', 'waybill_id', 'ticket_number', 'from_stop', 'to_stop',
        'from_stop_clean', 'to_stop_clean', 'route', 'date', 'time', 'hour',
        'passengers', 'collected_fare', 'subsidy_fare', 'total_fare', 'is_shakti_scheme'
    ]
    avail = [c for c in cols_to_insert if c in cleaned_df.columns]
    upload_df = cleaned_df[avail].copy()
    upload_df['date'] = upload_df['date'].astype(str)
    upload_df['time'] = upload_df['time'].astype(str)
    upload_df = upload_df.where(pd.notnull(upload_df), None)

    records = upload_df.to_dict(orient='records')
    for r in records:
        for k, v in r.items():
            if isinstance(v, float) and math.isnan(v):
                r[k] = None

    if mode == 'replace':
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_table = f'tickets_backup_{timestamp}'
        try:
            exec_sql(f"CREATE TABLE {backup_table} AS TABLE tickets;")
        except Exception as e:
            print(f"Backup notice: {e}")

        # Delete previous records
        supabase.table('tickets').delete().neq('id', 0).execute()

    # Batch insert
    for i in range(0, len(records), 1000):
        batch = records[i:i + 1000]
        supabase.table('tickets').insert(batch).execute()

    return len(records)

@bp.route('/upload', methods=['POST'])
def upload():
    mode = request.args.get('mode', 'merge')  # merge or replace
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    filename = file.filename.lower()

    try:
        if filename.endswith('.xlsx') or filename.endswith('.xls'):
            raw_df = pd.read_excel(file)
        elif filename.endswith('.csv'):
            raw_df = pd.read_csv(file)
        elif filename.endswith('.json'):
            raw_df = pd.DataFrame(json.load(file))
        else:
            return jsonify({"error": "Unsupported file format. Please upload .xlsx, .csv, or .json"}), 400

        # Update in-memory and disk cache
        cleaned_df = update_dataset(raw_df)

        # Sync to Supabase
        rows_saved = _save_to_supabase(cleaned_df, mode)

        total_pax = int(cleaned_df['passengers'].sum()) if 'passengers' in cleaned_df.columns else len(cleaned_df)
        buses_count = int(cleaned_df['waybill_id'].nunique()) if 'waybill_id' in cleaned_df.columns else 0

        return jsonify({
            'message': 'Dataset uploaded and processed successfully!',
            'mode': mode,
            'records_loaded': len(cleaned_df),
            'total_passengers': total_pax,
            'buses_count': buses_count,
            'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat()
        })
    except Exception as e:
        return jsonify({"error": f"Failed processing dataset: {str(e)}"}), 500

@bp.route('/backups', methods=['GET'])
def list_backups():
    if not is_supabase_configured():
        return jsonify([])
    try:
        result = supabase.from_('information_schema.tables').select('table_name, create_time').eq('table_schema', 'public').like('table_name', 'tickets_backup_%').execute()
        backups = [{'name': r['table_name'], 'created_at': r.get('create_time')} for r in (result.data or [])]
        return jsonify(backups)
    except Exception as e:
        return jsonify([])

@bp.route('/history', methods=['GET'])
def history():
    log_path = Path(__file__).resolve().parent / 'data_history.json'
    if not log_path.exists():
        return jsonify([])
    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    except Exception:
        return jsonify([])

@bp.after_request
def log_operation(response):
    if request.path.endswith('/upload') and request.method == 'POST' and response.status_code == 200:
        try:
            log_path = Path(__file__).resolve().parent / 'data_history.json'
            entry = {
                'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                'mode': request.args.get('mode', 'merge'),
                'filename': request.files['file'].filename if 'file' in request.files else 'unknown'
            }
            if log_path.exists():
                with open(log_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = []
            data.append(entry)
            with open(log_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass
    return response
