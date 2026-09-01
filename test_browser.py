import subprocess, time, json, urllib.request, socket

proc = subprocess.Popen([
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "--remote-debugging-port=9222",
    "--headless",
    "--disable-gpu",
    "http://localhost:8000"
])

time.sleep(2)

try:
    res = urllib.request.urlopen("http://localhost:9222/json").read()
    targets = json.loads(res.decode("utf-8"))
    page_target = None
    for t in targets:
        if t.get("type") == "page" and "localhost:8000" in t.get("url", ""):
            page_target = t
            break
    if not page_target:
        for t in targets:
            if t.get("type") == "page":
                page_target = t
                break
    
    print("Found page target:", page_target.get("title"), page_target.get("url"))
    ws_url = page_target.get("webSocketDebuggerUrl")
    print("WS URL:", ws_url)
finally:
    proc.terminate()
