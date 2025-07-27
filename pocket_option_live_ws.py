
import websocket
import json
import threading

WS_URL = "wss://api-spb.po.market/socket.io/?EIO=4&transport=websocket"
SSID = "de1c620ff12ee405626bef1b68878747"

def on_message(ws, message):
    if "EUR/USD" in message or "price" in message:
        print(f"[RECEIVED] {message}")

def on_error(ws, error):
    print(f"[ERROR] {error}")

def on_close(ws, close_status_code, close_msg):
    print("[CLOSED] Connection closed")

def on_open(ws):
    print("[OPENED] WebSocket connection established")

    # إرسال SSID كبداية للربط
    auth_msg = f'42["authenticate",{{"ssid":"{SSID}"}}]'
    ws.send(auth_msg)

    # الاشتراك في السوق EUR/USD OTC
    subscribe_msg = '42["subscribe",{"market":"EURUSD_OTC"}]'
    ws.send(subscribe_msg)

# تشغيل WebSocket
def run():
    ws = websocket.WebSocketApp(WS_URL,
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.run_forever()

# تشغيله في Thread منفصل
thread = threading.Thread(target=run)
thread.start()
