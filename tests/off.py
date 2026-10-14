from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args=['--no-sandbox'])
    c=b.new_context(viewport={'width':390,'height':780});pg=c.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('http://localhost:8766/index.html');pg.wait_for_timeout(500)
    pg.evaluate('navigator.serviceWorker.ready.then(()=>1)');pg.wait_for_timeout(1500)
    print('sw controlling:',pg.evaluate('!!navigator.serviceWorker.controller') or pg.evaluate('navigator.serviceWorker.ready.then(r=>!!r.active)'))
    pg.evaluate('S.players.push({id:"x1",name:"لاعب دون اتصال",num:"5",pos:"",status:"نشط",notes:""});save()');pg.wait_for_timeout(300)
    c.set_offline(True);pg.goto('http://localhost:8766/index.html');pg.wait_for_timeout(800)
    ok=pg.evaluate('S.drills.length')==150 and pg.evaluate('S.players.some(p=>p.name==="لاعب دون اتصال")')
    pg.evaluate('go("board")');pg.evaluate('exportPNG()')
    print('OFFLINE reload: app loads + data persists:',ok,'| png export offline:',pg.evaluate('document.querySelector("#modal img").src.startsWith("data:image/png")'),'| errors',errs)
    b.close()
