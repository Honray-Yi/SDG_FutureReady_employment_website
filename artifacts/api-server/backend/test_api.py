"""Contract/regression tests against the original ranking implementation."""
import concurrent.futures
import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
import app as service


class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(service.app)
        cls.values, _ = service.dataset.load()

    def test_bootstrap_and_headers(self):
        r = self.client.get('/api/bootstrap')
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual((len(data['profiles']), len(data['roles']), len(data['skills'])), (3, 12, 20))
        self.assertTrue(all(p['is_synthetic'] for p in data['profiles']))
        self.assertEqual(r.headers['cache-control'], 'no-store')
        self.assertEqual(data['metadata']['research_retrieved_at'], self.values['data/research_counts.json']['retrieved_at'])

    def test_all_profiles_and_scenarios_preserve_original_scores(self):
        for p in self.values['data/synthetic_profiles.json']:
            for scenario in ('moderate', 'fast'):
                with self.subTest(profile=p['profile_id'], scenario=scenario):
                    response = self.client.post('/api/match', json={'profile_id': p['profile_id'], 'scenario': scenario})
                    self.assertEqual(response.status_code, 200)
                    result = response.json()
                    expected = service.engine.rank(p, scenario)
                    self.assertEqual([(r['role_id'], r['score'], r['skills_gap']) for r in result['roles']], [(r['role_id'], r['score'], r['skills_gap']) for r in expected])
                    for r in expected:
                        path = result['pathways'][r['role_id']]
                        original = service.engine.pathway(p, r['role_id'])
                        self.assertEqual(path['estimated_course_hours'], original['estimated_course_hours'])
                        self.assertEqual([s['course_id'] for s in path['steps']], [s['course_id'] for s in original['steps']])
                        seen = set()
                        for step in path['steps']:
                            self.assertTrue(set(step['prerequisite_course_ids']) <= seen)
                            seen.add(step['course_id'])

    def test_rejects_real_profiles_and_invalid_inputs(self):
        for body in ({'profile_id': 'real-person'}, {'profile_id': 'DEMO-ANALYST', 'cv': 'a real resume'}, {'profile_id': 'DEMO-ANALYST', 'hours_per_week': 0}, {'profile_id': 'DEMO-ANALYST', 'hours_per_week': 41}, {'profile_id': 'DEMO-ANALYST', 'hours_per_week': 3.5}, {'profile_id': 'DEMO-ANALYST', 'scenario': 'made-up'}):
            with self.subTest(body=body):
                self.assertEqual(self.client.post('/api/match', json=body).status_code, 422)

    def test_hours_change_schedule_not_rank(self):
        a = self.client.post('/api/match', json={'profile_id': 'DEMO-ANALYST', 'hours_per_week': 4}).json()
        b = self.client.post('/api/match', json={'profile_id': 'DEMO-ANALYST', 'hours_per_week': 20}).json()
        self.assertEqual(a['roles'], b['roles'])
        self.assertGreater(a['pathways']['R05']['estimated_course_weeks'], b['pathways']['R05']['estimated_course_weeks'])

    def test_concurrent_profiles_do_not_leak_state(self):
        ids = [p['profile_id'] for p in self.values['data/synthetic_profiles.json']]
        def request(pid):
            return self.client.post('/api/match', json={'profile_id': pid}).json()
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
            responses = list(pool.map(request, ids))
        self.assertEqual([r['profile']['profile_id'] for r in responses], ids)

    def test_data_update_is_read_without_server_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(service.DATA_PACKAGE / 'data', root / 'data')
            with patch.object(service, 'dataset', service.Dataset(root)):
                first = self.client.post('/api/match', json={'profile_id': 'DEMO-ANALYST'}).json()
                path = root / 'data/trend_signals.json'
                value = json.loads(path.read_text(encoding='utf-8'))
                for signal in value['signals']:
                    if signal['research_status'] == 'usable':
                        signal['research_share_relative_change'] = 0
                path.write_text(json.dumps(value), encoding='utf-8')
                second = self.client.post('/api/match', json={'profile_id': 'DEMO-ANALYST'}).json()
                self.assertNotEqual(first['metadata']['snapshot_id'], second['metadata']['snapshot_id'])
                self.assertNotEqual(first['roles'], second['roles'])
                self.assertEqual(first['metadata']['research_retrieved_at'], second['metadata']['research_retrieved_at'])

    def test_missing_data_has_safe_error(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(service, 'dataset', service.Dataset(Path(directory))):
            response = self.client.get('/api/bootstrap')
            self.assertEqual(response.status_code, 503)
            self.assertNotIn(str(service.DATA_PACKAGE), response.text)

    def test_missing_research_is_neutral(self):
        values = copy.deepcopy(self.values)
        values['data/trend_signals.json']['signals'] = []
        rank = service.bind(service.engine.rank, values)
        roles = rank(values['data/synthetic_profiles.json'][0])
        self.assertTrue(all(e['research_momentum'] == .5 for r in roles for e in r['signal_evidence']))


if __name__ == '__main__':
    unittest.main()
