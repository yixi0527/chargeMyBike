import requests

url = "https://wx.jwnzn.com/mini_jwnzn/miniapp/mp_parseCk.action"

headers = {
    "Host": "wx.jwnzn.com",
    "Connection": "keep-alive",
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept-Encoding": "gzip,compress,br,deflate",
    "User-Agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) "
        "Mobile/15E148 MicroMessenger/8.0.64(0x1800402b) NetType/WIFI Language/zh_CN"
    ),
    "Referer": "https://servicewechat.com/wxbca9e5fdb915c13d/98/page-frame.html",
}

# 你给出的请求体
payload = {
    "ck": "04021cd51a00",
    "memberId": "1227584"
}

# 使用 Session 可以复用连接并更容易管理 cookies、重试等
session = requests.Session()
session.headers.update(headers)

try:
    resp = session.post(url, data=payload, timeout=10)  # timeout 可调
    print("Status code:", resp.status_code)
    ctype = resp.headers.get("Content-Type", "")
    if "application/json" in ctype:
        try:
            print("Response JSON:", resp.json())
        except ValueError:
            print("Response text (invalid JSON):", resp.text)
    else:
        print("Response text:", resp.text)
except requests.exceptions.RequestException as e:
    print("Request failed:", e)
