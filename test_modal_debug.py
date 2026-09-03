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

    eval_script = """
    (() => {
        openWhatsAppBotModal();
        const m = document.getElementById("whatsappBotModal");
        const parent = m.parentElement;
        const rect = m.getBoundingClientRect();
        return {
            modalHTML: m.outerHTML.slice(0, 120),
            parentTag: parent.tagName,
            parentClass: parent.className,
            rect: { top: rect.top, left: rect.left, width: rect.width, height: rect.height },
            computedDisplay: window.getComputedStyle(m).display,
            computedZIndex: window.getComputedStyle(m).zIndex
        };
    })()
    """
    ws.send(json.dumps({"id": 2, "method": "Runtime.evaluate", "params": {"expression": eval_script, "returnByValue": True}}))
    while True:
        r = json.loads(ws.recv())
        if r.get("id") == 2:
            print("Modal debug info:", json.dumps(r, indent=2))
            break
finally:
    proc.terminate()
