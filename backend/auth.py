"""Admin authentication for dataset-management operations."""
import hmac
import os
import secrets
import time
from collections import defaultdict
from functools import lru_cache
from threading import Lock

from flask import jsonify, request, session
from werkzeug.security import check_password_hash, generate_password_hash

_attempts = defaultdict(list)
_attempts_lock = Lock()
_LOCK_WINDOW = 600
_MAX_ATTEMPTS = 5


def _production():
    return os.getenv('FLASK_ENV', '').lower() == 'production' or os.getenv('RENDER') == 'true'


def admin_configured():
    return bool(os.getenv('ADMIN_EMAIL') and os.getenv('ADMIN_PASSWORD')) or not _production()


def _credentials():
    # Demo defaults are intentionally restricted to local development.
    if _production():
        return os.getenv('ADMIN_EMAIL', '').strip().lower(), os.getenv('ADMIN_PASSWORD', '')
    return os.getenv('ADMIN_EMAIL', 'admin@gmail.com').strip().lower(), os.getenv('ADMIN_PASSWORD', 'Admin123')


@lru_cache(maxsize=8)
def _password_hash(password):
    return generate_password_hash(password)


def csrf_token():
    token = session.get('csrf_token')
    if not token:
        token = secrets.token_urlsafe(32)
        session['csrf_token'] = token
    return token


def auth_status():
    email, _ = _credentials()
    return jsonify({'authenticated': bool(session.get('admin_authenticated')), 'email': session.get('admin_email'), 'csrf_token': csrf_token(), 'configured': admin_configured(), 'demo_credentials': not _production() and not os.getenv('ADMIN_PASSWORD')})


def login():
    data = request.get_json(silent=True) or {}
    supplied_csrf = request.headers.get('X-CSRF-Token', '')
    if not supplied_csrf or not hmac.compare_digest(supplied_csrf, session.get('csrf_token', '')):
        return jsonify({'error': 'Session check failed. Reload the page and try again.'}), 403
    if not admin_configured():
        return jsonify({'error': 'Admin credentials are not configured for this deployment.'}), 503

    ip = request.remote_addr or 'unknown'
    now = time.monotonic()
    with _attempts_lock:
        _attempts[ip] = [t for t in _attempts[ip] if now - t < _LOCK_WINDOW]
        if len(_attempts[ip]) >= _MAX_ATTEMPTS:
            return jsonify({'error': 'Too many attempts. Try again in 10 minutes.'}), 429

    expected_email, expected_password = _credentials()
    supplied_email = str(data.get('email', '')).strip().lower()
    supplied_password = str(data.get('password', ''))
    email_ok = hmac.compare_digest(supplied_email, expected_email)
    password_ok = check_password_hash(_password_hash(expected_password), supplied_password) if expected_password else False
    if not (email_ok and password_ok):
        with _attempts_lock:
            _attempts[ip].append(now)
        return jsonify({'error': 'Email or password is incorrect.'}), 401

    session.clear()
    session.permanent = True
    session['admin_authenticated'] = True
    session['admin_email'] = expected_email
    csrf_token()
    return jsonify({'authenticated': True, 'email': expected_email, 'csrf_token': session['csrf_token']})


def logout():
    supplied_csrf = request.headers.get('X-CSRF-Token', '')
    if not supplied_csrf or not hmac.compare_digest(supplied_csrf, session.get('csrf_token', '')):
        return jsonify({'error': 'Session check failed. Reload the page and try again.'}), 403
    session.clear()
    return jsonify({'authenticated': False})
