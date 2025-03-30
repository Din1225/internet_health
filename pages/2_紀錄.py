import streamlit as st 
import pandas as pd
from datetime import datetime, timedelta
from common import load_records
import requests
import base64

st.set_page_config(page_title="紀錄展示", layout="wide")

st.title("紀錄展示")

# 刷新按鈕：更新 session state 中的 daily_records
if st.button("刷新資料"):
    st.session_state.daily_records = load_records()
    st.success("資料已刷新！")

# 從 session state 中取得最新資料，如果沒有則直接從 CSV 載入
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
    
    df["week_start"] = df["date"].dt.to_period('W').apply(lambda r: r.start_time)
    

    grouped = df.groupby("week_start")
    
    for week, group in grouped:
        week_end = week + pd.Timedelta(days=6)
        st.subheader(f"週：{week.strftime('%Y-%m-%d')} ~ {week_end.strftime('%Y-%m-%d')}")
        # 日期、早餐、午餐、晚餐、螢幕使用時間、睡眠時數、含糖飲料、步數、反思
        header_cols = st.columns([1, 3, 3, 3, 2, 2, 2, 2, 4])
        header_cols[0].markdown("**日期**")
        header_cols[1].markdown("**早餐**")
        header_cols[2].markdown("**午餐**")
        header_cols[3].markdown("**晚餐**")
        header_cols[4].markdown("**螢幕使用時間**")
        header_cols[5].markdown("**睡眠時數**")
        header_cols[6].markdown("**含糖飲料**")
        header_cols[7].markdown("**步數**")
        header_cols[8].markdown("**反思**")
        
        # 依日期排序後迭代每一筆紀錄
        for _, row in group.sort_values("date").iterrows():
            row_cols = st.columns([1, 3, 3, 3, 2, 2, 2, 2, 4])
            # 日期
            row_cols[0].write(row["date"].strftime("%Y-%m-%d"))
            
            # 早餐
            breakfast_val = row.get("breakfast")
            breakfast_desc = row.get("breakfast_desc")
            if isinstance(breakfast_val, str) and breakfast_val.strip():
                row_cols[1].image(breakfast_val, use_container_width=True)
            elif isinstance(breakfast_desc, str) and breakfast_desc.strip():
                row_cols[1].write(breakfast_desc)
            else:
                row_cols[1].write("無")
            
            # 午餐
            lunch_val = row.get("lunch")
            lunch_desc = row.get("lunch_desc")
            if isinstance(lunch_val, str) and lunch_val.strip():
                row_cols[2].image(lunch_val, use_container_width=True)
            elif isinstance(lunch_desc, str) and lunch_desc.strip():
                row_cols[2].write(lunch_desc)
            else:
                row_cols[2].write("無")
            
            # 晚餐
            dinner_val = row.get("dinner")
            dinner_desc = row.get("dinner_desc")
            if isinstance(dinner_val, str) and dinner_val.strip():
                row_cols[3].image(dinner_val, use_container_width=True)
            elif isinstance(dinner_desc, str) and dinner_desc.strip():
                row_cols[3].write(dinner_desc)
            else:
                row_cols[3].write("無")
            
            # 螢幕使用時間
            screen_time = row.get("screen_time")
            if screen_time is not None and str(screen_time).strip() != "":
                row_cols[4].write(f"{screen_time:.1f}")
            else:
                row_cols[4].write("無")
            
            # 睡眠時數
            row_cols[5].write(row.get("sleep_hours", ""))
            # 含糖飲料數量
            row_cols[6].write(row.get("sugary_drinks", ""))
            # 步數
            row_cols[7].write(row.get("steps", ""))
            # 反思內容
            reflection = row.get("reflection", "")
            row_cols[8].write(reflection if reflection and str(reflection).strip() else "無")
        
        # 顯示該週平均數值（不包含反思）
        avg_screen = group["screen_time"].mean() if "screen_time" in group.columns else 0
        avg_sleep = group["sleep_hours"].mean()
        avg_sugary = group["sugary_drinks"].mean()
        avg_steps = group["steps"].mean()
        
        st.markdown("---")
        avg_cols = st.columns([1, 3, 3, 3, 2, 2, 2, 2, 4])
        avg_cols[0].write("平均")
        avg_cols[1].write("-")
        avg_cols[2].write("-")
        avg_cols[3].write("-")
        avg_cols[4].write(f"{avg_screen:.1f}")
        avg_cols[5].write(f"{avg_sleep:.1f}")
        avg_cols[6].write(f"{avg_sugary:.1f}")
        avg_cols[7].write(f"{avg_steps:.0f}")
        avg_cols[8].write("-")
        st.markdown("---")
