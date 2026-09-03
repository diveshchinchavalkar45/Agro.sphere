import subprocess, time, json, urllib.request, websocket, base64

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

    # Test Live Sync with Backend
    test_eval = """
    (() => {
        return {
            productsCount: state.products.length,
            firstProduct: state.products[0].crop,
            hasBackendToast: document.querySelector('.toast') ? document.querySelector('.toast').textContent : 'NONE'
        };
    })()
    """
    ws.send(json.dumps({"id": 10, "method": "Runtime.evaluate", "params": {"expression": test_eval, "returnByValue": True}}))
    while True:
        r = json.loads(ws.recv())
        if r.get("id") == 10:
            break
    print("Backend + Frontend Connection Test:", json.dumps(r.get("result", {}), indent=2))

    # Test Listing a New Product to Backend via Frontend
    list_test = """
    (() => {
        const testItem = {
            crop: "Organic Guava (अमरूद)",
            category: "fruits",
            grade: "Premium",
            location: "Nashik",
            qty: 35,
            price: 5200,
            img: "https://images.unsplash.com/photo-1536511132770-e5058c7e8c46?q=80&w=687&auto=format&fit=crop",
            e: "🍐",
            buyer: "AgroFresh Direct",
            isUrgent: true,
            sizeSpec: "Large Sweet Variety",
            freshnessSpec: "Tree Ripened",
            packagingSpec: "20kg Crates",
            pesticideSpec: "Organic Certified",
            harvestSpec: "Harvested Today"
        };
        syncProductToBackend(testItem);
        return { status: "sent" };
    })()
    """
    ws.send(json.dumps({"id": 11, "method": "Runtime.evaluate", "params": {"expression": list_test, "returnByValue": True}}))
    while True:
        r11 = json.loads(ws.recv())
        if r11.get("id") == 11:
            break
    
    time.sleep(2)

    # Check that product is saved in SQLite database
    db_check = urllib.request.urlopen("http://127.0.0.1:5000/api/products").read()
    db_items = json.loads(db_check.decode("utf-8"))
    print("Total items in Backend DB:", len(db_items))
    print("Latest listed crop in DB:", db_items[0]["crop"], f"({db_items[0]['qty']}q at ₹{db_items[0]['price']}/q)")

finally:
    proc.terminate()
