"""Build public v2 materials; never freeze an incomplete baseline run.
Run: python work/user_study/build_trials.py [--freeze] [--root /ssd1/chingheng/FlashMakeUp]
"""
import argparse,hashlib,json,shutil
from pathlib import Path
from PIL import Image
HERE=Path(__file__).resolve().parent

def digest(data):return hashlib.sha256(data).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path('/ssd1/chingheng/FlashMakeUp'));p.add_argument('--side',type=int,default=640);p.add_argument('--freeze',action='store_true');a=p.parse_args()
 target=HERE/'site';target.mkdir(exist_ok=True);(target/'img').mkdir(exist_ok=True)
 existing=json.loads((target/'trials.json').read_text()) if (target/'trials.json').exists() else {}
 if existing.get('frozen'):raise SystemExit('Materials are frozen. Create a new study version instead of overwriting them.')
 gc=a.root/'work/gpt_compare';pairs=gc/'pairs_100_v2.json';data=json.loads(pairs.read_text());groups=data['groups']
 methods={'ours':a.root/'work/stage2_paper/out/hybrid/s2v2_full3000_c2o3_300_p065','magicmakeup':gc/'mm_chain','art':gc/'art','fluxmakeup':gc/'fluxmakeup','stablemakeup':gc/'stablemakeup'}
 for g in groups:
  assert g['source_split'] in ('syn/test','creative/test','creative/unseen_style'),g['gid']
  assert len(g['refs'])==3 and all(r['split'] in ('creative/test','creative/unseen_style') for r in g['refs']),g['gid']
 complete=[g for g in groups if all((d/(g['gid']+'.png')).is_file() for d in methods.values())]
 counts={m:sum((d/(g['gid']+'.png')).is_file() for g in groups) for m,d in methods.items()}
 if a.freeze and (len(complete)!=len(groups) or len(complete)<44):raise SystemExit(f'Cannot freeze: {len(complete)}/{len(groups)} complete looks; counts={counts}')
 if len(complete)<8:raise SystemExit('Pilot needs 8 complete looks (one per baseline plus four checks).')
 provenance=[];used=set()
 def save(src,side):
  raw=src.read_bytes();name=digest(raw+str(side).encode())[:24]+'.jpg';im=Image.open(src).convert('RGB');im.thumbnail((side,side),Image.Resampling.LANCZOS);im.save(target/'img'/name,quality=95,subsampling=0)
  used.add(name);provenance.append({'source':str(src),'source_sha256':digest(raw),'asset':'img/'+name,'asset_sha256':digest((target/'img'/name).read_bytes())});return 'img/'+name
 looks=[]
 for g in complete:
  gid=g['gid'];refs=[]
  for r in g['refs']:refs.append({'img':save(gc/'refs'/(r['ref']+'.png'),a.side//2),'part':{'face':'face paint'}.get(r['part'],r['part'])})
  looks.append({'gid':gid,'src':save(gc/'src'/(gid+'.png'),a.side),'refs':refs,'outputs':{m:save(d/(gid+'.png'),a.side) for m,d in methods.items()}})
 manifest={'version':'irismix-public-v2-1','mode':'formal' if a.freeze else 'pilot','frozen':a.freeze,'created_from':pairs.name,'pairs_md5':hashlib.md5(pairs.read_bytes()).hexdigest(),'pairs_sha256':digest(pairs.read_bytes()),'source_policy':'public LayerBeauty v2 only; no CPM-Real or MF2K','ours':'ours','baselines':[m for m in methods if m!='ours'],'per_baseline':10 if a.freeze else 1,'attention_checks':4,'expected_trials':44 if a.freeze else 8,'availability':{'total_looks':len(groups),'complete_looks':len(complete),'method_counts':counts},'looks':looks}
 manifest['materials_sha256']=digest(json.dumps(manifest,sort_keys=True,separators=(',',':')).encode());(target/'trials.json').write_text(json.dumps(manifest,indent=2)+'\n');(HERE/'provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
 for f in (target/'img').glob('*'):
  if f.name not in used:f.unlink()
 if not (target/'config.json').exists():(target/'config.json').write_text(json.dumps({'submit_url':'/api/responses','recruitment_open':False},indent=2)+'\n')
 if a.freeze:
  with (HERE/'STUDY.md').open('a') as f:f.write('\n## Frozen materials\n- trials.json MD5: `'+hashlib.md5((target/'trials.json').read_bytes()).hexdigest()+'`\n- Materials SHA-256: `'+manifest['materials_sha256']+'`\n')
 print(json.dumps({'mode':manifest['mode'],'counts':counts,'complete':len(complete),'expected_trials':manifest['expected_trials'],'materials_sha256':manifest['materials_sha256']},indent=2))
if __name__=='__main__':main()
