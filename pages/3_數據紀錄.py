import streamlit as st 
import pandas as pd
from datetime import datetime, timedelta
from common import load_records

st.set_page_config(page_title="數據紀錄", layout="wide")
st.title("數據紀錄")

# 刷新按鈕：更新 session state 中的 daily_records
if st.button("刷新資料"):
    st.session_state.daily_records = load_records()
    st.success("資料已刷新！")

# 從 session state 或 CSV 取得最新資料
if 'daily_records' in st.session_state:
    records = st.session_state.daily_records
else:
    records = load_records()

if not records:
    st.info("尚未有紀錄。")
else:
    df = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")
    
    # 以週為單位計算週起始日期
    df["week_start"] = df["date"].dt.to_period('W').apply(lambda r: r.start_time)
    
    grouped = df.groupby("week_start")
    
    for week, group in grouped:
        week_end = week + timedelta(days=6)
        st.subheader(f"週：{week.strftime('%Y-%m-%d')} ~ {week_end.strftime('%Y-%m-%d')}")
        
        # 建立表格標題，共 5 欄：日期、螢幕使用時間、睡眠時數、含糖飲料、步數
        header_cols = st.columns([1, 2, 2, 2, 2])
        header_cols[0].markdown("**日期**")
        header_cols[1].markdown("**螢幕使用時間**")
        header_cols[2].markdown("**睡眠時數**")
        header_cols[3].markdown("**含糖飲料**")
        header_cols[4].markdown("**步數**")
        
        for _, row in group.sort_values("date").iterrows():
            row_cols = st.columns([1, 2, 2, 2, 2])
            row_cols[0].write(row["date"].strftime("%Y-%m-%d"))
            
            # 螢幕使用時間
            screen_time = row.get("screen_time")
            if screen_time is not None and str(screen_time).strip() != "":
                row_cols[1].write(f"{screen_time:.1f}")
            else:
                row_cols[1].write("無")
            
            # 睡眠時數
            row_cols[2].write(row.get("sleep_hours", ""))
            # 含糖飲料數量
            row_cols[3].write(row.get("sugary_drinks", ""))
            # 步數
            row_cols[4].write(row.get("steps", ""))
        
        # 顯示該週平均數值
        avg_screen = group["screen_time"].mean() if "screen_time" in group.columns else 0
        avg_sleep = group["sleep_hours"].mean()
        avg_sugary = group["sugary_drinks"].mean()
        avg_steps = group["steps"].mean()
        
        st.markdown("---")
        avg_cols = st.columns([1, 2, 2, 2, 2])
        avg_cols[0].write("平均")
        avg_cols[1].write(f"{avg_screen:.1f}")
        avg_cols[2].write(f"{avg_sleep:.1f}")
        avg_cols[3].write(f"{avg_sugary:.1f}")
        avg_cols[4].write(f"{avg_steps:.0f}")
        st.markdown("---")
