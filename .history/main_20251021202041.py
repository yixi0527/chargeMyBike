import requests
import random
import time
import json
from datetime import datetime

# 充电站数据
charge_stations = [
    {"ck": "073515b94200", "name": "7号站东华大学20号楼停车区（松江校区）"},
    {"ck": "04021cd51a00", "name": "3号站东华大学20号楼停车区（松江校区）"},
    {"ck": "04015f9d0f00", "name": "4号站东华大学20号楼停车区（松江校区）"},
    {"ck": "04015c9f1900", "name": "5号站东华大学20号楼停车区（松江校区）"},
    {"ck": "04023ad93500", "name": "6号站东华大学20号楼停车区（松江校区）"},
    {"ck": "04023ada2100", "name": "8号站东华大学20号楼停车区（松江校区）"}
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
    return f"123{random.randint(1000000, 9999999)}"

# 存储查询结果
def save_result_to_file(data):
    filename = "charge_station_data.json"
    try:
        with open(filename, "r") as f:
            results = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        results = []

    results.append(data)

    with open(filename, "w") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

# 请求并解析每个站点
def query_station(station, session):
    member_id = generate_member_id()
    payload = {
        "ck": station["ck"],
        "memberId": member_id
    }

    try:
        resp = session.post(url, data=payload, timeout=10, verify=False)
        print(f"Request to {station['name']} succeeded with status code: {resp.status_code}")

        if resp.status_code == 200:
            ctype = resp.headers.get("Content-Type", "")
            if "application/json" in ctype:
                try:
                    response_data = resp.json()
                    products = response_data.get('products', [])
                    
                    for product in products:
                        end_time_ms = product.get('endTime')
                        if end_time_ms != '未知' and end_time_ms is not None:
                            end_time_hms = convert_milliseconds_to_hms(int(end_time_ms))
                            data = {
                                "station_name": station["name"],
                                "sid": product["sid"],
                                "end_time": end_time_hms,
                                "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }
                            save_result_to_file(data)
                except ValueError:
                    print(f"Failed to parse JSON for station: {station['name']}")
            else:
                print(f"Non-JSON response for station: {station['name']}")
    except requests.exceptions.RequestException as e:
        print(f"Request failed for station {station['name']}: {e}")

# 主程序
def main():
    # 使用 Session 对象以复用连接
    session = requests.Session()
    session.headers.update(headers)

    while True:
        start_time = time.time()

        # 执行所有站点查询
        for station in charge_stations:
            query_station(station, session)
            # 微小时间间隔，避免被识别为恶意请求
            time.sleep(random.uniform(0.5, 1.0))  # 0.5到1秒之间的随机等待

        # 每15秒后再进行下一轮查询
        elapsed_time = time.time() - start_time
        wait_time = max(0, 15 - elapsed_time)  # 确保每次查询间隔大约为15秒
        print(f"Waiting for {wait_time:.2f} seconds before next round of queries...")
        time.sleep(wait_time)

if __name__ == "__main__":
    main()
