import streamlit as st
import requests
import base64

st.set_page_config(page_title="網路使用與健康促進紀錄", layout="wide")

def get_base64_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        return base64.b64encode(response.content).decode()
    else:
        return None

# 替換為你在 GCS 上的公開圖片 URL
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

# 調整 margin-top 到 150px 讓標題往下移
st.markdown(
    """
    <div style="display: flex; justify-content: center; margin-top: 300px;">
        <h1 style="
            color: #F8F8F8; 
            font-family: 'Helvetica', sans-serif; 
            font-size: 48px; 
            font-weight: 700;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
            background-color: rgba(0, 0, 0, 0.6);
            padding: 10px 20px;
            border-radius: 8px;
        ">
            網路使用與健康促進紀錄
        </h1>
    </div>
    """,
    unsafe_allow_html=True
)
