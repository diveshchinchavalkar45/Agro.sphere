import subprocess, time, json, urllib.request, websocket, base64

proc = subprocess.Popen([
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "--remote-debugging-port=9222",
    "--remote-allow-origins=*",
    "--headless",
    "--disable-gpu",
    "--window-size=1280,900",
    "http://localhost:8000"
])

time.sleep(2)

try:
    res = urllib.request.urlopen("http://localhost:9222/json").read()
    targets = json.loads(res.decode("utf-8"))
    page_target = [t for t in targets if t.get("type") == "page" and "localhost:8000" in t.get("url", "")][0]
    ws_url = page_target["webSocketDebuggerUrl"]

    ws = websocket.create_connection(ws_url)
    ws.send(json.dumps({"id": 1, "method": "Runtime.enable"}))
    ws.send(json.dumps({"id": 2, "method": "Page.enable"}))
    ws.send(json.dumps({"id": 3, "method": "Page.reload"}))

    time.sleep(2)

    # Screenshot Dashboard
    ws.send(json.dumps({"id": 4, "method": "Page.captureScreenshot", "params": {"format": "png"}}))
    while True:
        r = json.loads(ws.recv())
        if r.get("id") == 4:
            with open("dashboard_shot.png", "wb") as f:
                f.write(base64.b64decode(r["result"]["data"]))
            break
    print("Saved dashboard_shot.png")

    # Navigate to schedule and screenshot
    ws.send(json.dumps({"id": 5, "method": "Runtime.evaluate", "params": {"expression": "go('schedule')"}}))
    time.sleep(1)
    ws.send(json.dumps({"id": 6, "method": "Page.captureScreenshot", "params": {"format": "png"}}))
    while True:
        r = json.loads(ws.recv())
        if r.get("id") == 6:
            with open("schedule_shot.png", "wb") as f:
                f.write(base64.b64decode(r["result"]["data"]))
            break
    print("Saved schedule_shot.png")

    # Check computed styles of voice assistant button and calendar
    check_js = """
    (() => {
        const btn = document.querySelector('#voiceAssistantBtn');
        const dashCard = document.querySelector('.dashboard-voice-card');
        const cal = document.querySelector('.calendar-card');
        const calDays = document.querySelector('#calendarDays');
        return {
            voiceBtn: btn ? {
                display: window.getComputedStyle(btn).display,
                visibility: window.getComputedStyle(btn).visibility,
                opacity: window.getComputedStyle(btn).opacity,
                zIndex: window.getComputedStyle(btn).zIndex,
                position: window.getComputedStyle(btn).position,
                bottom: window.getComputedStyle(btn).bottom,
                right: window.getComputedStyle(btn).right,
                rect: btn.getBoundingClientRect()
            } : 'NO BTN',
            dashCard: dashCard ? {
                display: window.getComputedStyle(dashCard).display,
                rect: dashCard.getBoundingClientRect()
            } : 'NO DASH CARD',
            cal: cal ? {
                display: window.getComputedStyle(cal).display,
                rect: cal.getBoundingClientRect()
            } : 'NO CAL',
            calDaysChildren: calDays ? calDays.children.length : 0,
            calDaysHTML: calDays ? calDays.innerHTML.slice(0, 100) : 'EMPTY'
        };
    })()
    """
    ws.send(json.dumps({"id": 7, "method": "Runtime.evaluate", "params": {"expression": check_js, "returnByValue": True}}))
    while True:
        r = json.loads(ws.recv())
        if r.get("id") == 7:
            break
    print("Computed elements info:", json.dumps(r.get("result", {}), indent=2))

finally:
    proc.terminate()
