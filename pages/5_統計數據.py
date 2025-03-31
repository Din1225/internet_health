import pandas as pd
import streamlit as st
from st_aggrid import AgGrid
from streamlit_echarts import st_echarts
from common import load_records

st.set_page_config(page_title="統計數據", layout="wide")
st.title("統計數據")

daily_records = load_records()

if daily_records:
    df_show = pd.DataFrame(daily_records)
    df_show["date"] = pd.to_datetime(df_show["date"])
    df_show = df_show.sort_values("date")
    
    df_show["date_display"] = df_show["date"].dt.strftime("%Y-%m-%d")
    
    # 計算平均數值
    avg_sleep = df_show["sleep_hours"].mean()
    avg_steps = df_show["steps"].mean()
    avg_sugary = df_show["sugary_drinks"].mean()
    avg_screen = df_show["screen_time"].mean() if "screen_time" in df_show.columns else 0
    
    st.markdown("### 總平均數據")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("平均睡眠時數", f"{avg_sleep:.1f} 小時")
    col2.metric("平均每日步數", f"{avg_steps:.0f} 步")
    col3.metric("平均每日含糖飲料", f"{avg_sugary:.1f} 杯")
    col4.metric("平均螢幕使用時間", f"{avg_screen:.1f} 小時")
    
    st.subheader("每日紀錄概覽")
    AgGrid(df_show[["date_display", "sleep_hours", "steps", "sugary_drinks", "screen_time"]])
    daily_dates = df_show["date"].dt.strftime("%Y-%m-%d").tolist()
    
    # 每日睡眠時數趨勢圖
    sleep_data = df_show["sleep_hours"].tolist()
    option_sleep = {
        "tooltip": {"trigger": "axis"},
        "xAxis": {"type": "category", "data": daily_dates},
        "yAxis": {"type": "value"},
        "series": [{"data": sleep_data, "type": "line", "name": "睡眠時數"}]
    }
    st.subheader("每日睡眠時數趨勢")
    st_echarts(options=option_sleep, height="400px")
    
    # 每日步數圖
    steps_data = df_show["steps"].tolist()
    option_steps = {
        "tooltip": {"trigger": "axis"},
        "xAxis": {"type": "category", "data": daily_dates},
        "yAxis": {"type": "value"},
        "series": [{"data": steps_data, "type": "bar", "name": "步數"}]
    }
    st.subheader("每日步數")
    st_echarts(options=option_steps, height="400px")
    
    # 每日含糖飲料數量圖
    sugary_data = df_show["sugary_drinks"].tolist()
    option_sugary = {
        "tooltip": {"trigger": "axis"},
        "xAxis": {"type": "category", "data": daily_dates},
        "yAxis": {"type": "value"},
        "series": [{"data": sugary_data, "type": "line", "name": "含糖飲料數量"}]
    }
    st.subheader("每日含糖飲料數量趨勢")
    st_echarts(options=option_sugary, height="400px")
    
    # 每日螢幕使用時間趨勢圖（若有資料）
    if "screen_time" in df_show.columns:
        screen_data = df_show["screen_time"].tolist()
        option_screen = {
            "tooltip": {"trigger": "axis"},
            "xAxis": {"type": "category", "data": daily_dates},
            "yAxis": {"type": "value"},
            "series": [{"data": screen_data, "type": "line", "name": "螢幕使用時間"}]
        }
        st.subheader("每日螢幕使用時間趨勢")
        st_echarts(options=option_screen, height="400px")
    
else:
    st.info("尚未有每日紀錄數據。")
