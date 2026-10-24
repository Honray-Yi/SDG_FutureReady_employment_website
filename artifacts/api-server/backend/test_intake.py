import io,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'backend'))
from fastapi.testclient import TestClient
from pypdf import PdfWriter
from pypdf.generic import DictionaryObject,NameObject,DecodedStreamObject
from app import app,CATALOG_HASH,CATALOG
from intake.engine import candidates,IDS

# Fictional test text only; no personal resume data.
def pdf_bytes(content=None,encrypted=False,pages=1):
    writer=PdfWriter()
    for _ in range(pages):
        page=writer.add_blank_page(width=612,height=792)
        if content:
            font=DictionaryObject({NameObject('/Type'):NameObject('/Font'),NameObject('/Subtype'):NameObject('/Type1'),NameObject('/BaseFont'):NameObject('/Helvetica')})
            page[NameObject('/Resources')]=DictionaryObject({NameObject('/Font'):DictionaryObject({NameObject('/F1'):writer._add_object(font)})})
            stream=DecodedStreamObject();escaped=content.replace('\\','\\\\').replace('(','\\(').replace(')','\\)')
            stream.set_data(('BT /F1 12 Tf 40 700 Td ('+escaped+') Tj ET').encode('ascii'))
            page[NameObject('/Contents')]=writer._add_object(stream)
    if encrypted:writer.encrypt('secret')
    out=io.BytesIO();writer.write(out);return out.getvalue()

class IntakeTests(unittest.TestCase):
    def setUp(self):self.client=TestClient(app)
    def body(self,skills=None):return {'skill_dictionary_version':CATALOG['version'],'dictionary_hash':CATALOG_HASH,'display_name':'Test','is_synthetic':True,'skills':skills or []}
    def parse(self,raw):return self.client.post('/api/profile/parse',content=raw,headers={'content-type':'application/pdf','x-synthetic-profile':'true'})
    def test_catalog_and_synthetic_demo_contract(self):
        data=self.client.get('/api/skills').json()
        self.assertEqual(len(data['skills']),20);self.assertEqual(len(set(IDS)),20)
        self.assertTrue(all(x['is_synthetic'] for x in self.client.get('/api/demo-profiles').json()['profiles']))
    def test_unknown_and_zero_remain_distinct(self):
        body=self.body([{'skill_id':'programming','level':0,'source':'self_report','confirmed':True}])
        data=self.client.post('/api/profile',json=body).json()
        self.assertEqual(data['vectors']['levels'][:2],[0,None]);self.assertEqual(data['vectors']['binary_presence'][:2],[0,None])
        self.assertEqual(data['vectors']['known_mask'][:2],[True,False]);self.assertEqual(data['summary']['known'],1)
        self.assertEqual(len(data['vectors']['binary_thresholds']),60)
    def test_order_independent_normalization(self):
        rows=[{'skill_id':'nlp','level':2,'source':'self_report','confirmed':True},{'skill_id':'programming','level':1,'source':'self_report','confirmed':True}]
        a=self.client.post('/api/profile',json=self.body(rows)).json();b=self.client.post('/api/profile',json=self.body(rows[::-1])).json()
        self.assertEqual(a['vectors'],b['vectors']);j=IDS.index('nlp');self.assertEqual(a['vectors']['binary_thresholds'][j*3:j*3+3],[1,1,0])
    def test_invalid_levels_ids_confirmation_and_duplicates_rejected(self):
        base={'skill_id':'programming','level':2,'source':'self_report','confirmed':True}
        for change in [{'level':4},{'level':-1},{'level':1.5},{'level':'2'},{'level':True},{'skill_id':'made_up'},{'confirmed':False},{'level':None}]:
            with self.subTest(change=change):self.assertEqual(self.client.post('/api/profile',json=self.body([{**base,**change}])).status_code,422)
        self.assertEqual(self.client.post('/api/profile',json=self.body([base,base])).status_code,422)
    def test_dictionary_change_and_synthetic_provenance(self):
        b=self.body();b['dictionary_hash']='outdated';self.assertEqual(self.client.post('/api/profile',json=b).status_code,409)
        b=self.body([{'skill_id':'programming','level':1,'source':'demo','confirmed':True}]);b['is_synthetic']=False;self.assertEqual(self.client.post('/api/profile',json=b).status_code,422)
        b['is_synthetic']=True;self.assertEqual(self.client.post('/api/profile',json=b).status_code,200)
    def test_keyword_boundaries_and_no_parent_inference(self):
        rows=candidates(['HTML and XML. Python developer.'])
        self.assertEqual([r['skill_id'] for r in rows],['programming'])
    def test_rpa_does_not_imply_robotics(self):
        rows=candidates(['参与机器人流程自动化项目'])
        self.assertIn('workflow_adoption',[r['skill_id'] for r in rows])
        self.assertNotIn('robotics',[r['skill_id'] for r in rows])

    def test_negation_learning_and_evidence_offsets(self):
        text='No Python experience. Learning SQL. NLP project.'
        by={r['skill_id']:r for r in candidates([text])}
        self.assertEqual(by['programming']['evidence'][0]['mention_type'],'negated')
        self.assertEqual(by['data_engineering']['evidence'][0]['mention_type'],'learning')
        for row in by.values():
            self.assertIsNone(row['level']);self.assertFalse(row['confirmed'])
            for e in row['evidence']:self.assertEqual(text[e['start']:e['end']],e['matched_text'])
    def test_pdf_parse_confirmation_to_standard_profile(self):
        result=self.parse(pdf_bytes('Synthetic test resume. Python and data analysis project.')).json()
        self.assertEqual(result['status'],'needs_review');self.assertEqual(result['page_count'],1)
        rows=[{k:r[k] for k in ['skill_id','level','confirmed','evidence']}|{'source':'cv_keyword'} for r in result['candidates']]
        for r in rows:r.update(level=1,confirmed=True)
        normalized=self.client.post('/api/profile',json=self.body(rows));self.assertEqual(normalized.status_code,200)
        self.assertEqual(normalized.json()['summary']['known'],2)
        self.assertNotIn('pages',result)
    def test_pdf_error_cases(self):
        cases=[(b'not PDF','invalid_pdf'),(pdf_bytes(),'no_extractable_text'),(pdf_bytes('Synthetic test resume with Python',True),'encrypted_pdf'),(pdf_bytes(pages=21),'too_many_pages')]
        for raw,code in cases:
            with self.subTest(code=code):
                r=self.parse(raw);self.assertEqual(r.status_code,422);self.assertEqual(r.json()['detail']['code'],code)
        self.assertEqual(self.parse(b'x'*(8*1024*1024+1)).status_code,413)
        self.assertEqual(self.client.post('/api/profile/parse',content=b'text',headers={'x-synthetic-profile':'true'}).status_code,415)
    def test_no_match_does_not_mean_no_skills(self):
        result=self.parse(pdf_bytes('Synthetic resume with experience in horticulture.')).json()
        self.assertEqual(result['candidates'],[]);self.assertEqual(result['status'],'needs_review')
    def test_static_assets_and_no_store(self):
        for path in ['/intake','/intake-static/app.js','/intake-static/style.css','/api/health']:
            response=self.client.get(path);self.assertEqual(response.status_code,200)

if __name__=='__main__':unittest.main()
