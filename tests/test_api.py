"""
KSRTC Kalaburagi Division - Test Suite for BusPulse API
Verifies that all analytical endpoints return valid HTTP 200 responses with correct schema.
Uses Python built-in unittest (zero extra dependencies).
"""
import unittest
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(BACKEND_DIR))

from backend.app import app

class TestBusPulseAPI(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_health_endpoint(self):
        res = self.client.get('/api/v1/health')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['records_loaded'], 19275)

    def test_kpi_summary(self):
        res = self.client.get('/api/v1/kpi/summary')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertGreater(data['total_passengers'], 0)
        self.assertEqual(data['active_fleet_buses'], 47)
        self.assertGreater(data['shakti_subsidy_claim'], 0)

        # Test interactive filters
        res_morning = self.client.get('/api/v1/kpi/summary?window=morning')
        self.assertEqual(res_morning.status_code, 200)
        self.assertLess(res_morning.get_json()['total_passengers'], data['total_passengers'])

        res_shakti = self.client.get('/api/v1/kpi/summary?shakti=true')
        self.assertEqual(res_shakti.status_code, 200)
        self.assertGreater(res_shakti.get_json()['shakti_subsidy_claim'], 0)

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

    def test_ai_forecast(self):
        res = self.client.get('/api/v1/ai/forecast')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('predicted', data)
        self.assertGreater(len(data['predicted']), 0)

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
