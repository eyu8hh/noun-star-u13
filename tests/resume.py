import json,sys
from playwright.sync_api import sync_playwright
R=[];errs=[]
def ok(n,c,x=''):R.append(bool(c));print(('PASS ' if c else 'FAIL ')+n,x)
URL=sys.argv[1] if len(sys.argv)>1 else 'http://localhost:8765/new.html'
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':390,'height':780});pg=ctx.new_page()
    pg.on('pageerror',lambda e:errs.append(str(e)));SAVE=[False]
    pg.on('dialog',lambda d:(d.accept() if SAVE[0] else d.dismiss()) if 'حفظها' in d.message else d.accept())
    ev=pg.evaluate
    def load():pg.goto(URL);pg.wait_for_timeout(700)
    def reload():pg.reload();pg.wait_for_timeout(700)
    def shift(ms):ev('(()=>{const o=JSON.parse(localStorage.nsu13_live);o.ref-=%d;localStorage.nsu13_live=JSON.stringify(o);clearInterval(LT);LV=null})()'%ms)  # simulate the app being killed: no further writes
    def resume():pg.click('text=استئناف الحصة');pg.wait_for_timeout(300)
    def key():return ev('localStorage.getItem("nsu13_live")')
    load()
    ev('S.players=[{id:"p1",name:"لاعب أ",num:"1",pos:"",status:"نشط",notes:""}]')
    ev('S.sessions=[{id:"s1",name:"حصة الاستعادة",date:"2026-10-14",total:4,goal:"",att:{},eval:"تقييم سابق",ph:[{id:"a",name:"إحماء",min:2,drill:S.drills[0].id},{id:"b",name:"رئيسي",min:1,drill:S.drills[1].id},{id:"c",name:"ختام",min:1,drill:""}]}]');ev('save()')
    lib=ev('JSON.stringify(S.drills)');keys=ev('Object.keys(S).join()');ndr=ev('S.drills.length')
    # 1 running timer, app closed
    ev('startLive("s1")');pg.click('#lvp');pg.wait_for_timeout(300);shift(30000);reload()
    ok('prompt appears on reopen',pg.locator('text=حصة غير منتهية').count()==1 and 'حصة الاستعادة' in ev('$("#modal").innerText'))
    resume();l=ev('LV.left')
    ok('running timer restored using timestamps (~120-30s)',ev('LV.run')==True and 88<=l<=91,l)
    # 2 paused
    pg.click('text=إيقاف مؤقت');pg.wait_for_timeout(200);shift(600000);reload();resume()
    ok('paused timer restored, no time lost while closed',ev('LV.run')==False and abs(ev('LV.left')-l)<3 and ev('$("#lvp").textContent')=='ابدأ',ev('LV.left'))
    # 3 time ended while closed
    pg.click('#lvp');shift(150000);reload();resume()
    ok('time ended while closed -> overtime, no auto-advance, no re-beep',ev('LV.left')<0 and ev('LV.i')==0 and ev('LV.beeped')==True and ev('$("#lvc").textContent').startswith('+'),ev('$("#lvc").textContent'))
    # 4 phase change + duration change
    ev('lvGo(1)');ev('lvAdj(1)');ev('lvAdj(1)');reload();resume()
    ok('phase + temporary duration change restored',ev('LV.i')==1 and ev('LV.adj[1]')==120 and ev('LV.len')==180,(ev('LV.i'),ev('LV.len')))
    ok('session durations/library untouched',ev('S.sessions[0].ph[1].min')==1 and ev('JSON.stringify(S.drills)')==lib)
    ev('lvGo(-1)');ev('lvGo(1)');ok('returning to an adjusted phase keeps the adjustment',ev('LV.left')==180)
    # 5 unsaved attendance + note survive; saved once; crash-duplicate safe
    ev('lvAtt("p1")');pg.locator('details:has-text("ملاحظات الحصة") summary').click();pg.fill('#live textarea','ملاحظة غير محفوظة');pg.wait_for_timeout(1200)
    ok('nothing written to the session yet',ev('S.sessions[0].eval')=='تقييم سابق' and ev('S.sessions[0].att.p1')is None)
    saved=key();reload();resume()
    ok('unsaved attendance+note restored',ev('LV.att.p1')=='p' and ev('LV.note')=='ملاحظة غير محفوظة')
    ev('lvSave()');pg.wait_for_timeout(200)
    ev('localStorage.setItem("nsu13_live",%s)'%json.dumps(saved))  # simulate crash before state was cleared
    reload();resume();ev('lvSave()');pg.wait_for_timeout(200)
    e=ev('S.sessions[0].eval');ok('note appended exactly once (idempotent), old evaluation kept',e.count('ملاحظة غير محفوظة')==1 and e.startswith('تقييم سابق') and ev('S.sessions.length')==1,e)
    # 6 end session -> never restored
    SAVE[0]=False;pg.click('#live button:text-is("إنهاء")');pg.wait_for_timeout(300)
    ok('end clears resume state',key()is None and ev('$("#live").style.display')=='none');reload()
    ok('not offered again after ending',pg.locator('text=حصة غير منتهية').count()==0 and ev('S.sessions.length')==1)
    # 7 finished + saved -> cleared
    ev('startLive("s1")');ev('lvGo(1)');ev('lvGo(1)');ev('lvGo(1)');ev('LV.note="ختام";lvPersist(true)');reload();ok('finished-but-unsaved session is offered',pg.locator('text=حصة غير منتهية').count()==1)
    resume();ev('lvSave()');pg.wait_for_timeout(200);ok('finished + saved: state cleared',key()is None);reload();ok('no prompt afterwards',pg.locator('text=حصة غير منتهية').count()==0)
    # 8 stale / corrupt / deleted
    ev('startLive("s1")');shift(13*3600*1000);reload();ok('stale (>12h) state discarded with notice',pg.locator('text=حصة غير منتهية').count()==0 and key()is None)
    ev('localStorage.setItem("nsu13_live","{bad json")');reload();ok('corrupt state discarded, app still works',key()is None and ev('S.drills.length')==ndr)
    ev('startLive("s1")');ev('S.sessions=[];save()');reload();ok('state of a deleted session discarded',key()is None)
    ev('S.sessions=[{id:"s1",name:"حصة الاستعادة",date:"2026-10-14",total:4,goal:"",att:{},eval:"",ph:[{id:"a",name:"إحماء",min:2,drill:""}]}];save()')
    # 9 write failure warning
    ev('(()=>{Object.defineProperty(window,"localStorage",{get(){throw new Error("denied")},configurable:true})})()');ev('startLive("s1")')
    ok('failed autosave shows a visible warning',ev('LV.saveFail')==True and ev('$("#lvw").style.display')=='block');ev('LV.saveFail=false;lvClear()')
    reload()
    # 10 light writes
    ev('(()=>{window._w=0;const o=Storage.prototype.setItem;Storage.prototype.setItem=function(k,v){if(k==="nsu13_live")window._w++;return o.call(this,k,v)}})()')
    ev('startLive("s1")');pg.click('#lvp');w0=ev('window._w');pg.wait_for_timeout(4000);ok('no periodic writes while timer runs',ev('window._w')==w0,(w0,ev('window._w')))
    pg.locator('details:has-text("ملاحظات الحصة") summary').click();pg.type('#live textarea','abcdefghijklmnopqrst',delay=15);pg.wait_for_timeout(1500);ok('typing a note = 1 debounced write',ev('window._w')-w0==1,ev('window._w')-w0)
    # 11 banner on home + start while state exists offers resume (no duplicate)
    ev('exitLive()');ev('go("home")');pg.wait_for_timeout(200);ok('home banner offers resume',pg.locator('text=حصة جارية').count()>=1)
    ev('go("sess")');ev('startLive("s1")');pg.wait_for_timeout(200);ok('starting again offers resume instead of a second run',pg.locator('text=حصة غير منتهية').count()==1 and ev('LV')is None);ev('closeM()')
    ev('lvResume()');pg.wait_for_timeout(300);ev('endLive(0)')
    # 12 backup/restore unaffected + data safe
    ev('expB()');bk=ev('$("#bk").value');ev('closeM()')
    ok('live state not in backup; library + schema intact',('nsu13_live' not in bk) and ev('S.drills.length')==ndr and ev('JSON.stringify(S.drills)')==lib and ev('Object.keys(S).join()')==keys)
    ok('no JS errors',not errs,errs[:3]);b.close()
print('%d/%d'%(sum(R),len(R)))
