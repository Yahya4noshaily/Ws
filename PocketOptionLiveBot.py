import websocket
import threading
import time
import json
from flask import Flask, jsonify, render_template_string, request

# بياناتك الحقيقية (كوكيزك كامل)
WS_URL = "wss://api-eu.po.market/socket.io/?EIO=4&transport=websocket"
COOKIES = '''ci_session=a%3A4%3A%7Bs%3A10%3A%22session_id%22%3Bs%3A32%3A%22c9ce4ad1f4059df4d39a864e01fd8e00%22%3Bs%3A10%3A%22ip_address%22%3Bs%3A12%3A%22151.255.8.27%22%3Bs%3A10%3A%22user_agent%22%3Bs%3A120%3A%22Mozilla%2F5.0%20%28iPhone%3B%20CPU%20iPhone%20OS%2018_5%20like%20Mac%20OS%20X%29%20AppleWebKit%2F605.1.15%20%28KHTML%2C%20like%20Gecko%29%20Version%2F18.5%20Mobile%2F15E1%22%3Bs%3A13%3A%22last_activity%22%3Bi%3A1753660887%3B%7D5c0bb00fd4b062f0c98b368b8b4ffdfd; lang=en; loggedIn=1; no-login-captcha=1; _gcl_au=1.1.63045385.1753479369.455749598.1753660880.1753660885; ttcsid=1753660869109::TG3uxSwnU0q_zrWB7A7M.14.1753660885700; ttcsid_CPC6SBRC77U2IO5KPOI0=1753660869108::k7yGGhhtXO1zxP3hG8y1.13.1753660885708; _ga_8D1Z2CLK9Z=GS2.1.s1753660868$o12$g1$t1753660879$j49$l0$h0; _fbp=fb.1.1753479369430.673956421940525777; _scid_r=r1zXWEKnrc709hHDvF56Lonhk9iSaMKHd0aHeQ; _tt_enable_cookie=1; _ttp=01K11R7N72JN6YG53JYWRV1PFB_.tt.1; _uetsid=612df600699f11f087e52f514f1697e6; _uetvid=612e3100699f11f0a5f225a12ecda212; afUserId=6f349eb9-051e-4c5a-b986-9abd3e891bba-p; lo_uid=1753479369243-6z3m0k95i56; _ga=GA1.1.631716718.1753479369; zoom-width=[[1%2C1%2C2.1156]]; a=H7rrXy9zejWAmb; ac=kuzonall; af_message=affiliate; cl_id=385044760; code=50START; gclid=Cj0KCQjwnJfEBhCzARIsAIMtfKI01HASeubPDIlgXySL7BzEmFgqWp2nVj9R_wj3ZSLwBkR4KRSYUAsaAhQsEALw_wcB; link_id=1307141; reg_url=utm_campaign%3D792386%26utm_source%3Daffiliate%26utm_medium%3Drevshare%26a%3DH7rrXy9zejWAmb%26ac%3Dkuzonall%26code%3D50START%26gad_source%3D1%26gad_campaignid%3D21844303173%26gbraid%3D0AAAAAqhZgo4AbqtCOXie7KEfaZ6z3ds23%26gclid%3DCj0KCQjwnJfEBhCzARIsAIMtfKI01HASeubPDIlgXySL7BzEmFgqWp2nVj9R_wj3ZSLwBkR4KRSYUAsaAhQsEALw_wcB; t=0; utm_campaign=792386; utm_medium=revshare; utm_source=affiliate; is_pwa=0; _sctr=1%7C1753650000000; _screload=; _scid=qVzXWEKnrc709hHDvF56Lonhk9iSaMKHd0aHcw; AF_SYNC=1753568662568; chat_room=125785264; chat_tab=chats; be_chart-1=collapsed; click_id=1n2nllc2n0j; chat_opened=1; is_pwa=0; referer=https%3A%2F%2Fpayments.exsolution.com%2F; ftw=1; guide=1; _gcl_aw=GCL.1753479383.CjwKCAjw1ozEBhAdEiwAn9qbzVeD1FAkRbJOPu_l1Y9JkjowYBISiHN58LIkYjiINSW6xoI22e5ZXxoCyAYQAvD_BwE; uuid=6357c590-b25e-471b-8177-d74dd98df775'''

USER_AGENT = "Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Mobile/15E148 Safari/604.1"
REFERER = "https://m.pocketoption.com/en/login"
ORIGIN = "https://m.pocketoption.com"

# متغير عالمي لحفظ آخر توصية
last_signal = {
    "signal": "لا يوجد توصية بعد",
    "price": 0,
    "market": "EUR/USD OTC",
    "time": "",
    "strategy": ""
}

prices = []
SIGNAL_LENGTH = 14  # تحليل 14 شمعة دقيقة

def advanced_scalping_strategy(prices):
    if len(prices) < SIGNAL_LENGTH:
        return None, ""
    sma_short = sum(prices[-5:]) / 5
    sma_long = sum(prices[-SIGNAL_LENGTH:]) / SIGNAL_LENGTH
    last_price = prices[-1]
    momentum = last_price - prices[-5]
    if last_price > sma_short > sma_long and momentum > 0:
        return "CALL", "SMA/قوة زخم صاعد"
    elif last_price < sma_short < sma_long and momentum < 0:
        return "PUT", "SMA/قوة زخم هابط"
    else:
        return None, ""

def on_message(ws, message):
    global last_signal, prices
    try:
        data = json.loads(message)
        # ** عدّل هنا إذا شكل بيانات WS عندك يختلف **
        if isinstance(data, dict) and 'price' in data:
            price = float(data['price'])
            prices.append(price)
            if len(prices) > SIGNAL_LENGTH:
                prices.pop(0)
            signal, strat = advanced_scalping_strategy(prices)
            if signal:
                last_signal = {
                    "signal": "شراء" if signal == "CALL" else "بيع",
                    "price": price,
                    "market": "EUR/USD OTC",
                    "time": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "strategy": strat
                }
                print(f"🚀 توصية: {last_signal['signal']} | سعر: {price} | وقت: {last_signal['time']} | استراتيجية: {strat}")
    except Exception as e:
        pass

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

# شغل WS في Thread منفصل
threading.Thread(target=run_ws, daemon=True).start()

# واجهة ويب بـ Flask
app = Flask(__name__)

HTML = '''
<!doctype html>
<html>
<head>
    <title>توصيات سكالبنج لايف EUR/USD OTC</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Tahoma, Arial; direction: rtl; background: #f2f2f2; color: #222; }
        .box { margin: 40px auto; background: #fff; border-radius: 10px; box-shadow: 0 4px 14px #0002; max-width: 400px; padding: 30px; }
        .buy { color: green; }
        .sell { color: red; }
        .btn { background: #1164e4; color: #fff; border: none; padding: 8px 24px; border-radius: 4px; font-size: 18px; margin: 15px 0 0 0;}
    </style>
</head>
<body>
<div class="box">
    <h2>توصية سكالبنج لايف</h2>
    <b>السوق:</b> {{ market }}<br>
    <b>الوقت:</b> {{ time }}<br>
    <b>السعر الحالي:</b> {{ price }}<br>
    <b>التوصية:</b>
    <span class="{{'buy' if signal=='شراء' else 'sell'}}">{{ signal }}</span><br>
    <b>الاستراتيجية:</b> {{ strategy }}<br>
    <form method="post">
        <button class="btn" type="submit">تحديث يدوي</button>
    </form>
    <small>مدة الصفقة: دقيقة واحدة</small>
</div>
</body>
</html>
'''

@app.route("/", methods=["GET", "POST"])
def home():
    return render_template_string(
        HTML,
        market=last_signal["market"],
        time=last_signal["time"],
        price=last_signal["price"],
        signal=last_signal["signal"],
        strategy=last_signal["strategy"]
    )

@app.route("/api")
def api():
    return jsonify(last_signal)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
