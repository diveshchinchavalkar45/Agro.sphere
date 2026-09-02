import subprocess, time, json, urllib.request, websocket, base64
from PIL import Image, ImageDraw, ImageFont

# 1. Capture additional UI screenshots: Prices and Product Inspection
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
    ws.send(json.dumps({"id": 1, "method": "Page.enable"}))
    ws.send(json.dumps({"id": 2, "method": "Runtime.enable"}))

    # Navigate to Prices
    ws.send(json.dumps({"id": 3, "method": "Runtime.evaluate", "params": {"expression": "go('prices')"}}))
    time.sleep(1)
    ws.send(json.dumps({"id": 4, "method": "Page.captureScreenshot", "params": {"format": "png"}}))
    while True:
        r = json.loads(ws.recv())
        if r.get("id") == 4:
            with open("prices_shot.png", "wb") as f:
                f.write(base64.b64decode(r["result"]["data"]))
            break
    print("Saved prices_shot.png")

    # Navigate to Products and open Quality Modal
    ws.send(json.dumps({"id": 5, "method": "Runtime.evaluate", "params": {"expression": "go('products'); setTimeout(() => openQualityModal(state.products[0]), 300);"}}))
    time.sleep(1)
    ws.send(json.dumps({"id": 6, "method": "Page.captureScreenshot", "params": {"format": "png"}}))
    while True:
        r = json.loads(ws.recv())
        if r.get("id") == 6:
            with open("products_modal_shot.png", "wb") as f:
                f.write(base64.b64decode(r["result"]["data"]))
            break
    print("Saved products_modal_shot.png")

finally:
    proc.terminate()

# 2. Generate Flowchart Image for Technical Architecture & Workflow
flowchart_img = Image.new("RGB", (900, 360), color="#f4f9f2")
draw = ImageDraw.Draw(flowchart_img)

# Steps: [Farmer / FPO Input] -> [AI Price Discovery & Grading] -> [Smart Match & Collective Pool] -> [Logistics & Live Tracking] -> [Weighbridge & Instant Payment]
boxes = [
    ("1. Produce Ingestion", "Farmer lists lot / Voice AI\nGrade A/B & Fast Clearance", "#173a25", "#ffffff"),
    ("2. Intelligence Layer", "Agro-Sphere Price Engine\nAPMC Mandi Trend Analysis", "#2b7428", "#ffffff"),
    ("3. Collective Pooling", "Small Lots Aggregate\nDirect Corporate Buyer Bids", "#3c8c38", "#ffffff"),
    ("4. Logistics Dispatch", "Smart Calendar Booking\nLive Truck (MH-15) GPS", "#58a354", "#ffffff"),
    ("5. Settlement & Trust", "Digital Scale Verification\nInstant NEFT Payment & Care", "#173a25", "#ffffff")
]

x = 20
box_w = 155
box_h = 240
y = 60

for i, (title, sub, bg, fg) in enumerate(boxes):
    # Draw box
    draw.rounded_rectangle([x, y, x + box_w, y + box_h], radius=12, fill=bg, outline="#c2e6bc", width=2)
    # Text
    draw.text((x + 12, y + 20), title, fill="#b8e86a")
    draw.text((x + 12, y + 65), sub, fill=fg)
    
    # Arrow to next
    if i < len(boxes) - 1:
        arr_x = x + box_w + 5
        arr_y = y + box_h // 2
        draw.polygon([(arr_x, arr_y - 8), (arr_x + 14, arr_y), (arr_x, arr_y + 8)], fill="#2b7428")
        draw.line([(arr_x - 5, arr_y), (arr_x + 10, arr_y)], fill="#2b7428", width=3)
    
    x += box_w + 22

flowchart_img.save("architecture_flowchart.png")
print("Saved architecture_flowchart.png")
