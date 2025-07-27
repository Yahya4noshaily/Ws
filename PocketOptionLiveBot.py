import websocket
import json
import threading
import time

WS_URL = "wss://api-spb.po.market/socket.io/?EIO=4&transport=websocket"
CI_SESSION = 'a:4:{s:10:"session_id";s:32:"de1c620ff12ee405626bef1b68878747";...}'
USER_AGENT = "Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Mobile/15E148 Safari/604.1"

# سجل الأسعار والشمعات
prices = []
SIGNAL_LENGTH = 10
last_signal = None
loss_flag = False

def filter_trend(prices):
    # إذا كان آخر 10 شمعات متجهة لنفس الاتجاه بقوة
    up = sum(1 for i in range(1, len(prices)) if prices[i] > prices[i-1])
    down = sum(1 for i in range(1, len(prices)) if prices[i] < prices[i-1])
    if up >= 8:
        return "UP"
    elif down >= 8:
        return "DOWN"
    else:
        return None

def volatility_filter(prices):
    # يدخل فقط إذا كان الفرق بين أعلى وأقل سعر كبير (أي السوق غير متذبذب)
    return max(prices) - min(prices) > 0.0004

def triple_confluence(prices):
    # ثلاث شروط: الترند + قوة الحركة + حركة آخر شمعتين بنفس الاتجاه
    trend = filter_trend(prices)
    strong_move = volatility_filter(prices)
    same_last2 = prices[-1] > prices[-2] if trend == "UP" else prices[-1] < prices[-2]
    return trend, strong_move, same_last2

def on_message(ws, message):
    global last_signal, loss_flag
    try:
        # فك الداتا (مثال: تحتاج تعدل حسب شكل رسائل ws عندك)
        if '"EURUSD"' in message and 'price' in message:
            data = json.loads(message)
            price = float(data.get('price', 0))
            prices.append(price)
            if len(prices) > SIGNAL_LENGTH:
                prices.pop(0)
            # بعد ما يتجمع 10 أسعار
            if len(prices) >= SIGNAL_LENGTH:
                trend, strong_move, same_last2 = triple_confluence(prices)
                if trend and strong_move and same_last2 and not loss_flag:
                    if trend == "UP":
                        print("🚀 توصية: شراء (CALL) - دقيقة واحدة ✅")
                        last_signal = "CALL"
                    elif trend == "DOWN":
                        print("⬇️ توصية: بيع (PUT) - دقيقة واحدة ✅")
                        last_signal = "PUT"
                    else:
                        print("⏸️ لا توجد توصية حالياً.")
                else:
                    print("⏸️ لا توجد توصية، بانتظار قوة إشارة/فلترة تذبذب/تأكيد ثلاثي...")
    except Exception as e:
        print("Error parsing message:", e)

def on_error(ws, error):
    print(f"❌ Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("🔴 WebSocket Closed")

def on_open(ws):
    print("✅ WebSocket Connection OPEN")

def run_ws():
    ws = websocket.WebSocketApp(
        WS_URL,
        header=[
            f"Cookie: ci_session={CI_SESSION}",
            f"User-Agent: {USER_AGENT}"
        ],
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()

if __name__ == "__main__":
    run_ws()
