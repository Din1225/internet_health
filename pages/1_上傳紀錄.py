import datetime
import streamlit as st
import requests
import base64
from common import upload_file_to_gcs, load_records, save_records, remove_record_by_date

st.set_page_config(page_title="上傳紀錄", layout="wide")

# 背景圖片設定
def get_base64_from_url(url):
    response = requests.get(url)   
    if response.status_code == 200:
        return base64.b64encode(response.content).decode()
    else:
        return None

bg_url = "https://storage.googleapis.com/internet_health/upload_bg3.jpg"
bg_image_base64 = get_base64_from_url(bg_url)
if bg_image_base64:
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: url("data:image/jpg;base64,{bg_image_base64}") no-repeat center center fixed;
            background-size: cover;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
else:
    st.error("背景圖片載入失敗。")

st.title("上傳紀錄")

# 初始化 daily_records
st.session_state.setdefault("daily_records", load_records())

# 先建立表單提交新紀錄，將資料暫存於 pending_record
with st.form("daily_form", clear_on_submit=True):
    record_date = st.date_input("紀錄日期", datetime.date.today())
    
    st.markdown("#### 上床時間")
    col1, col2, col3, col4 = st.columns([1, 0.3, 1, 0.3])
    bed_hour = col1.number_input("時", min_value=0, max_value=23, value=23, step=1, format="%d")
    bed_minute = col3.number_input("分", min_value=0, max_value=59, value=0, step=1, format="%d")
    bed_time = datetime.time(bed_hour, bed_minute)
    
    st.markdown("#### 起床時間")
    col5, col6, col7, col8 = st.columns([1, 0.3, 1, 0.3])
    wake_hour = col5.number_input("時", min_value=0, max_value=23, value=7, step=1, format="%d", key="wake_hour")
    wake_minute = col7.number_input("分", min_value=0, max_value=59, value=0, step=1, format="%d", key="wake_minute")
    wake_time = datetime.time(wake_hour, wake_minute)
    
    st.markdown("#### 螢幕使用")
    col_screen1, col_screen2 = st.columns([2, 3])
    screen_time = col_screen1.number_input("螢幕使用時間（小時）", min_value=0.0, step=0.1, value=0.0, format="%.1f", help="請輸入今日螢幕使用總時數")
    screen_evidence = col_screen2.file_uploader("上傳螢幕使用證明照片", type=["png", "jpg", "jpeg"], key="screen_evidence")
    
    record_datetime = datetime.datetime.combine(record_date, datetime.time(0, 0))
    
    # 計算睡眠時數
    bed_datetime = datetime.datetime.combine(record_date, bed_time)
    wake_datetime = datetime.datetime.combine(record_date, wake_time)
    if wake_datetime <= bed_datetime:
        wake_datetime += datetime.timedelta(days=1)
    sleep_hours = round((wake_datetime - bed_datetime).total_seconds() / 3600.0, 1)
    st.write(f"計算得的睡眠時數：{sleep_hours:.1f} 小時")
    
    sleep_evidence = st.file_uploader("上傳睡眠證明照片", type=["png", "jpg", "jpeg"], key="sleep_evidence")
    
    st.write("請上傳餐點照片與輸入食物描述：")
    # 早餐
    breakfast_desc = st.text_input("早餐食物描述", key="breakfast_desc")
    breakfast_img = st.file_uploader("早餐照片", type=["png", "jpg", "jpeg"], key="breakfast")
    
    # 午餐
    lunch_desc = st.text_input("午餐食物描述", key="lunch_desc")
    lunch_img = st.file_uploader("午餐照片", type=["png", "jpg", "jpeg"], key="lunch")
    
    # 晚餐
    dinner_desc = st.text_input("晚餐食物描述", key="dinner_desc")
    dinner_img = st.file_uploader("晚餐照片", type=["png", "jpg", "jpeg"], key="dinner")
    
    # 新增：宵夜
    late_night_desc = st.text_input("宵夜食物描述", key="late_night_desc")
    late_night_img = st.file_uploader("宵夜照片", type=["png", "jpg", "jpeg"], key="late_night")
    
    sugary_drinks = st.number_input("當天含糖飲料數量", min_value=0, step=1, value=0, help="請輸入當天喝的含糖飲料數量")
    steps = st.number_input("今日步數", min_value=0, step=100, value=0)
    steps_evidence = st.file_uploader("上傳步數證明照片", type=["png", "jpg", "jpeg"], key="steps_evidence")
    
    submit_daily = st.form_submit_button("提交每日紀錄")

if submit_daily:
    new_record = {
        "date": record_datetime,
        "sleep_hours": sleep_hours,
        "sleep_evidence": upload_file_to_gcs(sleep_evidence, record_date, "sleep"),
        "breakfast": upload_file_to_gcs(breakfast_img, record_date, "breakfast"),
        "breakfast_desc": breakfast_desc,
        "lunch": upload_file_to_gcs(lunch_img, record_date, "lunch"),
        "lunch_desc": lunch_desc,
        "dinner": upload_file_to_gcs(dinner_img, record_date, "dinner"),
        "dinner_desc": dinner_desc,
        "late_night": upload_file_to_gcs(late_night_img, record_date, "late_night"),
        "late_night_desc": late_night_desc,
        "sugary_drinks": sugary_drinks,
        "steps": steps,
        "steps_evidence": upload_file_to_gcs(steps_evidence, record_date, "steps"),
        "screen_time": screen_time,
        "screen_evidence": upload_file_to_gcs(screen_evidence, record_date, "screen")
    }
    st.session_state.pending_record = new_record
    st.info("請輸入上傳密碼以確認上傳資料。")
    
    with st.form("password_form"):
        password_input = st.text_input("請輸入上傳密碼", type="password", key="upload_password")
        password_submit = st.form_submit_button("確認上傳")
    # 用 st.write 除錯，檢查表單是否提交
    st.write("password_submit:", password_submit, "password_input:", password_input)
    if password_submit:
        if password_input == st.secrets["UPLOAD_PASSWORD"]:
            st.success("密碼正確")
            record_date_val = st.session_state.pending_record["date"].date()
            duplicate_index = None
            for i, rec in enumerate(st.session_state.daily_records):
                if rec["date"].date() == record_date_val:
                    duplicate_index = i
                    break
            if duplicate_index is not None:
                st.warning("該日期已有紀錄。將覆蓋舊紀錄。")
                updated_records = remove_record_by_date(record_date_val, st.session_state.daily_records)
                if updated_records is not None:
                    st.session_state.daily_records = updated_records
                    st.session_state.daily_records.append(st.session_state.pending_record)
                    if save_records(st.session_state.daily_records):
                        st.success("現有紀錄已被覆蓋！")
                    else:
                        st.error("儲存資料失敗。")
                else:
                    st.error("移除舊紀錄失敗。")
            else:
                st.session_state.daily_records.append(st.session_state.pending_record)
                if save_records(st.session_state.daily_records):
                    st.success("每日紀錄已提交，且圖片已上傳至 GCS！")
                else:
                    st.error("儲存資料失敗。")
            del st.session_state.pending_record
        else:
            st.error("密碼錯誤，請重試。")
    st.stop()
