import os
import uuid
import datetime
import pandas as pd
from google.cloud import storage

# 從st.secrets讀取憑證
try:
    import streamlit as st
    if "GCP_CREDENTIALS" in st.secrets:
        print("成功讀取 st.secrets 中的 GCP_CREDENTIALS")
        with open("/tmp/credentials.json", "w") as f:
            f.write(st.secrets["GCP_CREDENTIALS"])
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/tmp/credentials.json"
    else:
        print("GCP_CREDENTIALS 不存在於 st.secrets 中。")
except Exception as e:
    print("Error reading st.secrets:", e)


DATA_FILE = "daily_records.csv"
BUCKET_NAME = "internet_health"

client = storage.Client()
bucket = client.bucket(BUCKET_NAME)

def upload_file_to_gcs(uploaded_file, record_date, category):
    """
    將上傳的檔案上傳到 GCS，並以格式：YYYYMMDD_category_UUID.ext 重新命名，
    回傳該檔案的public URL。
    """
    if uploaded_file is not None:
        ext = os.path.splitext(uploaded_file.name)[1]
        new_filename = f"{record_date.strftime('%Y%m%d')}_{category}_{uuid.uuid4().hex}{ext}"
        blob = bucket.blob(new_filename)
        blob.upload_from_file(uploaded_file)
        return blob.public_url
    return ""

def load_records():
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE, parse_dates=["date"])
            return df.to_dict(orient="records")
        except Exception as e:
            print("Error loading records:", e)
            return []
    return []

def save_records(records):
    try:
        df = pd.DataFrame(records)
        df.to_csv(DATA_FILE, index=False)
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
