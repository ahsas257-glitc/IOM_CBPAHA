import streamlit as st
import pandas as pd
import re
from io import BytesIO

# تنظیمات صفحه
st.set_page_config(
    page_title="Missing Translation Extractor",
    page_icon="🗂️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# استایل‌های Liquid Glass
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* { font-family: 'Inter', sans-serif; }

.stApp {
    background: linear-gradient(-45deg,
        #f0f5ff 0%,
        #e8f0ff 25%,
        #f8fbff 50%,
        #ebf2ff 75%,
        #f0f5ff 100%);
    background-size: 400% 400%;
    animation: gradientBG 15s ease infinite;
    min-height: 100vh;
}

@keyframes gradientBG {
    0% { background-position: 0% 50% }
    50% { background-position: 100% 50% }
    100% { background-position: 0% 50% }
}

.main-header {
    background: rgba(255, 255, 255, 0.72);
    backdrop-filter: blur(20px) saturate(180%);
    -webkit-backdrop-filter: blur(20px) saturate(180%);
    border: 1px solid rgba(255, 255, 255, 0.85);
    border-radius: 24px;
    padding: 24px 32px;
    margin-bottom: 22px;
    box-shadow:
        0 8px 32px rgba(31, 38, 135, 0.07),
        inset 0 1px 0 rgba(255, 255, 255, 0.6),
        inset 0 -1px 0 rgba(0, 0, 0, 0.05);
}

.badge {
    display: inline-flex;
    align-items: center;
    padding: 6px 14px;
    background: rgba(255, 255, 255, 0.7);
    border: 1px solid rgba(120, 140, 220, 0.4);
    border-radius: 20px;
    font-size: 14px;
    font-weight: 500;
    color: #1a237e;
    backdrop-filter: blur(10px);
}

.glass-card {
    background: rgba(255, 255, 255, 0.65);
    backdrop-filter: blur(18px) saturate(200%);
    -webkit-backdrop-filter: blur(18px) saturate(200%);
    border: 1px solid rgba(255, 255, 255, 0.75);
    border-radius: 20px;
    padding: 22px 26px;
    margin-bottom: 24px;
    box-shadow:
        0 12px 28px rgba(31, 38, 135, 0.08),
        inset 0 1px 0 rgba(255, 255, 255, 0.7),
        0 1px 3px rgba(0, 0, 0, 0.02);
}

.section-title {
    font-size: 18px;
    font-weight: 600;
    color: #1a237e;
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    gap: 10px;
}

.divider {
    height: 1px;
    background: linear-gradient(90deg,
        transparent,
        rgba(120, 140, 220, 0.4),
        transparent);
    margin: 22px 0;
    border: none;
}
</style>
""", unsafe_allow_html=True)

# Regex برای تشخیص متن فارسی/پشتو
ARABIC_BLOCK_RE = re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]")

def is_dari_pashto_text(x) -> bool:
    if x is None:
        return False
    s = str(x).strip()
    if not s or s.lower() in {"nan", "none", "null"}:
        return False
    return bool(ARABIC_BLOCK_RE.search(s))

def read_dataset(uploaded_file):
    name = uploaded_file.name.lower()
    if name.endswith(".csv"):
        df = pd.read_csv(uploaded_file, dtype=str, keep_default_na=False)
        return {"type": "csv", "df": df, "sheets": None, "xls": None}

    if name.endswith(".xlsx") or name.endswith(".xlsm"):
        xls = pd.ExcelFile(uploaded_file)
        return {"type": "excel", "df": None, "sheets": xls.sheet_names, "xls": xls}

    raise ValueError("Only CSV or XLSX/XLSM files are supported.")

def columns_with_dari_pashto(df: pd.DataFrame, limit_scan: int = 2000) -> list[str]:
    cols = []
    n = min(len(df), limit_scan)
    if n == 0:
        return cols
    sample = df.head(n)
    for c in sample.columns:
        if any(is_dari_pashto_text(v) for v in sample[c]):
            cols.append(c)
    return cols

def extract_translation_list(df: pd.DataFrame, key_col: str, exclude_cols: list[str], remove_duplicates: bool):
    rows = []
    exclude_set = set(exclude_cols)

    for idx, row in df.iterrows():
        key_raw = row.get(key_col, "")
        key_val = str(key_raw).strip()
        if not key_val or key_val.lower() in {"nan", "none", "null"}:
            key_val = f"ROW_{idx+1:06d}"

        for col in df.columns:
            if col in exclude_set:
                continue
            val = row.get(col, "")
            if is_dari_pashto_text(val):
                rows.append({"key": key_val, "label": col, "value": str(val).strip()})

    out = pd.DataFrame(rows, columns=["key", "label", "value"])
    if remove_duplicates and not out.empty:
        out = out.drop_duplicates(subset=["key", "label", "value"]).reset_index(drop=True)
    return out

def build_excel_from_df(out_df: pd.DataFrame, sheet_name: str):
    import openpyxl
    from openpyxl.utils import get_column_letter

    buff = BytesIO()
    sheet = (sheet_name or "Translation_List").strip() or "Translation_List"

    with pd.ExcelWriter(buff, engine="openpyxl") as writer:
        out_df.to_excel(writer, sheet_name=sheet, index=False)
        ws = writer.book[sheet]
        ws.freeze_panes = "A2"

        for col_idx, col_name in enumerate(out_df.columns, start=1):
            values = out_df[col_name].head(500).astype(str).tolist()
            max_len = max([len(str(col_name))] + [len(v) for v in values if v is not None])
            ws.column_dimensions[get_column_letter(col_idx)].width = min(max_len + 3, 60)

    buff.seek(0)
    return buff

# -------------------------------
# ✅ Session State برای آمار ترجمه‌ها
# -------------------------------
if "translations_count" not in st.session_state:
    st.session_state.translations_count = 0

# Header
st.markdown("""
<div class="main-header">
  <div style="display:flex;justify-content:space-between;align-items:center;gap:12px;">
    <div>
      <h1 style="margin:0;color:#1a237e;font-size:32px;font-weight:700;">🗂️ Missing Translation Extractor</h1>
      <p style="margin:6px 0 0 0;color:#555;font-size:16px;">Extract Dari/Pashto translations from datasets with ease</p>
    </div>
    <div class="badge"><span style="margin-right:8px;">✨</span> Missing Translation</div>
  </div>
</div>
""", unsafe_allow_html=True)

# Upload
st.markdown("""
<div class="glass-card">
  <div class="section-title">📤 Upload Dataset</div>
</div>
""", unsafe_allow_html=True)

uploaded = st.file_uploader(
    "Drag and drop or click to upload Excel (.xlsx/.xlsm) or CSV file",
    type=["xlsx", "xlsm", "csv"],
    label_visibility="collapsed"
)

if not uploaded:
    st.info("👆 Please upload a dataset to get started")
    st.stop()

try:
    meta = read_dataset(uploaded)
except Exception as e:
    st.error(f"❌ Error reading file: {str(e)}")
    st.stop()

# Select sheet & load df
selected_sheet = None
if meta["type"] == "excel":
    st.markdown('<div class="glass-card"><div class="section-title">📄 Select Worksheet</div></div>', unsafe_allow_html=True)
    selected_sheet = st.selectbox("Choose the worksheet to analyze:", meta["sheets"], label_visibility="collapsed")
    df = pd.read_excel(meta["xls"], sheet_name=selected_sheet, dtype=str, keep_default_na=False)
else:
    df = meta["df"]

# ✅ Stats (بدون JS)
rows_count = len(df)
cols_count = df.shape[1]
trans_count = st.session_state.translations_count

c1, c2, c3 = st.columns(3)
c1.metric("Total Rows", f"{rows_count:,}")
c2.metric("Columns", f"{cols_count:,}")
c3.metric("Translations", f"{trans_count:,}")

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# Preview
st.markdown('<div class="glass-card"><div class="section-title">👁️ Data Preview</div></div>', unsafe_allow_html=True)
st.dataframe(df.head(30), use_container_width=True, height=400)

# Settings
st.markdown('<div class="glass-card"><div class="section-title">⚙️ Extraction Settings</div></div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    key_col = st.selectbox("🔑 Key Column", options=list(df.columns), index=0)
    cols_dp = columns_with_dari_pashto(df, limit_scan=2000)
    if cols_dp:
        exclude_cols = st.multiselect("🚫 Exclude Columns", options=cols_dp, default=[])
    else:
        exclude_cols = []
        st.info("ℹ️ No columns with Dari/Pashto text were detected")

with col2:
    output_sheet_name = st.text_input("Output Sheet Name", value="Translation_List")
    remove_duplicates = st.checkbox("Remove duplicate translations", value=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# Extract button
if st.button("🚀 Generate Translation List", type="primary", use_container_width=True):
    with st.spinner("🔍 Extracting translations..."):
        out_df = extract_translation_list(df, key_col, exclude_cols, remove_duplicates)

    if out_df.empty:
        st.session_state.translations_count = 0
        st.warning("⚠️ No Dari/Pashto text was found in the dataset (or all relevant columns were excluded)")
        st.stop()

    # ✅ Update translations count in state
    st.session_state.translations_count = len(out_df)

    st.success(f"✅ Successfully extracted {len(out_df):,} translation entries!")

    st.markdown('<div class="glass-card"><div class="section-title">📋 Extracted Translations</div></div>', unsafe_allow_html=True)
    st.dataframe(out_df.head(200), use_container_width=True, height=450)

    col_d1, col_d2 = st.columns(2)

    with col_d1:
        out_xlsx = build_excel_from_df(out_df, output_sheet_name)
        safe_base = re.sub(r'[^a-zA-Z0-9_-]+', '_', uploaded.name.rsplit('.', 1)[0])
        out_name = f"translation_list_{safe_base}.xlsx"

        st.download_button(
            "📥 Download Excel (One Sheet Only)",
            data=out_xlsx,
            file_name=out_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key="download_excel_one_sheet"
        )
        st.info(f"📄 Export contains only one sheet: **{(output_sheet_name or 'Translation_List')}**")

    with col_d2:
        csv_data = out_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            "📄 Download as CSV",
            data=csv_data,
            file_name="translation_list.csv",
            mime="text/csv",
            use_container_width=True,
            key="download_csv"
        )

    # ✅ بعد از استخراج، stats بالا در rerun درست نمایش داده می‌شود
    st.rerun()
