import datetime
import streamlit as st
import pandas as pd
from common import load_reflections, save_reflections


st.set_page_config(page_title="上傳反思心得紀錄", layout="wide")
st.title("上傳反思心得紀錄")

# 讀取現有反思紀錄
# 初始化 reflection_records
st.session_state.setdefault("reflection_records", load_reflections())

# ---------------- 反思輸入表單 ----------------
with st.form("reflection_form", clear_on_submit=True):
    # 讓使用者指定反思日期
    refl_date = st.date_input("請選擇反思日期", datetime.date.today())
    # 根據使用者選擇的日期，計算該週的起始與結束日期（以週一為起點）
    week_start = pd.to_datetime(refl_date).to_period("W").start_time.date()
    week_end = week_start + datetime.timedelta(days=6)


    refl_text = st.text_area("請輸入反思內容", help="每週僅有一筆反思紀錄，若已存在將被更新")
    refl_submit = st.form_submit_button("提交反思")

if refl_submit:
    # 將反思資料暫存，這裡以週的起始日期作為該筆紀錄的日期
    st.session_state.pending_reflection = {
        "date": datetime.datetime.combine(week_start, datetime.time(0, 0)),
        "reflection": refl_text
    }
    st.info("反思紀錄已提交，請輸入密碼以確認上傳。")


# ---------------- 密碼確認表單 ----------------

# 從環境變數中取得密碼
UPLOAD_PASSWORD = st.secrets["UPLOAD_PASSWORD"]

# 如果 pending_record 已存在，則顯示密碼表單
if "pending_reflection" in st.session_state:
    with st.form("password_form"):
        password_input = st.text_input("請輸入上傳密碼", type="password", key="upload_password")
        password_submit = st.form_submit_button("確認上傳")
    if password_submit:
        if password_input == UPLOAD_PASSWORD:
            st.success("密碼正確，正在更新反思紀錄...")
            records = load_reflections()
            pending_date = st.session_state.pending_reflection["date"]
            # 以 pending_date 計算該週的起始日期
            pending_week_start = pd.to_datetime(pending_date).to_period("W").start_time.date()
            updated = False
            # 檢查是否已有本週反思紀錄
            for rec in records:
                rec_week_start = pd.to_datetime(rec["date"]).to_period("W").start_time.date()
                if rec_week_start == pending_week_start:
                    rec["reflection"] = st.session_state.pending_reflection["reflection"]
                    updated = True
                    break
            if not updated:
                records.append(st.session_state.pending_reflection)
            if save_reflections(records):
                st.write(records)
                st.success("反思紀錄已更新！")
            else:
                st.error("更新反思紀錄失敗。")
            del st.session_state.pending_reflection
        else:
            st.error("密碼錯誤，請重試。")
    st.stop()
