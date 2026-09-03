import subprocess, time, json, urllib.request, websocket

proc = subprocess.Popen([
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "--remote-debugging-port=9222",
    "--remote-allow-origins=*",
    "--headless",
    "--disable-gpu",
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

    eval_script = """
    (() => {
        openWhatsAppBotModal();
        const m = document.getElementById("whatsappBotModal");
        const style = window.getComputedStyle(m);
        return {
            classes: m.className,
            display: style.display,
            zIndex: style.zIndex,
            opacity: style.opacity,
            visibility: style.visibility,
            top: m.getBoundingClientRect().top,
            height: m.getBoundingClientRect().height
        };
    })()
    """
    ws.send(json.dumps({"id": 4, "method": "Runtime.evaluate", "params": {"expression": eval_script, "returnByValue": True}}))
    while True:
        r = json.loads(ws.recv())
        if r.get("id") == 4:
            print("Modal computed style:", json.dumps(r, indent=2))
            break
finally:
    proc.terminate()
