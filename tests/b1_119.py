import json,sys,subprocess,collections
from playwright.sync_api import sync_playwright
R=[];errs=[]
def ok(n,c,x=''):R.append(bool(c));print(('PASS ' if c else 'FAIL ')+n,x)
B='http://localhost:8765/'
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':390,'height':780});pg=ctx.new_page()
    pg.on('pageerror',lambda e:errs.append(str(e)));pg.on('requestfailed',lambda r:errs.append('FAILED '+r.url));pg.on('response',lambda r:r.status>=400 and errs.append('HTTP%d %s'%(r.status,r.url)))
    pg.on('dialog',lambda d:d.accept());ev=pg.evaluate
    # --- user data created in the OLD version
    pg.goto(B+'old119.html');pg.wait_for_timeout(500)
    old_n=ev('S.drills.length')
    ev('editDrill()');pg.fill('#f1','تمريري الخاص');pg.click('#modal .bt:not(.s)')
    sid=ev('S.drills.find(d=>d.src==="seed").id');ev('go("drills")');ev(f'arcD("{sid}")')
    ev('editP()');pg.fill('#p1','لاعب قديم');pg.click('#modal .bt:not(.s)')
    ev('newSess()');ev('ES.name="حصة قديمة";saveS()')
    ev('B=newB();B.name="لوحة قديمة";B.frames[0].p=[P("a",.5,.5,1)];saveB()') if False else None
    ev('go("board")');ev('tool="pa";boardView()');ev('B.name="لوحة قديمة";B.frames[0].p.push({id:"q",k:"a",x:.5,y:.5,n:1});saveB()')
    ev('S.forms={"تشكيلة قديمة":[{x:.5,y:.5,k:"a",n:1}]};save()')
    ev('expB()');oldbk=ev('$("#bk").value');ev('closeM()')
    snap=json.loads(ev('JSON.stringify(S)'))
    # --- open NEW version on same origin/IndexedDB
    pg.goto(B+'new.html');pg.wait_for_timeout(700)
    ok('migration adds 31, keeps all old',ev('S.drills.length')==old_n+1+31,ev('S.drills.length'))
    ok('old user data intact',ev('S.drills.find(d=>d.id==="%s").status'%sid)=='مؤرشف' and ev('S.drills.some(d=>d.name==="تمريري الخاص")') and ev('S.players.some(p=>p.name==="لاعب قديم")') and ev('S.sessions.some(s=>s.name==="حصة قديمة")') and ev('S.boards.some(b=>b.name==="لوحة قديمة")') and ev('!!S.forms["تشكيلة قديمة"]'))
    pg.reload();pg.wait_for_timeout(600);ok('no duplicate re-seed after reload',ev('S.drills.length')==old_n+32)
    ds=ev('S.drills');tot=len(ds)
    ok('ids unique',len({d['id'] for d in ds})==tot);ok('names unique',len({d['name'] for d in ds})==tot)
    ok('all have dg+steps>=3',all(d.get('dg') and len(d['steps'])>=3 for d in ds if d['src']=='seed'))
    ok('all diagrams render',ev('S.drills.filter(d=>d.src==="seed").every(d=>dgImg(d).length>1000)'))
    hs=ev('S.drills.filter(d=>d.src==="seed").map(d=>hs(dgImg(d)))');c=collections.Counter(hs)
    print('distinct diagram images:',len(c),'of',len(hs),'| max reuse',max(c.values()));ok('every seed drill has a unique diagram',len(c)==len(hs))
    cats=collections.Counter(d['cat'] for d in ds if d['src']=='seed');print('per category:',dict(cats))
    # filters (old + new together)
    ev('go("drills")')
    def cnt(**k):
        for a,v in k.items():ev(f'{a}={json.dumps(v)}')
        ev('dl()');t=ev('$("#cnt").textContent')
        for a in k:ev(f'{a}=""')
        return t,int(t.split()[1])
    act=[d for d in ds if d['status']!='مؤرشف']
    ok('filter level',cnt(fl='متقدم')[1]==sum(d['level']=='متقدم' for d in act),cnt(fl='متقدم')[0])
    ok('filter players=3',cnt(fn=3)[1]==ev('S.drills.filter(d=>d.status!=="مؤرشف"&&npr(d)[0]<=3&&3<=npr(d)[1]).length'))
    ok('filter phase تهدئة',cnt(fp='تهدئة')[1]==sum(d['cat']=='التهدئة' for d in act))
    ok('filter type لعب',cnt(ft='لعب')[1]==sum(d['cat']=='مباريات مصغرة' for d in act))
    ok('filter duration ≤10',cnt(fd='≤10')[1]==sum(d['min']<=10 for d in act))
    ok('search finds new+old',cnt(fq='ركنية')[1]>=1 and cnt(fq='روندو')[1]>=3)
    ok('archived list',cnt(fa=True)[1]==1 and True)
    ev('fa=false')
    # actions on a new drill
    nid=ev('S.drills.find(d=>d.sid==="n7").id');ev(f'viewDrill("{nid}")');ok('view shows diagram+safety',ev('document.querySelector("#modal img")!==null')and 'السلامة' in ev('$("#modal").innerText'));ev('closeM()')
    ev(f'editDrill("{nid}")');pg.fill('#f1','ركنية معدلة');pg.click('#modal .bt:not(.s)');n=ev('S.drills.length')
    ok('edit new drill = copy, original kept',ev('S.drills.some(d=>d.name==="ركنية قصيرة منظمة")') and ev('S.drills.some(d=>d.name==="ركنية معدلة")') and n==tot+1)
    ev(f'copyD("{nid}")');ev(f'arcD("{nid}")');ev(f'favD("{nid}")');ev('delD(S.drills.find(d=>d.name==="ركنية معدلة").id)')
    ok('copy/archive/fav/delete',ev('S.drills.length')==tot+1 and ev(f'S.drills.find(d=>d.id==="{nid}").status')=='مؤرشف');ev(f'arcD("{nid}")')
    # session with new drills + print + pdf
    ev('newSess()');ev('ES.name="حصة جديدة";ES.ph[0].drill=S.drills.find(d=>d.sid==="n3").id;ES.ph[0].note="ملاحظتي";ES.ph[1].drill=S.drills.find(d=>d.sid==="n14").id;saveS()')
    pg.reload();pg.wait_for_timeout(600)
    ok('session w/ new drills persists',ev('S.sessions.find(s=>s.name==="حصة جديدة").ph[0].drill')==ev('S.drills.find(d=>d.sid==="n3").id'))
    ev('printSession(S.sessions.find(s=>s.name==="حصة جديدة"))');pg.wait_for_timeout(300)
    txt=ev('$("#print").innerText');ok('print has drill, note, safety',all(k in txt for k in['مثلث مفتوح','ملاحظتي','السلامة']) and ev('document.querySelectorAll("#print img.di").length')>=2)
    pg.emulate_media(media='print');pg.pdf(path='/tmp/t/b1.pdf',format='A4',print_background=True,prefer_css_page_size=True);pg.emulate_media(media='screen')
    ev('$("#print").style.display="none"')
    # backups
    ev('expB()');nb=ev('$("#bk").value');ev('closeM()');cur=ev('JSON.stringify(S)')
    ev('S.drills=[];S.players=[];save()');ev('impB()');pg.fill('#ib',nb);ev('chkB()');ok('new backup valid',ev('!!BK'));ev('doB()')
    ok('restore new backup: all back',ev('JSON.stringify(S)')==cur)
    ev('impB()');pg.fill('#ib',oldbk);ev('chkB()');ok('OLD backup accepted',ev('!!BK'));ev('doB()')
    ok('old backup restored + migrated to new library',ev('S.drills.length')==old_n+1+31 and ev('S.players.some(p=>p.name==="لاعب قديم")'),ev('S.drills.length'))
    bad=json.loads(nb);bad['data']['drills'][0]['name']='x';ev('impB()');pg.fill('#ib',json.dumps(bad));ev('chkB()');ok('tampered rejected',not ev('!!BK'))
    ok('no JS errors / missing resources',not errs,errs[:4])
    b.close()
print('%d/%d'%(sum(R),len(R)))
