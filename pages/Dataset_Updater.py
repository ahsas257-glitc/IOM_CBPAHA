import streamlit as st
import pandas as pd
import io
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ===================== PAGE CONFIG (MUST BE FIRST) =====================
st.set_page_config(page_title="Excel Date Filter & Google Sheet Updater", page_icon="📊", layout="wide")

# ===================== LIQUID GLASS UI (STYLE ONLY) =====================
st.markdown("""
<style>
@keyframes gradientFlow {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
@keyframes floaty {
  0%,100%{ transform: translateY(0px); }
  50%{ transform: translateY(-10px); }
}
@keyframes pulse {
  0%,100% { opacity: 1; transform: scale(1); }
  50% { opacity: .55; transform: scale(1.15); }
}

.stApp{
  background: linear-gradient(-45deg,#0a0a14 0%,#15152a 25%,#1a1a35 50%,#0f172a 75%,#0a0a14 100%);
  background-size: 400% 400%;
  animation: gradientFlow 25s ease infinite;
  min-height: 100vh;
}

.glass-hero{
  background: linear-gradient(135deg, rgba(255,255,255,0.09), rgba(255,255,255,0.03));
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 26px;
  padding: 26px 28px;
  box-shadow: 0 25px 50px rgba(0,0,0,0.35), 0 0 80px rgba(100,150,255,0.12);
  backdrop-filter: blur(22px);
  -webkit-backdrop-filter: blur(22px);
  animation: floaty 7s ease-in-out infinite;
  margin-bottom: 18px;
}

.gradient-text{
  background: linear-gradient(135deg,#4ecdc4 0%,#45b7d1 35%,#a8edea 55%,#45b7d1 75%,#4ecdc4 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-size: 200% 200%;
  animation: gradientFlow 8s ease infinite;
}

.pulse-dot{
  display:inline-block;
  width:8px; height:8px;
  border-radius:50%;
  background:#4ecdc4;
  box-shadow:0 0 10px rgba(78,205,196,0.6);
  animation: pulse 2s infinite;
  margin: 0 10px;
}

.card{
  background: linear-gradient(145deg, rgba(255,255,255,0.07), rgba(255,255,255,0.03));
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 18px;
  padding: 16px 16px;
  box-shadow: 0 15px 35px rgba(0,0,0,0.25);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  margin: 10px 0;
}

.badge{
  display:inline-flex; align-items:center;
  padding: 7px 14px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: .4px;
  margin: 0 8px 8px 0;
  border: 1px solid rgba(255,255,255,0.12);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.badge-blue{ background: rgba(69,183,209,0.12); color:#a8edea; border-color: rgba(69,183,209,0.25); }
.badge-green{ background: rgba(120,220,120,0.12); color:#aaffaa; border-color: rgba(120,220,120,0.25); }
.badge-orange{ background: rgba(255,180,120,0.12); color:#ffccaa; border-color: rgba(255,180,120,0.25); }
.badge-purple{ background: rgba(180,120,255,0.12); color:#d4aaff; border-color: rgba(180,120,255,0.25); }

.divider{
  height:2px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.12), rgba(100,200,255,0.35), rgba(255,255,255,0.12), transparent);
  margin: 16px 0;
  border: none;
}

.small-note{
  color: rgba(255,255,255,0.65);
  font-size: 0.9rem;
  line-height: 1.7;
}
</style>
""", unsafe_allow_html=True)

# ===================== HERO (UI ONLY) =====================
st.markdown("""
<div class="glass-hero">
  <div style="text-align:center;">
    <h1 style="margin:0; font-size:2.35rem;" class="gradient-text">📊 Excel Start-Date Filter & Google Sheet Updater</h1>
    <div style="display:flex; justify-content:center; align-items:center; margin-top:10px;">
      <span class="pulse-dot"></span>
      <span style="color:rgba(255,255,255,0.75); letter-spacing:2px;">
        FILTER → REMOVE UUIDs → UPLOAD NEW RECORDS → DOWNLOAD
      </span>
      <span class="pulse-dot"></span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ===================== ORIGINAL CODE (LOGIC UNCHANGED) =====================
json_path = r"D:\IOM_CBPAHA\iomcbpaha-37221bb23bb2.json"
sheet_id = "1AHTDIC9eAAitXwlR6wL_ruiTfZx6ytIuzJrV7GkHjQE"
sheet_name = "Data_Set"
remove_sheet_name = "Remove_from_DS"

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(json_path, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(sheet_id).worksheet(sheet_name)

# Read removal keys from Remove_from_DS sheet
try:
    remove_sheet = client.open_by_key(sheet_id).worksheet(remove_sheet_name)
    remove_values = remove_sheet.get_all_values()
    if len(remove_values) > 0:
        headers = remove_values[0]
        if "_uuid" in headers:
            remove_df = pd.DataFrame(remove_values[1:], columns=headers)
            if "_uuid" in remove_df.columns:
                remove_uuids = set(remove_df["_uuid"].astype(str))
            else:
                remove_uuids = set()
        else:
            remove_uuids = set()
    else:
        remove_uuids = set()
except Exception as e:
    st.warning(f"⚠️ Could not read Remove_from_DS sheet: {e}")
    remove_uuids = set()

# Read existing data
all_values = sheet.get_all_values()
if len(all_values) == 0:
    existing_data = pd.DataFrame()
    existing_uuids = set()
else:
    cols = all_values[0]
    seen = {}
    new_cols = []
    for c in cols:
        if c in seen:
            seen[c] += 1
            new_cols.append(f"{c}_{seen[c]}")
        else:
            seen[c] = 0
            new_cols.append(c)
    existing_data = pd.DataFrame(all_values[1:], columns=new_cols)
    if "_uuid" in existing_data.columns:
        existing_uuids = set(existing_data["_uuid"].astype(str))
    else:
        existing_uuids = set()

# ===================== UI (ENGLISH ONLY) =====================
st.markdown("""
<div class="card">
  <div class="badge badge-blue">UPLOAD</div>
  <div class="small-note">
    Upload an Excel file, select a date column, choose a start date, then filter the dataset.
    Records whose <b>_uuid</b> exists in <b>Remove_from_DS</b> will be excluded before upload.
  </div>
</div>
""", unsafe_allow_html=True)

dataset = st.file_uploader("📂 Upload your Excel dataset:", type=["xlsx"])

if dataset:
    df = pd.read_excel(dataset)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 📁 Dataset Preview")
    st.dataframe(df.head(), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    date_column = st.selectbox("🗂️ Select Date Column:", df.columns)
    df[date_column] = pd.to_datetime(df[date_column], errors="coerce")

    if df[date_column].isnull().all():
        st.error("❌ Selected column does NOT contain valid date values!")
    else:
        start_date = st.date_input("📅 Select Start Date")
        filtered_df = df[df[date_column] >= pd.to_datetime(start_date)].copy()

        # Remove records whose key exists in Remove_from_DS
        if "_uuid" in filtered_df.columns:
            filtered_df = filtered_df[~filtered_df["_uuid"].astype(str).isin(remove_uuids)]

        for col in filtered_df.select_dtypes(include=["float", "int"]).columns:
            filtered_df[col] = pd.to_numeric(filtered_df[col], errors="coerce").astype("Int64")

        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🔎 Filtered Data")
        max_cells = 262144
        total_cells = filtered_df.shape[0] * filtered_df.shape[1]
        if total_cells <= max_cells:
            styled = filtered_df.style.set_properties(**{
                'background-color': '#F9F9F9',
                'color': '#2E4053',
                'border-color': '#D5DBDB',
                'border-width': '1px',
                'border-style': 'solid'
            }).highlight_max(color='#82E0AA').highlight_min(color='#F1948A')
            st.dataframe(styled, use_container_width=True)
        else:
            st.info(f"ℹ️ Data too large for styled view ({total_cells} cells). Showing plain table for performance.")
            st.dataframe(filtered_df, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("""
        <div class="badge badge-green">UPLOAD TO GOOGLE SHEET</div>
        <div class="small-note">
          Click the button below to append only <b>new</b> records to <b>Data_Set</b> (based on <b>_uuid</b>).
        </div>
        """, unsafe_allow_html=True)

        if st.button("⬆️ Upload New Records to Google Sheet", type="primary"):
            if "_uuid" not in filtered_df.columns:
                st.error("❌ ERROR: Column '_uuid' not found in dataset!")
            else:
                new_rows = filtered_df[~filtered_df["_uuid"].astype(str).isin(existing_uuids)]
                if new_rows.empty:
                    st.warning("⚠️ No new records to add. All UUIDs already exist.")
                else:
                    clean_rows = new_rows.copy()
                    for col in clean_rows.columns:
                        if pd.api.types.is_datetime64_any_dtype(clean_rows[col]):
                            clean_rows[col] = clean_rows[col].dt.strftime("%Y-%m-%d")
                    rows_to_upload = clean_rows.astype(str).replace("nan", "").replace("<NA>", "").values.tolist()
                    sheet.append_rows(rows_to_upload)
                    st.success(f"✅ {len(new_rows)} new rows successfully added to Google Sheet!")
        st.markdown("</div>", unsafe_allow_html=True)

        # Download filtered data as Excel (unchanged logic)
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            for col in filtered_df.select_dtypes(include=["float", "int"]).columns:
                filtered_df[col] = pd.to_numeric(filtered_df[col], errors="coerce").astype("Int64")
            filtered_df.to_excel(writer, sheet_name="FilteredData", index=False)
        buffer.seek(0)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("""
        <div class="badge badge-purple">DOWNLOAD</div>
        <div class="small-note">Download the filtered output as an Excel file.</div>
        """, unsafe_allow_html=True)

        st.download_button(
            label="📥 Download filtered data as Excel",
            data=buffer,
            file_name="filtered_data_output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        st.markdown("</div>", unsafe_allow_html=True)
