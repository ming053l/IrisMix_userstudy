import unittest,tempfile,json,importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('study_analysis',Path(__file__).with_name('analyze.py'));a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
class AnalysisTests(unittest.TestCase):
 def test_known_probabilities(self):
  self.assertAlmostEqual(a.binom_p(5,10),1);self.assertAlmostEqual(a.binom_p(10,10),2/1024);self.assertAlmostEqual(a.wilson(5,10)[0],.2365896,places=5);self.assertLess(a.binom_p(1000,1000),1e-200)
 def test_exclusions_and_qa_isolation(self):
  d=json.loads((Path(__file__).parent/'site/trials.json').read_text());ids=[l['gid'] for l in d['looks']];tr=[]
  for b in d['baselines']:tr.append({'gid':ids[len(tr)],'base':b,'check':False,'ours_left':True,'ms':5000,'a':{'makeup':'A','identity':'A','realism':'A'}})
  for n in range(4):tr.append({'gid':ids[len(tr)],'base':'source','check':True,'ours_left':True,'ms':5000,'a':{'makeup':'A','identity':'A','realism':'A'}})
  base={'rater':'valid-rater','mode':'pilot','materials_sha256':d['materials_sha256'],'consented':'yes','finished':'yes','trials':tr}
  fail=json.loads(json.dumps(base));fail['rater']='attention-fail';fail['trials'][-1]['a']['makeup']='B';fail['trials'][-2]['a']['makeup']='B'
  fast=json.loads(json.dumps(base));fast['rater']='too-fast'
  for t in fast['trials']:t['ms']=2999
  qa={**base,'rater':'qa-only','is_test':True}
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/'responses.json';path.write_text(json.dumps({'responses':[base,base,fail,fast,qa]}));r=a.analyze([path],'pilot',100);self.assertEqual(r['participants_kept'],1);self.assertEqual(len(r['excluded']),2);self.assertEqual(r['ignored'],{'duplicate_rater':1,'qa':1});self.assertTrue(all(x['win_rate']==1 for x in r['results']));self.assertEqual(len(r['results']),12)
if __name__=='__main__':unittest.main()
