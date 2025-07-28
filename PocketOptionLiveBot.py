import websocket
import json
import time

# ===== بياناتك الحقيقية =====
WS_URL = "wss://api-eu.po.market/socket.io/?EIO=4&transport=websocket"

# انسخ كامل سطر الكوكيز من الهيدر هنا (ابدأ من ci_session إلى آخر قيمة)
COOKIES = "ci_session=a%3A4%3A%7Bs%3A10%3A%22session_id%22%3Bs%3A32%3A%22c9ce4ad1f4059df4d39a864e01fd8e00%22%3Bs%3A10%3A%22ip_address%22%3Bs%3A12%3A%22151.255.8.27%22%3Bs%3A10%3A%22user_agent%22%3Bs%3A120%3A%22Mozilla%2F5.0%20%28iPhone%3B%20CPU%20iPhone%20OS%2018_5%20like%20Mac%20OS%20X%29%20AppleWebKit%2F605.1.15%20%28KHTML%2C%20like%20Gecko%29%20Version%2F18.5%20Mobile%2F15E1%22%3Bs%3A13%3A%22last_activity%22%3Bi%3A1753660887%3B%7D5c0bb00fd4b062f0c98b368b8b4ffdfd; lang=en; loggedIn=1; no-login-captcha=1; _gcl_au=1.1.63045385.1753479369.455749598.1753660880.1753660885; ttcsid=1753660869109::TG3uxSwnU0q_zrWB7A7M.14.1753660885700; ttcsid_CPC6SBRC77U2IO5KPOI0=1753660869108::k7yGGhhtXO1zxP3hG8y1.13.1753660885708; _ga_8D1Z2CLK9Z=GS2.1.s1753660868$o12$g1$t1753660879$j49$l0$h0; _fbp=fb.1.1753479369430.673956421940525777; _scid_r=r1zXWEKnrc709hHDvF56Lonhk9iSaMKHd0aHeQ; _tt_enable_cookie=1; _ttp=01K11R7N72JN6YG53JYWRV1PFB_.tt.1; _uetsid=612df600699f11f087e52f514f1697e6; _uetvid=612e3100699f11f0a5f225a12ecda212; afUserId=6f349eb9-051e-4c5a-b986-9abd3e891bba-p; lo_uid=1753479369243-6z3m0k95i56; _ga=GA1.1.631716718.1753479369; zoom-width=[[1%2C1%2C2.1156]]; a=H7rrXy9zejWAmb; ac=kuzonall; af_message=affiliate; cl_id=385044760; code=50START; gclid=Cj0KCQjwnJfEBhCzARIsAIMtfKI01HASeubPDIlgXySL7BzEmFgqWp2nVj9R_wj3ZSLwBkR4KRSYUAsaAhQsEALw_wcB; link_id=1307141; reg_url=utm_campaign%3D792386%26utm_source%3Daffiliate%26utm_medium%3Drevshare%26a%3DH7rrXy9zejWAmb%26ac%3Dkuzonall%26code%3D50START%26gad_source%3D1%26gad_campaignid%3D21844303173%26gbraid%3D0AAAAAqhZgo4AbqtCOXie7KEfaZ6z3ds23%26gclid%3DCj0KCQjwnJfEBhCzARIsAIMtfKI01HASeubPDIlgXySL7BzEmFgqWp2nVj9R_wj3ZSLwBkR4KRSYUAsaAhQsEALw_wcB; t=0; utm_campaign=792386; utm_medium=revshare; utm_source=affiliate; is_pwa=0; _sctr=1%7C1753650000000; _screload=; _scid=qVzXWEKnrc709hHDvF56Lonhk9iSaMKHd0aHcw; AF_SYNC=1753568662568; chat_room=125785264; chat_tab=chats; be_chart-1=collapsed; click_id=1n2nllc2n0j; chat_opened=1; is_pwa=0; referer=https%3A%2F%2Fpayments.exsolution.com%2F; ftw=1; guide=1; _gcl_aw=GCL.1753479383.CjwKCAjw1ozEBhAdEiwAn9qbzVeD1FAkRbJOPu_l1Y9JkjowYBISiHN58LIkYjiINSW6xoI22e5ZXxoCyAYQAvD"

USER_AGENT = "Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Mobile/15E148 Safari/604.1"
REFERER = "https://m.pocketoption.com/en/login"
ORIGIN = "https://m.pocketoption.com"

# ===== استراتيجية سكالبنج دقيقة واحدة =====
prices = []
SIGNAL_LENGTH = 10
last_signal = None

def filter_trend(prices):
    up = sum(1 for i in range(1, len(prices)) if prices[i] > prices[i-1])
    down = sum(1 for i in range(1, len(prices)) if prices[i] < prices[i-1])
    if up >= 8:
        return "UP"
    elif down >= 8:
        return "DOWN"
    else:
        return None

def volatility_filter(prices):
    return max(prices) - min(prices) > 0.0004

def triple_confluence(prices):
    trend = filter_trend(prices)
    strong_move = volatility_filter(prices)
    same_last2 = prices[-1] > prices[-2] if trend == "UP" else prices[-1] < prices[-2]
    return trend, strong_move, same_last2

def on_message(ws, message):
    global last_signal
    try:
        # عدل هذا السطر حسب الرسائل الحقيقية لو عندك مثال
        if 'price' in message:
            try:
                data = json.loads(message)
            except:
                return
            price = float(data.get('price', 0))
            prices.append(price)
            if len(prices) > SIGNAL_LENGTH:
                prices.pop(0)
            if len(prices) >= SIGNAL_LENGTH:
                trend, strong_move, same_last2 = triple_confluence(prices)
                if trend and strong_move and same_last2:
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
    time.sleep(5)
    run_ws()

def on_open(ws):
    print("✅ WebSocket Connection OPEN لايف حقيقي ✅")

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

if __name__ == "__main__":
    run_ws()
    while True:
        time.sleep(10)
