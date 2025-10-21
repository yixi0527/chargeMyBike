import streamlit as st
import requests
import random
from datetime import datetime
from urllib3.exceptions import InsecureRequestWarning
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed

# 禁用 SSL 警告
warnings.simplefilter('ignore', InsecureRequestWarning)

st.set_page_config(page_title="充电桩剩余时间查询", layout="wide")

# 充电站信息
charge_stations = [
    {"ck": "073515b94200", "name": "7"},
    {"ck": "04021cd51a00", "name": "3"},
    {"ck": "04015f9d0f00", "name": "4"},
    {"ck": "04015c9f1900", "name": "5"},
    {"ck": "04023ad93500", "name": "6"},
    {"ck": "04023ada2100", "name": "8"}
]

# 请求 URL 和 headers
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

# 时间转换函数
def convert_milliseconds_to_hms(milliseconds):
    seconds = milliseconds // 1000
    minutes = seconds // 60
    hours = minutes // 60
    return f"{hours:02}:{minutes % 60:02}:{seconds % 60:02}"

# 随机生成 memberId
def generate_member_id():
    return f"123{random.randint(1000, 9999)}"

# 查询单个站点
def query_station(station, session):
    member_id = generate_member_id()
    payload = {"ck": station["ck"], "memberId": member_id}
    results = []
    try:
        resp = session.post(url, data=payload, timeout=10, verify=False)
        if resp.status_code == 200:
            response_data = resp.json()
            products = response_data.get('products', [])
            for product in products:
                end_time_ms = product.get('endTime')
                if end_time_ms is not None:
                    if end_time_ms == '未知':
                        end_time_ms = 0.0
                    results.append({
                        "station_name": station["name"],
                        "sid": product["sid"],
                        "end_time_ms": int(end_time_ms),
                        "end_time_hms": convert_milliseconds_to_hms(int(end_time_ms)),
                        "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
    except Exception as e:
        st.warning(f"查询 {station['name']} 出错: {e}")
    return results

# 查询所有站点
@st.cache_data(ttl=15)  # 缓存 15 秒，防止频繁请求
def fetch_all_data():
    session = requests.Session()
    session.headers.update(headers)
    all_results = []

    with ThreadPoolExecutor(max_workers=len(charge_stations)) as executor:
        futures = [executor.submit(query_station, station, session) for station in charge_stations]
        for future in as_completed(futures):
            all_results.extend(future.result())

    all_results.sort(key=lambda x: x["end_time_ms"])
    return all_results

st.title("⚡ 充电桩剩余时间查询")

if st.button("刷新数据"):
    data = fetch_all_data()
    st.success(f"已获取 {len(data)} 条数据！")
else:
    data = fetch_all_data()

def highlight_remaining_time(row):
    # 将剩余时间字符串 "HH:MM:SS" 转换为秒数
    h, m, s = map(int, row['剩余时间'].split(':'))
    total_seconds = h * 3600 + m * 60 + s
    
    if total_seconds == 0:
        color = 'lightgreen'
    elif total_seconds <= 2 * 3600:
        color = 'yellow'
    else:
        color = ''
    return [f'background-color: {color}' for _ in row]


# 显示表格
# 显示表格
if data:
    import pandas as pd
    df = pd.DataFrame(data)
    
    # 统计总条数和 end_time_ms 为 0 的条数
    total_count = len(df)
    zero_end_count = (df['end_time_ms'] == 0).sum()
    
    st.markdown(f"**共 {total_count} 条数据，其中空闲有 {zero_end_count} 个**")
    
    df_display = df[["station_name", "sid", "end_time_hms", "current_time"]]
    df_display.columns = ["站号", "口号", "剩余时间", "查询时间"]
    st.dataframe(df_display.style.apply(highlight_remaining_time, axis=1), use_container_width=True)
else:
    st.info("没有获取到数据。")

