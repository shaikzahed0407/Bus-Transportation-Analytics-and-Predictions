"""
KSRTC Kalaburagi Division - Test Suite for BusPulse API
Verifies that all analytical endpoints return valid HTTP 200 responses with correct schema.
Uses Python built-in unittest (zero extra dependencies).
"""
import unittest
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app import app

class TestBusPulseAPI(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_health_endpoint(self):
        res = self.client.get('/api/v1/health')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['status'], 'healthy')
        self.assertGreater(data['records_loaded'], 19275)
        self.assertEqual(len(data['date_range']), 31)

    def test_kpi_summary(self):
        res = self.client.get('/api/v1/kpi/summary')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertGreater(data['total_passengers'], 0)
        self.assertEqual(data['active_fleet_buses'], 47)
        self.assertGreater(data['shakti_subsidy_claim'], 0)

    def test_hourly_analytics(self):
        res = self.client.get('/api/v1/analytics/hourly')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('hourly', data)
        self.assertGreater(len(data['hourly']), 0)

    def test_routes_analytics(self):
        res = self.client.get('/api/v1/analytics/routes')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('top_routes', data)
        self.assertGreater(len(data['top_routes']), 0)

    def test_fleet_analytics(self):
        res = self.client.get('/api/v1/analytics/buses')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('fleet', data)
        self.assertEqual(len(data['fleet']), 47)
        self.assertIn('conductor_shift', data['fleet'][0])

    def test_query_filters(self):
        # Slicing by start_hour should return a subset of passengers
        res_all = self.client.get('/api/v1/kpi/summary')
        all_pax = res_all.get_json()['total_passengers']

        res_filtered = self.client.get('/api/v1/kpi/summary?start_hour=14')
        filtered_pax = res_filtered.get_json()['total_passengers']

        self.assertGreater(all_pax, filtered_pax)
        self.assertGreater(filtered_pax, 0)

    def test_ai_forecast(self):
        res = self.client.get('/api/v1/ai/forecast')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('predicted', data)
        self.assertGreater(len(data['predicted']), 0)
        self.assertEqual(data['data_days'], 31)
        self.assertEqual(data['validation_days'], 7)
        self.assertIn('validation_mae', data)

    def test_date_filter(self):
        first = self.client.get('/api/v1/kpi/summary?from_date=2026-09-20&to_date=2026-09-20').get_json()
        later = self.client.get('/api/v1/kpi/summary?from_date=2026-09-21&to_date=2026-09-26').get_json()
        self.assertGreater(first['total_passengers'], 0)
        self.assertGreater(later['total_passengers'], first['total_passengers'])

    def test_settings_requires_admin_and_csrf(self):
        self.assertEqual(self.client.get('/api/v1/data/status').status_code, 401)
        auth = self.client.get('/api/v1/auth/status').get_json()
        csrf = auth['csrf_token']
        denied = self.client.post('/api/v1/auth/login', json={
            'email': 'admin@gmail.com', 'password': 'Admin123'
        })
        self.assertEqual(denied.status_code, 403)
        login = self.client.post('/api/v1/auth/login', json={
            'email': 'admin@gmail.com', 'password': 'Admin123'
        }, headers={'X-CSRF-Token': csrf})
        self.assertEqual(login.status_code, 200)
        self.assertEqual(self.client.get('/api/v1/data/status').status_code, 200)
        csrf = login.get_json()['csrf_token']
        self.assertEqual(self.client.post('/api/v1/auth/logout', headers={'X-CSRF-Token': csrf}).status_code, 200)
        self.assertEqual(self.client.get('/api/v1/data/status').status_code, 401)

    def test_ai_simulation(self):
        res = self.client.post('/api/v1/ai/simulate', json={
            "growth_pct": 10.0,
            "shakti_pct": 80.0,
            "tariff_pct": 5.0
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('projected_passengers', data)
        self.assertGreaterEqual(data['buses_required'], 47)

if __name__ == "__main__":
    unittest.main()
