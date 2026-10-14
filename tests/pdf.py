from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':390,'height':780},has_touch=True,is_mobile=True).new_page()
    errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('http://localhost:8765/noun-star-u13.html');pg.wait_for_timeout(500);ev=pg.evaluate
    ev('''(()=>{B=newB();B.name="لوحة الضغط";B.pt="half";B.frames[0].p=[P("a",.3,.5,1),P("b",.6,.4,1),P("ball",.35,.5),P("goal",.5,.06)];B.frames[0].a=[A("pass",.3,.5,.6,.6)];B.frames.push(JSON.parse(JSON.stringify(B.frames[0])));S.boards=[B];
    S.sessions=[{id:"s1",name:"حصة الاختبار",date:"2026-10-14",total:60,goal:"تحسين التمرير",att:{},eval:"ملاحظات المدرب: تفاعل جيد",ph:[{id:"1",name:"الإحماء",min:15,drill:S.drills[0].id},{id:"2",name:"التمرير",min:25,drill:S.drills.find(d=>d.sid==="p3").id,board:B.id},{id:"3",name:"مباراة",min:30,drill:S.drills.find(d=>d.sid==="m2").id}]}]})()''')
    ev('printSession("s1")');pg.wait_for_timeout(300)
    pg.emulate_media(media='print');pg.pdf(path='/tmp/t/session.pdf',format='A4',print_background=True,prefer_css_page_size=True)
    ev('printDrill(S.drills[3].id)') if False else None
    print('errors',errs);b.close()
