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

    # Evaluate JS tests
    test_eval = """
    (() => {
        return {
            stateProductsLength: window.state ? window.state.products.length : 'NO STATE',
            productsGridHTMLCount: document.querySelector('#productsGrid') ? document.querySelector('#productsGrid').children.length : 'NO GRID',
            reviewsCount: document.querySelector('#reviews') ? document.querySelector('#reviews').children.length : 'NO REVIEWS',
            catTabsCount: document.querySelectorAll('.cat-tab').length,
            searchElem: !!document.querySelector('#search'),
            activeSection: document.querySelector('.section.active') ? document.querySelector('.section.active').id : 'NONE'
        };
    })()
    """
    ws.send(json.dumps({"id": 10, "method": "Runtime.evaluate", "params": {"expression": test_eval, "returnByValue": True}}))
    while True:
        res_msg = json.loads(ws.recv())
        if res_msg.get("id") == 10:
            break
    print("Test Results:", json.dumps(res_msg.get("result", {}), indent=2))

    # Test navigating to products
    ws.send(json.dumps({"id": 11, "method": "Runtime.evaluate", "params": {"expression": "go('products')", "returnByValue": True}}))
    time.sleep(0.5)
    ws.send(json.dumps({"id": 12, "method": "Runtime.evaluate", "params": {"expression": "document.querySelector('.section.active').id", "returnByValue": True}}))
    while True:
        res12 = json.loads(ws.recv())
        if res12.get("id") == 12:
            break
    print("Active Section after go('products'):", res12.get("result", {}).get("result", {}).get("value"))

    # Test typing in global search
    search_test = """
    (() => {
        const s = document.querySelector('#search');
        s.value = 'onion';
        s.dispatchEvent(new Event('input', { bubbles: true }));
        return {
            activeSectionAfterSearch: document.querySelector('.section.active').id
        };
    })()
    """
    ws.send(json.dumps({"id": 13, "method": "Runtime.evaluate", "params": {"expression": search_test, "returnByValue": True}}))
    while True:
        res13 = json.loads(ws.recv())
        if res13.get("id") == 13:
            break
    print("Search Test Result:", json.dumps(res13.get("result", {}), indent=2))

finally:
    proc.terminate()
