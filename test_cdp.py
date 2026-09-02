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

    # Enable Console and Runtime
    ws.send(json.dumps({"id": 1, "method": "Runtime.enable"}))
    ws.send(json.dumps({"id": 2, "method": "Log.enable"}))
    
    # Reload page
    ws.send(json.dumps({"id": 3, "method": "Page.reload"}))

    # Listen for 2 seconds
    start = time.time()
    while time.time() - start < 2:
        ws.settimeout(0.5)
        try:
            raw = ws.recv()
            msg = json.loads(raw)
            method = msg.get("method", "")
            if "exception" in method.lower() or "console" in method.lower() or "log" in method.lower():
                print("CDP Event:", msg)
        except websocket.WebSocketTimeoutException:
            pass

    # Test Voice Button & Modal
    test_eval = """
    (() => {
        const btn = document.querySelector('#voiceAssistantBtn');
        btn.click();
        const modal = document.querySelector('#voiceAssistantModal');
        return {
            hasVoiceBtn: !!btn,
            modalVisible: modal ? modal.classList.contains('show') : false
        };
    })()
    """
    ws.send(json.dumps({"id": 10, "method": "Runtime.evaluate", "params": {"expression": test_eval, "returnByValue": True}}))
    while True:
        res10 = json.loads(ws.recv())
        if res10.get("id") == 10:
            break
    print("Voice Modal Open Test:", json.dumps(res10.get("result", {}), indent=2))

    # Test Voice Simulation Query
    query_test = """
    (() => {
        simulateVoiceQuery('Onion ka mandi bhav kya hai?');
        return {
            dialogMsgsCount: document.querySelectorAll('.voice-msg').length,
            activeSection: document.querySelector('.section.active').id
        };
    })()
    """
    ws.send(json.dumps({"id": 11, "method": "Runtime.evaluate", "params": {"expression": query_test, "returnByValue": True}}))
    while True:
        res11 = json.loads(ws.recv())
        if res11.get("id") == 11:
            break
    print("Voice Query Simulation Test:", json.dumps(res11.get("result", {}), indent=2))

finally:
    proc.terminate()
