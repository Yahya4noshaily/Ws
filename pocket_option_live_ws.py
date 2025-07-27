
import websocket
import json
import time

SSID = "de1c620ff12ee405626bef1b68878747"
WS_URL = "wss://api-spb.po.market/socket.io/?EIO=4&transport=websocket"

def on_message(ws, message):
    if '42["tick' in message:
        try:
            data_str = message.split('42')[1]
            payload = json.loads(data_str)[1]
            symbol = payload.get("symbol")
            price = payload.get("value")
            timestamp = payload.get("ts")
            print(f"✅ {symbol} @ {price} | {timestamp}")
        except:
            pass

def on_open(ws):
    print("🟢 Connected to Pocket Option WebSocket")
    ws.send('40')
    time.sleep(1)
    ws.send(f'42["auth",{{"ssid":"{SSID}"}}]')
    time.sleep(1)
    ws.send('42["subscribe",{"symbol":"EURUSD-OTC"}]')

def on_error(ws, error):
    print(f"❌ Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("🔴 WebSocket closed")

if __name__ == "__main__":
    websocket.enableTrace(False)
    ws = websocket.WebSocketApp(
        WS_URL,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()
