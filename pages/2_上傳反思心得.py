import datetime
import streamlit as st
import pandas as pd
from common import load_reflections, save_reflections

st.set_page_config(page_title="反思紀錄", layout="wide")
st.title("反思紀錄 (新增/更新)")


# 取得今天的日期，並計算本週的起始與結束日期
today = datetime.date.today()
current_week_start = pd.to_datetime(today).to_period("W").start_time.date()
current_week_end = current_week_start + datetime.timedelta(days=6)

# 讀取現有反思紀錄
existing_reflections = load_reflections()

# 檢查本週是否已有反思紀錄，若有則預填反思內容
existing_reflection_text = ""
for rec in existing_reflections:
    rec_week_start = pd.to_datetime(rec["date"]).to_period("W").start_time.date()
    if rec_week_start == current_week_start:
        existing_reflection_text = rec.get("reflection", "")
        break

# ---------------- 反思輸入表單 ----------------
with st.form("reflection_form", clear_on_submit=True):
    st.markdown(f"**本週反思紀錄：{current_week_start} ~ {current_week_end}**")
    # 預設反思內容為本週已有的內容（若有）
    refl_text = st.text_area("請輸入反思內容", value=existing_reflection_text, help="本週僅有一筆反思紀錄，若已存在將被更新")
    refl_submit = st.form_submit_button("提交反思")
if refl_submit:
    st.session_state.pending_reflection = {
        "date": datetime.datetime.combine(current_week_start, datetime.time(0, 0)),
        "reflection": refl_text
    }
    st.info("反思紀錄已提交，請輸入密碼以確認上傳。")
    st.experimental_rerun()

# ---------------- 密碼確認表單 ----------------
if "pending_reflection" in st.session_state:
    with st.form("password_form"):
        password_input = st.text_input("請輸入上傳密碼", type="password", key="upload_password")
        password_submit = st.form_submit_button("確認上傳")
    if password_submit:
        correct_password = st.secrets["UPLOAD_PASSWORD"]
        if password_input == correct_password:
            st.success("密碼正確，正在更新反思紀錄...")
            # 讀取最新反思紀錄（若有）
            records = load_reflections()
            pending_date = st.session_state.pending_reflection["date"]
            week_start = pd.to_datetime(pending_date).to_period("W").start_time.date()
            updated = False
            # 檢查是否已有本週反思紀錄
            for rec in records:
                rec_week_start = pd.to_datetime(rec["date"]).to_period("W").start_time.date()
                if rec_week_start == week_start:
                    rec["reflection"] = st.session_state.pending_reflection["reflection"]
                    updated = True
                    break
            if not updated:
                records.append(st.session_state.pending_reflection)
            if save_reflections(records):
                st.success("反思紀錄已更新！")
            else:
                st.error("更新反思紀錄失敗。")
            del st.session_state.pending_reflection
        else:
            st.error("密碼錯誤，請重試。")
    st.stop()
