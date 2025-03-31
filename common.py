import os
import uuid
import datetime
import pandas as pd
from google.cloud import storage
from io import StringIO

# 嘗試從 st.secrets 中讀取憑證內容（僅在 Streamlit Cloud 環境中有效）
try:
    import streamlit as st
    if "GCP_CREDENTIALS" in st.secrets:
        with open("/tmp/credentials.json", "w") as f:
            f.write(st.secrets["GCP_CREDENTIALS"])
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/tmp/credentials.json"
    else:
        print("GCP_CREDENTIALS 不存在於 st.secrets 中。")
except Exception as e:
    print("Error reading st.secrets:", e)


DATA_FILE = "daily_records.csv"
BUCKET_NAME = "internet_health"  # 請替換成你的 Bucket 名稱

client = storage.Client()
bucket = client.bucket(BUCKET_NAME)

def upload_file_to_gcs(uploaded_file, record_date, category):
    """
    將上傳的檔案上傳到 GCS，並以格式：YYYYMMDD_category_UUID.ext 重新命名，
    回傳該檔案的公眾 URL。
    """
    if uploaded_file is not None:
        ext = os.path.splitext(uploaded_file.name)[1]
        new_filename = f"{record_date.strftime('%Y%m%d')}_{category}_{uuid.uuid4().hex}{ext}"
        blob = bucket.blob(new_filename)
        blob.upload_from_file(uploaded_file)
        return blob.public_url
    return ""

def load_records():
    """
    從 Google Cloud Storage 讀取 daily_records.csv，並返回 list of dicts。
    如果檔案不存在，回傳空列表。
    """
    blob = bucket.blob(DATA_FILE)
    if blob.exists():
        try:
            csv_data = blob.download_as_text()
            df = pd.read_csv(StringIO(csv_data), parse_dates=["date"])
            return df.to_dict(orient="records")
        except Exception as e:
            print("Error loading records:", e)
            return []
    else:
        return []

def save_records(records):
    """
    將紀錄 list 儲存為 CSV，然後上傳到 Google Cloud Storage。
    成功則返回 True，否則返回 False。
    """
    try:
        df = pd.DataFrame(records)
        csv_data = df.to_csv(index=False)
        blob = bucket.blob(DATA_FILE)
        blob.upload_from_string(csv_data, content_type="text/csv")
        return True
    except Exception as e:
        print("Error saving records:", e)
        return False

def remove_record_by_date(target_date, records):
    updated_records = []
    for rec in records:
        rec_date = rec["date"].date() if isinstance(rec["date"], datetime.datetime) else pd.to_datetime(rec["date"]).date()
        if rec_date != target_date:
            updated_records.append(rec)
    if save_records(updated_records):
        return updated_records
    else:
        return None

# --------------- 反思紀錄相關函式 ------------------

REFLECTION_FILE = "reflection_records.csv"

def load_reflections():
    """
    從 Google Cloud Storage 讀取 reflection_records.csv，並返回 list of dicts。
    如果檔案不存在，回傳空列表。
    """
    blob = bucket.blob(REFLECTION_FILE)
    if blob.exists():
        try:
            csv_data = blob.download_as_text()
            df = pd.read_csv(StringIO(csv_data), parse_dates=["date"])
            return df.to_dict(orient="records")
        except Exception as e:
            print("Error loading reflections:", e)
            return []
    else:
        return []

def save_reflections(records):
    """
    將反思紀錄 list 儲存為 CSV，然後上傳到 Google Cloud Storage。
    成功則返回 True，否則返回 False。
    """
    try:
        df = pd.DataFrame(records)
        csv_data = df.to_csv(index=False)
        blob = bucket.blob(REFLECTION_FILE)
        blob.upload_from_string(csv_data, content_type="text/csv")
        return True
    except Exception as e:
        print("Error saving reflections:", e)
        return False
