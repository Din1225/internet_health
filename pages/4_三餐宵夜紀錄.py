import streamlit as st 
import pandas as pd
from datetime import datetime, timedelta
from common import load_records

st.set_page_config(page_title="三餐宵夜紀錄展示", layout="wide")
st.title("三餐宵夜紀錄展示")

# 刷新按鈕：更新 session state 中的 daily_records
if st.button("刷新資料"):
    st.session_state.daily_records = load_records()
    st.success("資料已刷新！")

# 從 session_state 或 CSV 取得最新資料
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
    df["week_start"] = df["date"].dt.to_period("W").apply(lambda r: r.start_time)
    grouped = df.groupby("week_start")

    for week, group in grouped:
        week_end = week + timedelta(days=6)
        st.subheader(f"週：{week.strftime('%Y-%m-%d')} ~ {week_end.strftime('%Y-%m-%d')}")
        # 建立表格標題：日期、早餐、午餐、晚餐、宵夜
        header_cols = st.columns([1, 3, 3, 3, 3])
        header_cols[0].markdown("**日期**")
        header_cols[1].markdown("**早餐**")
        header_cols[2].markdown("**午餐**")
        header_cols[3].markdown("**晚餐**")
        header_cols[4].markdown("**宵夜**")
        
        for _, row in group.sort_values("date").iterrows():
            row_cols = st.columns([1, 3, 3, 3, 3])
            # 日期
            row_cols[0].write(row["date"].strftime("%Y-%m-%d"))
            
            # 早餐：圖片優先，否則描述
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
            
            # 宵夜
            late_night_val = row.get("late_night")
            late_night_desc = row.get("late_night_desc")
            if isinstance(late_night_val, str) and late_night_val.strip():
                row_cols[4].image(late_night_val, use_container_width=True)
            elif isinstance(late_night_desc, str) and late_night_desc.strip():
                row_cols[4].write(late_night_desc)
            else:
                row_cols[4].write("無")
