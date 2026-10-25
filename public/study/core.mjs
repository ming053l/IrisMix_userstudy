export const QS=['makeup','identity','realism'];
export function shuffle(items,random=Math.random){const a=[...items];for(let i=a.length-1;i>0;i--){const j=Math.floor(random()*(i+1));[a[i],a[j]]=[a[j],a[i]];}return a;}
export function makePlan(d,random=Math.random){
 const needed=d.baselines.length*d.per_baseline+d.attention_checks;
 if(d.looks.length<needed)throw Error(`Insufficient complete looks: ${d.looks.length}/${needed}`);
 const looks=shuffle(d.looks,random);let i=0;const plan=[];
 for(const base of d.baselines)for(let n=0;n<d.per_baseline;n++)plan.push({gid:looks[i++].gid,base,check:false,ours_left:random()<.5});
 for(let n=0;n<d.attention_checks;n++)plan.push({gid:looks[i++].gid,base:'source',check:true,ours_left:random()<.5});
 return shuffle(plan,random);
}
export function validateResponse(r,d){
 if(!r||typeof r.rater!=='string'||!/^[a-zA-Z0-9-]{8,64}$/.test(r.rater))throw Error('Invalid response ID');
 if(r.materials_sha256!==d.materials_sha256||r.mode!==d.mode)throw Error('Materials version mismatch');
 if(typeof r.consented!=='string'||!Number.isFinite(Date.parse(r.consented))||!Number.isFinite(Date.parse(r.started))||!Number.isFinite(Date.parse(r.finished))||!Array.isArray(r.trials)||r.trials.length!==d.expected_trials)throw Error('Incomplete response');
 if(r.is_test!==undefined&&typeof r.is_test!=='boolean')throw Error('Invalid test flag');
 if(!['zh','en'].includes(r.lang)||!(r.exp===null||Number.isInteger(r.exp)&&r.exp>=0&&r.exp<=3))throw Error('Invalid participant metadata');
 const ids=new Set(),counts=Object.fromEntries(d.baselines.map(b=>[b,0]));let checks=0;
 for(const t of r.trials){if(!d.looks.some(l=>l.gid===t.gid)||ids.has(t.gid))throw Error('Unknown or repeated look');ids.add(t.gid);if(typeof t.ours_left!=='boolean'||typeof t.check!=='boolean'||!Number.isFinite(t.ms)||t.ms<0||t.ms>86400000)throw Error('Invalid trial metadata');
 if(!t.a||Object.keys(t.a).length!==3||!QS.every(q=>t.a[q]==='A'||t.a[q]==='B'))throw Error('Each trial requires three answers');
 if(t.check){if(t.base!=='source')throw Error('Invalid attention check');checks++;}else{if(!(t.base in counts))throw Error('Unknown baseline');counts[t.base]++;}}
 if(checks!==d.attention_checks||Object.values(counts).some(n=>n!==d.per_baseline))throw Error('Unbalanced or incomplete plan');return true;
}
