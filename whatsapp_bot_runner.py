"""
Agro-Sphere — Dedicated Real WhatsApp Bot Runner
Standard Python (Built-in urllib) — No external dependencies required
"""

import urllib.request
import json

def test_local_webhook():
    print("🌾 Testing Real WhatsApp Bot Engine & Webhook...")
    test_queries = [
        ("1. Farmer asks Mandi Bhav in Hindi", "प्याज और टमाटर का आज का मंडी भाव क्या है?"),
        ("2. Farmer asks Truck Location in English", "Where is my truck MH-15-AB-1234?"),
        ("3. Farmer sends Crop Photo", "Photo of Onion crop attached", True),
        ("4. Farmer asks for Field Officer Help", "Connect me with Lasalgaon APMC officer")
    ]
    
    for title, query, *photo in test_queries:
        has_photo = photo[0] if photo else False
        payload = json.dumps({"message": query, "has_photo": has_photo}).encode("utf-8")
        req = urllib.request.Request(
            "http://127.0.0.1:5000/api/whatsapp/chat",
            data=payload,
            headers={"Content-Type": "application/json"}
        )
        try:
            res = urllib.request.urlopen(req)
            data = json.loads(res.read().decode("utf-8"))
            print(f"\n==========================================")
            print(f"👉 {title}")
            print(f"📥 Received from WhatsApp: {query}")
            print(f"📤 WhatsApp Bot Sent Back:\n{data['reply']}")
        except Exception as e:
            print(f"Error querying backend: {e}")

if __name__ == "__main__":
    test_local_webhook()
