import subprocess, time, json, urllib.request, websocket, base64

proc = subprocess.Popen([
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "--remote-debugging-port=9222",
    "--remote-allow-origins=*",
    "--headless",
    "--disable-gpu",
    "--window-size=1280,950",
    "http://localhost:8000"
])

time.sleep(2)

try:
    res = urllib.request.urlopen("http://localhost:9222/json").read()
    targets = json.loads(res.decode("utf-8"))
    page_target = [t for t in targets if t.get("type") == "page" and "localhost:8000" in t.get("url", "")][0]
    ws_url = page_target["webSocketDebuggerUrl"]

    ws = websocket.create_connection(ws_url)
    ws.send(json.dumps({"id": 1, "method": "Page.enable"}))
    ws.send(json.dumps({"id": 2, "method": "Page.reload"}))

    time.sleep(2)

    # Open WhatsApp Bot modal & simulate photo grading query
    ws.send(json.dumps({"id": 3, "method": "Runtime.evaluate", "params": {"expression": "openWhatsAppBotModal(); sendWhatsAppBotOption('📸 Test Crop Photo Grading');"}}))
    time.sleep(2)

    # Capture WhatsApp Bot Screenshot
    ws.send(json.dumps({"id": 4, "method": "Page.captureScreenshot", "params": {"format": "png"}}))
    while True:
        r = json.loads(ws.recv())
        if r.get("id") == 4:
            with open("whatsapp_bot_reply.png", "wb") as f:
                f.write(base64.b64decode(r["result"]["data"]))
            break
    print("Saved whatsapp_bot_reply.png")

finally:
    proc.terminate()
