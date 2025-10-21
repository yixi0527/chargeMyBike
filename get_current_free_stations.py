import requests
import random
import json
from datetime import datetime
from urllib3.exceptions import InsecureRequestWarning
import warnings

# 禁用 SSL 警告
warnings.simplefilter('ignore', InsecureRequestWarning)

# 充电站数据
charge_stations = [
    {"ck": "073515b94200", "name": "7-"},
    {"ck": "04021cd51a00", "name": "3-"},
    {"ck": "04015f9d0f00", "name": "4-"},
    {"ck": "04015c9f1900", "name": "5-"},
    {"ck": "04023ad93500", "name": "6-"},
    {"ck": "04023ada2100", "name": "8-"}
]

# 请求URL
url = "https://wx.jwnzn.com/mini_jwnzn/miniapp/mp_parseCk.action"

# 请求头
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

# 时间转换函数
def convert_milliseconds_to_hms(milliseconds):
    seconds = milliseconds // 1000
    minutes = seconds // 60
    hours = minutes // 60
    return f"{hours:02}:{minutes % 60:02}:{seconds % 60:02}"

# 随机生成memberId
def generate_member_id():
    return f"123{random.randint(1000, 9999)}"

# 查询单个站点
def query_station(station, session):
    member_id = generate_member_id()
    payload = {"ck": station["ck"], "memberId": member_id}

    try:
        resp = session.post(url, data=payload, timeout=10, verify=False)
        if resp.status_code == 200:
            response_data = resp.json()
            products = response_data.get('products', [])
            results = []
            for product in products:
                end_time_ms = product.get('endTime')
                if end_time_ms not in (None, '未知'):
                    results.append({
                        "station_name": station["name"],
                        "sid": product["sid"],
                        "end_time_ms": int(end_time_ms),
                        "end_time_hms": convert_milliseconds_to_hms(int(end_time_ms)),
                        "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
            return results
    except Exception as e:
        print(f"Error querying station {station['name']}: {e}")
    return []

# 主程序
def main():
    session = requests.Session()
    session.headers.update(headers)

    all_results = []
    for station in charge_stations:
        data = query_station(station, session)
        if data:
            all_results.extend(data)

    # 按剩余时间排序
    all_results.sort(key=lambda x: x["end_time_ms"])

    # 输出结果
    print("充电桩剩余时间列表（按剩余时间排序）：")
    for item in all_results:
        print(f"{item['station_name']}{item['sid']}\t{item['end_time_hms']}")

    # 保存到文件
    with open("all_charge_data_sorted.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()
