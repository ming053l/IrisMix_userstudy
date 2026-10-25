"""Validated analysis of completed responses. No QA records enter human results.
python work/user_study/analyze.py exported.json --mode pilot --out analysis_pilot.json
Default mode=formal. Include only the active frozen materials for formal analysis.
"""
import argparse,json,math,random,statistics
from collections import defaultdict,Counter
from pathlib import Path
HERE=Path(__file__).resolve().parent;QS=('makeup','identity','realism')
def wilson(w,n,z=1.96):
 if not n:return None
 p=w/n;d=1+z*z/n;c=p+z*z/(2*n);h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n));return [(c-h)/d,(c+h)/d]
def binom_p(w,n):
 if not n:return None
 k=min(w,n-w);return min(1.,2*sum(math.exp(math.lgamma(n+1)-math.lgamma(i+1)-math.lgamma(n-i+1)-n*math.log(2)) for i in range(k+1)))
def fleiss(items):
 counts=[(sum(v),len(v)) for v in items.values() if len(v)>=2]
 if not counts:return {'value':None,'reason':'No item has multiple raters'}
 if len({n for _,n in counts})!=1:return {'value':None,'reason':'Conventional Fleiss kappa requires equal rater counts per item; not computed for this unbalanced sample'}
 n=counts[0][1];p=sum(w for w,_ in counts)/(len(counts)*n);pe=p*p+(1-p)**2
 if pe==1:return {'value':None,'reason':'No marginal variation'}
 po=sum((w*(w-1)+(n-w)*(n-w-1))/(n*(n-1)) for w,_ in counts)/len(counts)
 return {'value':(po-pe)/(1-pe),'items':len(counts),'raters_per_item':n}
def analyze(files,mode='formal',boots=2000,seed=20261025):
 d=json.loads((HERE/'site/trials.json').read_text());all_res=[]
 for file in files:
  value=json.loads(Path(file).read_text());all_res.extend(value['responses'] if isinstance(value,dict) and 'responses' in value else value if isinstance(value,list) else [value])
 kept=[];excluded=[];seen=set();ignored=Counter()
 for r in all_res:
  if r.get('is_test'):ignored['qa']+=1;continue
  if r.get('mode')!=mode:ignored['other_mode']+=1;continue
  if r.get('rater') in seen:ignored['duplicate_rater']+=1;continue
  seen.add(r.get('rater'))
  try:
   assert r['materials_sha256']==d['materials_sha256'],'Materials mismatch'
   assert mode!='formal' or d['frozen'],'Formal materials are not frozen'
   assert r.get('consented') and r.get('finished'),'Incomplete response'
   tr=r['trials'];assert len(tr)==d['expected_trials'] and len({t['gid'] for t in tr})==len(tr),'Incomplete or repeated trials'
   for t in tr:
    assert t['gid'] in {l['gid'] for l in d['looks']} and isinstance(t['ours_left'],bool),'Unknown look or side'
    assert set(t['a'])==set(QS) and all(t['a'][q] in ('A','B') for q in QS),'Invalid answers'
    assert isinstance(t['ms'],(int,float)) and math.isfinite(t['ms']) and t['ms']>=0,'Invalid timing'
   assert sum(bool(t['check']) for t in tr)==d['attention_checks'],'Missing checks'
   for b in d['baselines']:assert sum(not t['check'] and t['base']==b for t in tr)==d['per_baseline'],'Unbalanced comparisons'
  except (AssertionError,KeyError,TypeError) as e:excluded.append({'rater':r.get('rater'),'reason':str(e)});continue
  fails=sum(t['check'] and t['a']['makeup']!=('A' if t['ours_left'] else 'B') for t in tr);median_ms=statistics.median(t['ms'] for t in tr)
  if fails>=2 or median_ms<3000:excluded.append({'rater':r['rater'],'reason':'Declared exclusion','attention_failures':fails,'median_ms':median_ms});continue
  kept.append(r)
 votes=defaultdict(lambda:defaultdict(list));items=defaultdict(lambda:defaultdict(list))
 for r in kept:
  for t in r['trials']:
   if t['check']:continue
   for q in QS:
    w=int(t['a'][q]==('A' if t['ours_left'] else 'B'));votes[(t['base'],q)][r['rater']].append(w);items[(t['base'],q)][t['gid']].append(w)
 rng=random.Random(seed);rows=[]
 for (base,q),raters in sorted(votes.items()):
  w=sum(map(sum,raters.values()));n=sum(map(len,raters.values()));rs=list(raters.values());samples=[]
  for _ in range(boots):
   chosen=[rng.choice(rs) for _ in rs];samples.append(sum(map(sum,chosen))/sum(map(len,chosen)))
  samples.sort();rows.append({'baseline':base,'question':q,'wins':w,'n':n,'win_rate':w/n,'wilson95':wilson(w,n),'binomial_two_sided_unadjusted':binom_p(w,n),'participant_bootstrap95':[samples[int(.025*boots)],samples[min(boots-1,int(.975*boots))]],'fleiss_kappa':fleiss(items[(base,q)])})
 return {'mode':mode,'materials_sha256':d['materials_sha256'],'participants_kept':len(kept),'excluded':excluded,'ignored':dict(ignored),'bootstrap_seed':seed,'bootstrap_replicates':boots,'note':'Wilson/binomial are unadjusted trial-level summaries; judgments repeat within raters/scenes. Participant bootstrap accounts for rater clustering but not scene clustering. Pilot results are separate from formal results.','results':rows}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('files',nargs='+');p.add_argument('--mode',choices=['formal','pilot'],default='formal');p.add_argument('--out',type=Path);a=p.parse_args();result=analyze(a.files,a.mode);text=json.dumps(result,indent=2);print(text)
 if a.out:a.out.write_text(text+'\n')
