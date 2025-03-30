import os
import uuid
import datetime
import pandas as pd
from google.cloud import storage

# 如果環境變數尚未設定，則嘗試從 st.secrets 中取得 GCP 憑證內容
# 注意：這需要在 Streamlit 運行環境中，因為 st.secrets 只在 Streamlit Cloud 或本地 streamlit 執行時可用
try:
    import streamlit as st
    if "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
        if "GCP_CREDENTIALS" in st.secrets:
            # 將憑證內容寫入 /tmp/credentials.json
            with open("/tmp/credentials.json", "w") as f:
                f.write(st.secrets["GCP_CREDENTIALS"])
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/tmp/credentials.json"
except Exception as e:
    # 若非 Streamlit 環境或無法讀取 st.secrets，則保持原有設定
    pass

# 設定資料檔案名稱與 Bucket 名稱
DATA_FILE = "daily_records.csv"
BUCKET_NAME = "internet_health"  # 請替換成你的 Bucket 名稱

client = storage.Client()
bucket = client.bucket(BUCKET_NAME)

def upload_file_to_gcs(uploaded_file, record_date, category):
    """
    將上傳的檔案上傳到 GCS，並以格式：YYYYMMDD_category_UUID.ext 重新命名，
    回傳該檔案的公眾 URL。
    
    注意：
      因為 Bucket 啟用了 Uniform Bucket-level Access，
      無法使用 blob.make_public()，
      請確保你的 Bucket IAM 已設定允許 allUsers 以 Storage Object Viewer 角色存取物件。
    """
    if uploaded_file is not None:
        ext = os.path.splitext(uploaded_file.name)[1]  # 取得副檔名（含 .）
        new_filename = f"{record_date.strftime('%Y%m%d')}_{category}_{uuid.uuid4().hex}{ext}"
        blob = bucket.blob(new_filename)
        blob.upload_from_file(uploaded_file)
        return blob.public_url
    return ""

def load_records():
    """從 CSV 檔案讀取每日紀錄，返回 list of dicts。"""
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE, parse_dates=["date"])
            return df.to_dict(orient="records")
        except Exception as e:
            print("Error loading records:", e)
            return []
    return []

def save_records(records):
    """將紀錄 list 儲存到 CSV 檔案。成功則返回 True，否則返回 False。"""
    try:
        df = pd.DataFrame(records)
        df.to_csv(DATA_FILE, index=False)
        return True
    except Exception as e:
        print("Error saving records:", e)
        return False

def remove_record_by_date(target_date, records):
    """
    根據 target_date (datetime.date) 從紀錄列表中移除所有日期相同的紀錄，
    然後寫入 CSV。成功則返回更新後的紀錄列表，否則返回 None。

    參數:
      target_date: datetime.date 物件，目標日期
      records: 紀錄列表，假設每筆紀錄的 "date" 為 datetime 物件

    回傳:
      更新後的紀錄列表（如果儲存成功），否則返回 None
    """
    updated_records = []
    for rec in records:
        # 確保 rec["date"] 為 datetime 物件
        rec_date = rec["date"].date() if isinstance(rec["date"], datetime.datetime) else pd.to_datetime(rec["date"]).date()
        if rec_date != target_date:
            updated_records.append(rec)
    if save_records(updated_records):
        return updated_records
    else:
        return None
