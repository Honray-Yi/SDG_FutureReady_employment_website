import copy
import hashlib
import json
from pathlib import Path
import unittest
from fastapi.testclient import TestClient
import app as service

class ModuleContractTests(unittest.TestCase):
    def setUp(self):
        self.client=TestClient(service.app)
        self.catalog=self.client.get('/api/skills').json()
    def body(self,rows=None):
        return {'schema_version':'1.0','skill_dictionary_version':self.catalog['version'],
                'dictionary_hash':self.catalog['dictionary_hash'],'is_synthetic':True,'display_name':'Synthetic contract test','skills':rows or []}
    def test_shared_dictionary_order_and_hash(self):
        canonical=json.loads((service.DATA_PACKAGE/'data/skill_dictionary.json').read_text(encoding='utf-8'))
        digest=hashlib.sha256(json.dumps(canonical,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
        self.assertEqual(digest,self.catalog['dictionary_hash'])
        boot=self.client.get('/api/bootstrap').json()
        self.assertEqual([s['skill_id'] for s in boot['skills']],[s['skill_id'] for s in canonical['skills']])
        self.assertEqual(boot['metadata']['dictionary_hash'],digest)
    def test_confirm_export_match_flow(self):
        rows=[{'skill_id':'programming','level':0,'source':'self_report','confirmed':True},
              {'skill_id':'data_analytics','level':2,'source':'demo','confirmed':True}]
        exported=self.client.post('/api/profile',json=self.body(rows)).json()
        result=self.client.post('/api/match',json={'profile':exported})
        self.assertEqual(result.status_code,200,result.text)
        result=result.json()
        self.assertEqual(result['profile']['skill_levels']['programming'],0)
        self.assertIsNone(result['profile']['skill_levels']['math_stats'])
        for role in result['roles']:
            self.assertLessEqual(role['score'],role['score_upper_bound'])
            for gap in role['skills_gap']:
                if gap['current_level'] is None:self.assertIsNone(gap['gap'])
            path=result['pathways'][role['role_id']]
            self.assertFalse(set(path['unknown_skill_ids']) & set(path['gaps']))
    def test_all_unknown_does_not_generate_courses(self):
        result=self.client.post('/api/match',json={'profile':self.body()}).json()
        self.assertTrue(all(r['assessment_coverage']==0 for r in result['roles']))
        self.assertTrue(all(not p['steps'] for p in result['pathways'].values()))
        self.assertTrue(all(r['score_upper_bound']>r['score'] for r in result['roles']))
    def test_rejects_stale_forged_and_non_synthetic_profiles(self):
        b=self.body();b['dictionary_hash']='old'
        self.assertEqual(self.client.post('/api/match',json={'profile':b}).status_code,409)
        b=self.body();b['is_synthetic']=False
        self.assertEqual(self.client.post('/api/match',json={'profile':b}).status_code,422)
        b=self.client.post('/api/profile',json=self.body()).json();b['vectors']['levels'][0]=3
        self.assertEqual(self.client.post('/api/match',json={'profile':b}).status_code,422)
        self.assertEqual(self.client.post('/api/match',json={'profile':self.body(),'profile_id':'DEMO-ANALYST'}).status_code,422)
        self.assertEqual(self.client.post('/api/profile/parse',content=b'%PDF-',headers={'content-type':'application/pdf'}).status_code,422)
    def test_current_module_export_json_roundtrip_is_accepted(self):
        # The uploaded package did not contain the former reference/module1
        # fixture. Exercise the actual exporter instead of inventing its contents.
        response=self.client.post('/api/profile',json=self.body([
            {'skill_id':'programming','level':1,'source':'self_report','confirmed':True}
        ]))
        self.assertEqual(response.status_code,200,response.text)
        exported=json.loads(json.dumps(response.json()))
        self.assertTrue(exported['is_synthetic'])
        result=self.client.post('/api/match',json={'profile':exported})
        self.assertEqual(result.status_code,200,result.text)
    def test_new_topics_have_no_fabricated_measurements(self):
        signals={s['skill_id']:s for s in self.client.get('/api/bootstrap').json()['signals']}
        for sid in ['math_stats','computer_vision','speech_audio','recommender','forecasting','optimization','robotics','human_ai','workflow_adoption']:
            self.assertIsNone(signals[sid]['job_snapshot_count'])
            self.assertEqual(signals[sid]['research_status'],'not_measured')

if __name__=='__main__':unittest.main()
