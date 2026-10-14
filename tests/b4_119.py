import json
from playwright.sync_api import sync_playwright
R=[]
def ok(n,c,x=''):R.append(bool(c));print(('PASS ' if c else 'FAIL ')+n,x)
B='http://localhost:8765/'
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':390,'height':780}).new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)));pg.on('dialog',lambda d:d.accept());ev=pg.evaluate
    pg.goto(B+'old119.html');pg.wait_for_timeout(500);ev('expB()');oldbk=ev('$("#bk").value');ev('closeM()')
    pg.goto(B+'new.html');pg.wait_for_timeout(700)
    ok('total = 150',ev('S.drills.length')==150,ev('S.drills.length'));ok('ids+names unique',ev('new Set(S.drills.map(d=>d.id)).size')==150 and ev('new Set(S.drills.map(d=>d.name)).size')==150)
    ok('150 distinct effective diagrams',ev('new Set(S.drills.map(d=>hs(dgImg(d)))).size')==150)
    nos=ev('S.drills.filter(d=>d.cat!=="الإحماء"&&d.cat!=="التهدئة"&&!E(d).safe).map(d=>d.name)');ok('every non-warmup drill has a safety note',not nos,nos)
    ok('every drill has space',ev('S.drills.every(d=>E(d).space)'))
    ok('31 old drills + others revised, originals untouched',ev('S.drills.filter(d=>d.rev).length')==34 and ev('S.drills.filter(d=>d.rev&&!d.safe).length')==33)
    ok('revised diagrams differ from originals',all(ev(f'(()=>{{const d=S.drills.find(x=>x.name==="{n}"||x.sid==="{n}");const o={{...d}};delete o.rev;return hs(dgImgs(o,1)[0])!==hs(dgImgs(d)[0])}})()') for n in['تمطيط وتهدئة','إحماء بالكرة في دوائر','p3']))
    ok('gk2 no longer advanced with <4 min',ev('(()=>{const d=E(S.drills.find(x=>x.sid==="gk2"));return d.np==="3-6"})()'))
    ok('no advanced drill with min players <3',ev('S.drills.filter(d=>E(d).level==="متقدم"&&npr(d)[0]<3).length')==0)
    sid=ev('S.drills.find(d=>d.name==="لمسة وتوجيه").id');ev(f'viewDrill("{sid}")');t=ev('$("#modal").innerText')
    ok('view shows revised badge+safety',('نسخة محسّنة' in t) and 'السلامة' in t);ev(f'viewDrill("{sid}",1)');t2=ev('$("#modal").innerText');ok('original view hides revision (no safety)','السلامة' not in t2 and 'عرض المحسّنة' in t2);ev('closeM()')
    ev('go("drills")');ev(f'copyD("{sid}")');c=ev('S.drills[0]');ok('copy of revised keeps revised data, no rev',c.get('safe') and 'rev' not in c);ev(f'delD("{c["id"]}")')
    ok('counter unchanged after copy+delete',ev('S.drills.length')==150)
    ev('go("drills")');ev('fq="سلامة"');ev('dl()');ev('fq=""');
    ev(f'printDrill("{sid}")');ok('print shows revised safety',('السلامة' in ev('$("#print").innerText')));ev('$("#print").style.display="none"')
    ev('printDrill(S.drills.find(x=>x.name==="تمطيط وتهدئة").id)');ok('2-stage revised drill prints 2 images',ev('document.querySelectorAll("#print img.di").length')==2);ev('$("#print").style.display="none"')
    pg.reload();pg.wait_for_timeout(600);ok('idempotent after reload (still 150, revs kept)',ev('S.drills.length')==150 and ev('S.drills.filter(d=>d.rev).length')==34)
    ev('impB()');pg.fill('#ib',oldbk);ev('chkB()');ok('previous-version backup valid',ev('!!BK'));ev('doB()');ok('old backup restored then migrated to 150 + revisions',ev('S.drills.length')==150 and ev('S.drills.filter(d=>d.rev).length')==34,ev('S.drills.length'))
    ev('expB()');nb=ev('$("#bk").value');ev('closeM()');ev('S.drills=[];save()');ev('impB()');pg.fill('#ib',nb);ev('chkB()');ev('doB()');ok('new backup round-trip keeps revisions',ev('S.drills.length')==150 and ev('S.drills.filter(d=>d.rev).length')==34)
    ok('no JS errors',not errs,errs[:3]);b.close()
print('%d/%d'%(sum(R),len(R)))
