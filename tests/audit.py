import json,re,random
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args=['--no-sandbox'])
    pg=b.new_context().new_page();pg.goto('http://localhost:8765/old.html');pg.wait_for_timeout(700)
    D=pg.evaluate('S.drills.filter(d=>d.src==="seed").map(d=>({...d,np_:d.dg?GEN[d.dg[0]](...d.dg.slice(1)).p.filter(i=>"abg".includes(i.k)).length:0,ncone:d.dg?GEN[d.dg[0]](...d.dg.slice(1)).p.filter(i=>i.k==="cone").length:0}))')
    fl=[]
    for d in D:
        m=[int(x) for x in re.findall(r'\d+',d['np'])];mx=max(m) if m else 99;mn=min(m) if m else 1
        if d['np_']>mx:fl.append((d['sid'] if 'sid' in d else '-',d['name'],'diagram shows %d players > max %d'%(d['np_'],mx)))
        if not d.get('safe') and d['cat'] not in('الإحماء','التهدئة'):fl.append((d.get('sid','-'),d['name'],'no safety note'))
        if d['min']>20:fl.append((d.get('sid','-'),d['name'],'duration %d'%d['min']))
        if len(d['steps'])<3:fl.append((d.get('sid','-'),d['name'],'few steps'))
        if d['level']=='متقدم' and mn<4:fl.append((d.get('sid','-'),d['name'],'advanced w/ min players %d'%mn))
    print(len(D),'drills audited; flags',len(fl))
    from collections import Counter
    print(Counter(f[2].split(' ')[0]+' '+f[2].split(' ')[1] for f in fl))
    for f in fl[:14]:print(f)
    random.seed(3);ids=['w1','c1','p3','n9','k2','u1','e3','gk2','sp2','q2']
    for d in D:
        if d.get('sid') in ids or d['name'] in('روندو 4 ضد 1','تمطيط وتهدئة'):print('--',d['name'],'|',d['cat'],d['level'],d['min'],'د',d['np'],d['space'] if 'space' in d else '','|',d['goal'],'|',' / '.join(d['steps'][:4]),'| سلامة:',d.get('safe','—'))
    b.close()
