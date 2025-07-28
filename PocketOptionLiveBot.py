import websocket
import threading
import time
from flask import Flask, jsonify

# بيانات WS وكوكيز مثل ما وضحنا فوق...
WS_URL = "wss://api-eu.po.market/socket.io/?EIO=4&transport=websocket"
COOKIES = "..."
USER_AGENT = "..."
REFERER = "..."
ORIGIN = "..."

last_signal = {"signal": "لا يوجد توصية بعد", "price": 0, "time": ""}

def on_message(ws, message):
    # عيّن بياناتك حسب التحليل
    print("WS Message:", message)
    # عدل السطر تحت حسب ما تستقبل من البيانات
    last_signal["signal"] = "CALL"  # أو "PUT" حسب تحليلك
    last_signal["price"] = ...      # السعر الحالي من الرسالة
    last_signal["time"] = time.strftime("%H:%M:%S")

def on_error(ws, error):
    print("❌ Error:", error)

def on_close(ws, close_status_code, close_msg):
    print("🔴 WebSocket Closed")
    time.sleep(5)
    run_ws()

def on_open(ws):
    print("✅ WebSocket Connection OPEN")

def run_ws():
    ws = websocket.WebSocketApp(
        WS_URL,
        header=[
            f"Cookie: {COOKIES}",
            f"User-Agent: {USER_AGENT}",
            f"Referer: {REFERER}",
            f"Origin: {ORIGIN}",
            "Accept-Language: en-US,en;q=0.9",
            "Accept-Encoding: gzip, deflate, br",
            "Connection: Upgrade"
        ],
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()

# شغل WS في ثريد جانبي
threading.Thread(target=run_ws, daemon=True).start()

# كود Flask لعرض آخر توصية في صفحة ويب
app = Flask(__name__)

@app.route("/")
def home():
    return jsonify(last_signal)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
