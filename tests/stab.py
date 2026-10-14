import json,sys,re
from playwright.sync_api import sync_playwright
R=[];errs=[]
def ok(n,c,x=''):R.append(bool(c));print(('PASS ' if c else 'FAIL ')+n,x)
URL=sys.argv[1] if len(sys.argv)>1 else 'http://localhost:8765/noun-star-u13.html'
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args=['--no-sandbox'])
    for vw,vh in((320,568),(360,640),(390,844),(768,1024)):
        ctx=b.new_context(viewport={'width':vw,'height':vh},has_touch=True,is_mobile=vw<700);pg=ctx.new_page()
        pg.on('pageerror',lambda e:errs.append(str(e)));pg.on('requestfailed',lambda r:errs.append('FAILED '+r.url));pg.on('response',lambda r:r.status>=400 and errs.append('HTTP%d %s'%(r.status,r.url)));pg.on('dialog',lambda d:d.accept())
        pg.goto(URL);pg.wait_for_timeout(600);ev=pg.evaluate
        ev('S.players=[{id:"p1",name:"لاعب بإسم طويل جدًا للاختبار",num:"10",pos:"مهاجم",status:"نشط",notes:""}]')
        ev('S.sessions=[{id:"s1",name:"حصة اختبار الشاشات بإسم طويل جدًا",date:"2026-10-14",total:60,goal:"",att:{},eval:"",ph:[{id:"a",name:"إحماء",min:15,drill:S.drills.find(d=>d.name==="تمطيط وتهدئة").id,note:"ملاحظة"},{id:"b",name:"رئيسي",min:25,drill:S.drills.find(d=>d.sid==="u1").id},{id:"c",name:"ختام",min:20,drill:""}]}]')
        bad=[]
        for v in('home','drills','board','sess','players','more'):
            ev(f'go("{v}")');pg.wait_for_timeout(150)
            w=ev('[document.documentElement.scrollWidth,innerWidth,$("#main").scrollWidth,$("#main").clientWidth]')
            if w[0]>w[1]+1 or w[2]>w[3]+1:bad.append((v,w))
        ev('editS("s1")');pg.wait_for_timeout(150);w=ev('[document.documentElement.scrollWidth,innerWidth,$("#main").scrollWidth,$("#main").clientWidth]');(w[0]>w[1]+1 or w[2]>w[3]+1) and bad.append(('sedit',w))
        ev('startLive("s1")');pg.wait_for_timeout(250);w=ev('[document.documentElement.scrollWidth,innerWidth,$("#live").scrollWidth,$("#live").clientWidth]');(w[0]>w[1]+1 or w[2]>w[3]+1) and bad.append(('live',w))
        small=ev('[...document.querySelectorAll("#live button")].filter(x=>x.offsetParent&&x.getBoundingClientRect().height<36).map(x=>x.textContent)')
        ok(f'{vw}x{vh}: no horizontal overflow on any screen incl. live',not bad,bad);ok(f'{vw}x{vh}: live buttons >=36px tall',not small,small)
        if vw==360:pg.screenshot(path='/tmp/t/live360.png')
        ev('endLive()');ctx.close()
    ctx=b.new_context(viewport={'width':390,'height':780});pg=ctx.new_page();pg.on('pageerror',lambda e:errs.append(str(e)));pg.on('dialog',lambda d:d.dismiss() if 'حفظها' in d.message else d.accept());ev=pg.evaluate
    pg.goto(URL);pg.wait_for_timeout(600)
    ok('document is RTL Arabic',ev('document.documentElement.dir')=='rtl' and ev('document.documentElement.lang')=='ar')
    # theme persists
    ev('S.settings.theme="dark";theme();save()');pg.reload();pg.wait_for_timeout(600);ok('dark theme persists after reload',ev('document.documentElement.dataset.theme')=='dark')
    ev('S.settings.theme="light";theme();save()')
    # PIN + resume ordering
    ev('S.sessions=[{id:"s1",name:"حصة PIN",date:"2026-10-14",total:10,goal:"",att:{},eval:"",ph:[{id:"a",name:"إحماء",min:2,drill:""}]}];save()')
    ev('sha("1234").then(h=>{S.settings.pin=h;save()})');pg.wait_for_timeout(300);ev('startLive("s1")');pg.wait_for_timeout(200);ev('exitLive()');pg.reload();pg.wait_for_timeout(800)
    ok('with PIN: lock shown, resume prompt NOT shown before unlock',ev('$("#lock").style.display')=='flex' and pg.locator('text=حصة غير منتهية').count()==0)
    pg.fill('#pin','0000');ev('unlock()');pg.wait_for_timeout(300);ok('wrong PIN keeps it locked',ev('$("#lock").style.display')=='flex')
    pg.fill('#pin','1234');ev('unlock()');pg.wait_for_timeout(500);ok('correct PIN unlocks and then offers resume',ev('$("#lock").style.display')=='none' and pg.locator('text=حصة غير منتهية').count()==1)
    ev('closeM();delete S.settings.pin;save();lvDrop()')
    # restore a backup that lacks the live session -> state discarded, no crash, data intact
    ev('startLive("s1")');ev('exitLive()');snapS=ev('JSON.stringify(S)')
    ev('expB()');bk=json.loads(ev('$("#bk").value'));ev('closeM()');bk['data']['sessions']=[];
    # recompute integrity hash like the app (fnv1a over JSON of data)
    h=ev('(d)=>hs(JSON.stringify(d))',bk['data']);bk['h']=h
    ev('impB()');pg.fill('#ib',json.dumps(bk));ev('chkB()');ok('backup without the session passes integrity check',ev('!!BK'));ev('doB()');pg.reload();pg.wait_for_timeout(700)
    ok('restore removed the session; stale live state discarded; no crash',ev('S.sessions.length')==0 and ev('localStorage.getItem("nsu13_live")')is None and pg.locator('text=حصة غير منتهية').count()==0 and ev('S.drills.length')==150)
    # data survives close/reopen in a NEW page of same context (IndexedDB persistence)
    ev('S.players=[{id:"p9",name:"لاعب دائم",num:"9",pos:"",status:"نشط",notes:""}];save()');pg.wait_for_timeout(300);pg2=ctx.new_page();pg2.goto(URL);pg2.wait_for_timeout(700)
    ok('data persists in a freshly opened page (150 drills + player)',pg2.evaluate('S.drills.length')==150 and pg2.evaluate('S.players.some(p=>p.name==="لاعب دائم")'))
    # print preview at A4 for a revised 2-stage drill + session
    ev('S.sessions=[{id:"s1",name:"طباعة",date:"2026-10-14",total:40,goal:"هدف",att:{},eval:"ملاحظة",ph:[{id:"a",name:"إحماء",min:15,drill:S.drills.find(d=>d.name==="تمطيط وتهدئة").id},{id:"b",name:"رئيسي",min:25,drill:S.drills.find(d=>d.sid==="u1").id}]}]');ev('printSession("s1")');pg.emulate_media(media='print');pg.pdf(path='/tmp/t/final.pdf',format='A4',print_background=True,prefer_css_page_size=True)
    ok('print has revised safety + both diagram stages',('السلامة' in ev('$("#print").innerText')) and ev('document.querySelectorAll("#print img.di").length')>=4)
    ok('no JS errors / failed requests (all viewports)',not errs,errs[:4]);b.close()
print('%d/%d'%(sum(R),len(R)))
