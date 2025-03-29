import os
import uuid
import datetime
import pandas as pd
import streamlit as st
from google.cloud import storage
from st_aggrid import AgGrid
from streamlit_echarts import st_echarts

# ---------------------- Google Cloud Storage 設定 ----------------------
# 設定 Google Cloud Storage 的憑證路徑
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./plasma-ember-455214-u6-bb5d400b1bf5.json"




# ---------------------- 基本設定 ----------------------
st.set_page_config(page_title="健康與生活紀錄", layout="wide")

# 設定 CSV 資料檔案名稱
DATA_FILE = "daily_records.csv"

# 設定 Google Cloud Storage
# 請確保環境變數 GOOGLE_APPLICATION_CREDENTIALS 已設定指向憑證 JSON
BUCKET_NAME = "internet_health"  # 請替換成你的 Bucket 名稱
client = storage.Client()
bucket = client.bucket(BUCKET_NAME)
print("Buckets:", bucket)

# ---------------------- 共用函式 ----------------------
def upload_file_to_gcs(uploaded_file, record_date, category):
    """
    將上傳的檔案上傳到 GCS，並以格式：YYYYMMDD_category_UUID.ext 重新命名，
    回傳該檔案的公眾 URL。
    """
    if uploaded_file is not None:
        ext = os.path.splitext(uploaded_file.name)[1]  # 取得副檔名（含 .）
        new_filename = f"{record_date.strftime('%Y%m%d')}_{category}_{uuid.uuid4().hex}{ext}"
        blob = bucket.blob(new_filename)
        blob.upload_from_file(uploaded_file)
        # 使檔案變為公眾可讀（依需求設定權限）
        blob.make_public()
        return blob.public_url
    return ""

# ---------------------- 資料持久化 ----------------------
# 若存在 CSV 檔案則讀取之，否則初始化空的每日紀錄列表
if 'daily_records' not in st.session_state:
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE, parse_dates=["date"])
            st.session_state.daily_records = df.to_dict(orient="records")
        except Exception as e:
            st.error(f"讀取資料檔案時發生錯誤：{e}")
            st.session_state.daily_records = []
    else:
        st.session_state.daily_records = []

# ---------------------- 每日紀錄表單 ----------------------
st.header("每日紀錄")
with st.form("daily_form", clear_on_submit=True):
    record_date = st.date_input("紀錄日期", datetime.date.today())
    sleep_hours = st.number_input("今日睡眠時數", min_value=0.0, step=0.5, value=8.0, help="請輸入今日睡眠總時數")
    sleep_evidence = st.file_uploader("上傳睡眠證明照片", type=["png", "jpg", "jpeg"], key="sleep_evidence")
    
    st.write("請上傳餐點照片：")
    breakfast = st.file_uploader("早餐照片", type=["png", "jpg", "jpeg"], key="breakfast")
    lunch = st.file_uploader("午餐照片", type=["png", "jpg", "jpeg"], key="lunch")
    dinner = st.file_uploader("晚餐照片", type=["png", "jpg", "jpeg"], key="dinner")
    
    sugary_drinks = st.number_input("當天含糖飲料數量", min_value=0, step=1, value=0, help="請輸入當天喝的含糖飲料數量")
    steps = st.number_input("今日步數", min_value=0, step=100, value=0)
    steps_evidence = st.file_uploader("上傳步數證明照片", type=["png", "jpg", "jpeg"], key="steps_evidence")
    reflection = st.text_area("每日反思", help="請記錄今天的心情、心得或學到的事")
    
    submit_daily = st.form_submit_button("提交每日紀錄")

if submit_daily:
    # 依類別上傳圖片到 GCS，並取得公眾 URL
    sleep_evidence_url = upload_file_to_gcs(sleep_evidence, record_date, "sleep")
    breakfast_url = upload_file_to_gcs(breakfast, record_date, "breakfast")
    lunch_url = upload_file_to_gcs(lunch, record_date, "lunch")
    dinner_url = upload_file_to_gcs(dinner, record_date, "dinner")
    steps_evidence_url = upload_file_to_gcs(steps_evidence, record_date, "steps")
    
    new_record = {
        "date": record_date,
        "sleep_hours": sleep_hours,
        "sleep_evidence": sleep_evidence_url,
        "breakfast": breakfast_url,
        "lunch": lunch_url,
        "dinner": dinner_url,
        "sugary_drinks": sugary_drinks,
        "steps": steps,
        "steps_evidence": steps_evidence_url,
        "reflection": reflection
    }
    st.session_state.daily_records.append(new_record)
    
    try:
        df = pd.DataFrame(st.session_state.daily_records)
        df.to_csv(DATA_FILE, index=False)
        st.success("每日紀錄已提交，且圖片已上傳至 GCS！")
    except Exception as e:
        st.error(f"儲存資料失敗：{e}")

# ---------------------- 每日紀錄展示 ----------------------
st.markdown("---")
st.header("目前紀錄")
if st.session_state.daily_records:
    df_show = pd.DataFrame(st.session_state.daily_records)
    df_show["date"] = pd.to_datetime(df_show["date"])
    df_show = df_show.sort_values("date")
    # 以 AgGrid 呈現部分欄位
    AgGrid(df_show[["date", "sleep_hours", "steps", "sugary_drinks"]])
else:
    st.info("尚未有每日紀錄。")

# ---------------------- 互動圖表 ----------------------
if st.session_state.daily_records:
    df_chart = pd.DataFrame(st.session_state.daily_records)
    df_chart["date"] = pd.to_datetime(df_chart["date"])
    df_chart = df_chart.sort_values("date")
    
    # 每日睡眠時數趨勢圖 (ECharts)
    daily_dates = df_chart["date"].dt.strftime("%Y-%m-%d").tolist()
    sleep_data = df_chart["sleep_hours"].tolist()
    option_sleep = {
        "tooltip": {"trigger": "axis"},
        "xAxis": {"type": "category", "data": daily_dates},
        "yAxis": {"type": "value"},
        "series": [{"data": sleep_data, "type": "line", "name": "睡眠時數"}]
    }
    st.subheader("每日睡眠時數趨勢")
    st_echarts(options=option_sleep, height="400px")
    
    # 每日步數圖 (ECharts)
    steps_data = df_chart["steps"].tolist()
    option_steps = {
        "tooltip": {"trigger": "axis"},
        "xAxis": {"type": "category", "data": daily_dates},
        "yAxis": {"type": "value"},
        "series": [{"data": steps_data, "type": "bar", "name": "步數"}]
    }
    st.subheader("每日步數")
    st_echarts(options=option_steps, height="400px")
    
    # 每週彙總統計：累計睡眠、步數與含糖飲料數量
    df_chart["week_start"] = df_chart["date"].dt.to_period('W').apply(lambda r: r.start_time)
    weekly_summary = df_chart.groupby("week_start").agg({
        "sleep_hours": "sum",
        "steps": "sum",
        "sugary_drinks": "sum"
    }).reset_index()
    
    st.markdown("### 每週彙總統計")
    AgGrid(weekly_summary)
    
    weekly_dates = [d.strftime("%Y-%m-%d") for d in weekly_summary["week_start"]]
    weekly_sleep = weekly_summary["sleep_hours"].tolist()
    option_weekly_sleep = {
        "tooltip": {"trigger": "axis"},
        "xAxis": {"type": "category", "data": weekly_dates},
        "yAxis": {"type": "value"},
        "series": [{"data": weekly_sleep, "type": "line", "name": "累計睡眠時數"}]
    }
    st.subheader("每週累計睡眠時數")
    st_echarts(options=option_weekly_sleep, height="400px")
    
    weekly_steps = weekly_summary["steps"].tolist()
    option_weekly_steps = {
        "tooltip": {"trigger": "axis"},
        "xAxis": {"type": "category", "data": weekly_dates},
        "yAxis": {"type": "value"},
        "series": [{"data": weekly_steps, "type": "line", "name": "累計步數"}]
    }
    st.subheader("每週累計步數")
    st_echarts(options=option_weekly_steps, height="400px")
    
    weekly_sugary = weekly_summary["sugary_drinks"].tolist()
    option_weekly_sugary = {
        "tooltip": {"trigger": "axis"},
        "xAxis": {"type": "category", "data": weekly_dates},
        "yAxis": {"type": "value"},
        "series": [{"data": weekly_sugary, "type": "line", "name": "累計含糖飲料數量"}]
    }
    st.subheader("每週累計含糖飲料數量")
    st_echarts(options=option_weekly_sugary, height="400px")
else:
    st.info("尚未有每日紀錄數據。")
