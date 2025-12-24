import streamlit as st
import pandas as pd
import re
from io import BytesIO

st.set_page_config(
    page_title="Translation Extractor Pro",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=JetBrains+Mono:wght@300;400&display=swap');

* {
    font-family: 'Poppins', sans-serif;
    color: #ffffff;
}

.stApp {
    background: linear-gradient(135deg, 
        #0a0f1a 0%, 
        #121828 25%, 
        #1a1a2e 50%, 
        #16213e 75%, 
        #0a0f1a 100%);
    background-size: 400% 400%;
    animation: cosmicFloat 20s ease infinite;
    min-height: 100vh;
}

@keyframes cosmicFloat {
    0% { background-position: 0% 50% }
    50% { background-position: 100% 50% }
    100% { background-position: 0% 50% }
}

.neon-glow {
    text-shadow: 
        0 0 10px rgba(255, 255, 255, 0.3),
        0 0 20px rgba(255, 255, 255, 0.2),
        0 0 30px rgba(255, 255, 255, 0.1);
}

.crystal-panel {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(25px) saturate(180%);
    -webkit-backdrop-filter: blur(25px) saturate(180%);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 28px;
    padding: 28px 34px;
    margin-bottom: 30px;
    box-shadow: 
        0 20px 60px rgba(0, 0, 0, 0.5),
        inset 0 1px 0 rgba(255, 255, 255, 0.1),
        inset 0 -1px 0 rgba(0, 0, 0, 0.5);
    position: relative;
    overflow: hidden;
}

.crystal-panel::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 200%;
    height: 100%;
    background: linear-gradient(90deg, 
        transparent, 
        rgba(255, 255, 255, 0.05), 
        transparent);
    animation: shimmer 3s infinite;
}

@keyframes shimmer {
    0% { transform: translateX(-100%) }
    100% { transform: translateX(100%) }
}

.quantum-card {
    background: linear-gradient(145deg, 
        rgba(255, 255, 255, 0.08) 0%, 
        rgba(255, 255, 255, 0.04) 100%);
    backdrop-filter: blur(20px) saturate(160%);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 24px;
    padding: 24px 28px;
    margin-bottom: 24px;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}

.quantum-card::after {
    content: '';
    position: absolute;
    top: -2px;
    left: -2px;
    right: -2px;
    bottom: -2px;
    background: linear-gradient(45deg, 
        rgba(255, 255, 255, 0.3), 
        rgba(200, 200, 255, 0.2), 
        rgba(255, 255, 255, 0.3), 
        rgba(255, 255, 255, 0.2));
    background-size: 400% 400%;
    border-radius: 26px;
    z-index: -1;
    opacity: 0;
    transition: opacity 0.4s;
    animation: gradientBorder 3s ease infinite;
}

.quantum-card:hover::after {
    opacity: 0.3;
}

@keyframes gradientBorder {
    0% { background-position: 0% 50% }
    50% { background-position: 100% 50% }
    100% { background-position: 0% 50% }
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
    margin: 25px 0;
}

.neon-stat {
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 20px;
    padding: 22px;
    text-align: center;
    position: relative;
    overflow: hidden;
    transition: all 0.3s ease;
}

.neon-stat:hover {
    transform: translateY(-5px);
    border-color: rgba(255, 255, 255, 0.4);
    box-shadow: 0 10px 30px rgba(255, 255, 255, 0.1);
}

.neon-stat::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, 
        rgba(255, 255, 255, 0.5), 
        rgba(200, 200, 255, 0.3), 
        rgba(255, 255, 255, 0.5));
    background-size: 200% 100%;
    animation: statGlow 2s linear infinite;
}

@keyframes statGlow {
    0% { background-position: 0% 0% }
    100% { background-position: 200% 0% }
}

.stat-number {
    font-size: 42px;
    font-weight: 700;
    background: linear-gradient(135deg, 
        #ffffff 0%, #ccccff 50%, #ffffff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 10px 0;
    font-family: 'JetBrains Mono', monospace;
}

.stat-label {
    font-size: 14px;
    color: rgba(255, 255, 255, 0.9);
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 1.5px;
}

.section-title {
    font-size: 20px;
    font-weight: 600;
    color: #ffffff;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 12px;
}

.section-title::before {
    content: '⟠';
    font-size: 24px;
    color: #ffffff;
    opacity: 0.8;
}

.stButton > button {
    background: linear-gradient(135deg, 
        rgba(255, 255, 255, 0.15) 0%, 
        rgba(200, 200, 255, 0.15) 100%);
    color: #ffffff;
    border: 1px solid rgba(255, 255, 255, 0.3);
    padding: 16px 36px;
    border-radius: 16px;
    font-weight: 600;
    font-size: 17px;
    transition: all 0.3s ease;
    box-shadow: 0 8px 32px rgba(255, 255, 255, 0.1);
    width: 100%;
    position: relative;
    overflow: hidden;
}

.stButton > button::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, 
        transparent, 
        rgba(255, 255, 255, 0.1), 
        transparent);
    transition: 0.5s;
}

.stButton > button:hover::before {
    left: 100%;
}

.stButton > button:hover {
    transform: translateY(-3px);
    box-shadow: 0 15px 40px rgba(255, 255, 255, 0.15);
    background: linear-gradient(135deg, 
        rgba(255, 255, 255, 0.2) 0%, 
        rgba(200, 200, 255, 0.2) 100%);
}

.stDataFrame {
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 20px !important;
    overflow: hidden !important;
}

.holographic-divider {
    height: 2px;
    background: linear-gradient(90deg, 
        transparent, 
        rgba(255, 255, 255, 0.5), 
        rgba(200, 200, 255, 0.3), 
        rgba(255, 255, 255, 0.5), 
        transparent);
    margin: 32px 0;
    border: none;
    border-radius: 2px;
}

.file-input {
    border: 2px dashed rgba(255, 255, 255, 0.3);
    border-radius: 20px;
    padding: 40px;
    text-align: center;
    background: rgba(255, 255, 255, 0.05);
    transition: all 0.3s ease;
    color: #ffffff;
}

.file-input:hover {
    border-color: rgba(255, 255, 255, 0.6);
    background: rgba(255, 255, 255, 0.08);
}

.stSelectbox > div > div,
.stMultiselect > div > div,
.stTextInput > div > div > input,
.stCheckbox > label {
    color: #ffffff !important;
    background: rgba(255, 255, 255, 0.08) !important;
    border-color: rgba(255, 255, 255, 0.2) !important;
}

.stSelectbox > div > div:hover,
.stMultiselect > div > div:hover {
    border-color: rgba(255, 255, 255, 0.4) !important;
}

.stSelectbox svg,
.stMultiselect svg {
    fill: #ffffff !important;
}

.stCheckbox > label > div:first-child {
    background: rgba(255, 255, 255, 0.08) !important;
    border-color: rgba(255, 255, 255, 0.2) !important;
}

.stCheckbox > label > div:first-child:hover {
    border-color: rgba(255, 255, 255, 0.4) !important;
}

.stCheckbox > label > div:first-child > div {
    background: #ffffff !important;
}

.particle {
    position: absolute;
    width: 4px;
    height: 4px;
    background: rgba(255, 255, 255, 0.5);
    border-radius: 50%;
    pointer-events: none;
}

.stSuccess {
    background: rgba(255, 255, 255, 0.1) !important;
    color: #ffffff !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
}

.stInfo {
    background: rgba(255, 255, 255, 0.1) !important;
    color: #ffffff !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
}

.stWarning {
    background: rgba(255, 255, 255, 0.1) !important;
    color: #ffffff !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
}

.stError {
    background: rgba(255, 255, 255, 0.1) !important;
    color: #ffffff !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
}

.stSpinner > div {
    color: #ffffff !important;
}

.stDownloadButton > button {
    background: linear-gradient(135deg, 
        rgba(255, 255, 255, 0.15) 0%, 
        rgba(200, 200, 255, 0.15) 100%) !important;
    color: #ffffff !important;
    border: 1px solid rgba(255, 255, 255, 0.3) !important;
}

.stDownloadButton > button:hover {
    background: linear-gradient(135deg, 
        rgba(255, 255, 255, 0.2) 0%, 
        rgba(200, 200, 255, 0.2) 100%) !important;
    border-color: rgba(255, 255, 255, 0.4) !important;
}

</style>
""", unsafe_allow_html=True)

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
        found = False
        for v in sample[c]:
            if is_dari_pashto_text(v):
                found = True
                break
        if found:
            cols.append(c)
    return cols

def extract_translation_list(df: pd.DataFrame, key_col: str, exclude_cols: list[str], remove_duplicates: bool):
    rows = []
    exclude_set = set(exclude_cols)
    
    total_rows = len(df)
    total_cols = len(df.columns)
    
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
                rows.append({
                    "key": key_val, 
                    "label": col, 
                    "value": str(val).strip(),
                    "row_index": idx + 1
                })
    
    out = pd.DataFrame(rows, columns=["key", "label", "value", "row_index"])
    
    if remove_duplicates and not out.empty:
        out = out.drop_duplicates(subset=["key", "label", "value"]).reset_index(drop=True)
    
    return out, total_rows, total_cols

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

st.markdown("""
<div class="crystal-panel">
    <div style="text-align: center; margin-bottom: 10px;">
        <h1 class="neon-glow" style="font-size: 48px; margin: 0; color: #ffffff;">⚡ TRANSLATION EXTRACTOR PRO</h1>
        <p style="color: rgba(255, 255, 255, 0.9); font-size: 18px; margin-top: 10px;">
            Quantum-Powered Translation Extraction Engine
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="stats-grid">
    <div class="neon-stat">
        <div class="stat-label">Total Rows</div>
        <div class="stat-number" id="total-rows">0</div>
        <div style="color: rgba(255, 255, 255, 0.7); font-size: 12px;">Dataset Size</div>
    </div>
    <div class="neon-stat">
        <div class="stat-label">Total Columns</div>
        <div class="stat-number" id="total-columns">0</div>
        <div style="color: rgba(255, 255, 255, 0.7); font-size: 12px;">Data Structure</div>
    </div>
    <div class="neon-stat">
        <div class="stat-label">Translations</div>
        <div class="stat-number" id="total-translations">0</div>
        <div style="color: rgba(255, 255, 255, 0.7); font-size: 12px;">Extracted Items</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="holographic-divider"></div>', unsafe_allow_html=True)

st.markdown('<div class="quantum-card"><div class="section-title">📤 UPLOAD DATASET</div>', unsafe_allow_html=True)
uploaded = st.file_uploader(
    "Drag & Drop or Click to Upload",
    type=["xlsx", "xlsm", "csv"],
    label_visibility="collapsed",
    key="file_upload"
)
st.markdown("</div>", unsafe_allow_html=True)

if not uploaded:
    st.markdown("""
    <div style="text-align: center; padding: 60px; color: rgba(255, 255, 255, 0.8);">
        <div style="font-size: 64px; margin-bottom: 20px;">🌌</div>
        <h3 style="color: #ffffff;">Ready for Quantum Processing</h3>
        <p style="color: rgba(255, 255, 255, 0.8);">Upload your dataset to begin extraction</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

try:
    meta = read_dataset(uploaded)
except Exception as e:
    st.error(f"❌ Error: {str(e)}")
    st.stop()

selected_sheet = None
df = None

if meta["type"] == "excel":
    st.markdown('<div class="quantum-card"><div class="section-title">📄 SELECT WORKSHEET</div>', unsafe_allow_html=True)
    selected_sheet = st.selectbox(
        "Choose worksheet:",
        meta["sheets"],
        label_visibility="collapsed"
    )
    df = pd.read_excel(meta["xls"], sheet_name=selected_sheet, dtype=str, keep_default_na=False)
    st.markdown("</div>", unsafe_allow_html=True)
else:
    df = meta["df"]

st.markdown(f"""
<script>
document.getElementById('total-rows').textContent = '{len(df):,}';
document.getElementById('total-columns').textContent = '{len(df.columns)}';
</script>
""", unsafe_allow_html=True)

st.markdown('<div class="quantum-card"><div class="section-title">👁️ DATA PREVIEW</div>', unsafe_allow_html=True)
st.dataframe(df.head(20), use_container_width=True, height=350)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="quantum-card"><div class="section-title">⚙️ EXTRACTION PARAMETERS</div>', unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    key_col = st.selectbox(
        "🔑 KEY COLUMN",
        options=list(df.columns),
        index=0,
        help="Identifier column for translations"
    )
    
    cols_dp = columns_with_dari_pashto(df, limit_scan=2000)
    if cols_dp:
        exclude_cols = st.multiselect(
            "🚫 EXCLUDE COLUMNS",
            options=cols_dp,
            default=[],
            help="Columns to exclude from extraction"
        )
    else:
        exclude_cols = []
        st.info("No Dari/Pashto columns detected")

with col2:
    output_sheet_name = st.text_input(
        "📝 OUTPUT SHEET NAME",
        value="Translation_List",
        help="Name for the export sheet"
    )
    
    remove_duplicates = st.checkbox(
        "🌀 REMOVE DUPLICATES",
        value=True,
        help="Eliminate duplicate translation entries"
    )

st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="holographic-divider"></div>', unsafe_allow_html=True)

if st.button("🚀 INITIATE QUANTUM EXTRACTION", type="primary", use_container_width=True):
    with st.spinner("🔄 Processing dataset..."):
        out_df, total_rows, total_cols = extract_translation_list(df, key_col, exclude_cols, remove_duplicates)
        
        if out_df.empty:
            st.warning("⚠️ No translations found")
            st.stop()
        
        st.markdown(f"""
        <script>
        document.getElementById('total-translations').textContent = '{len(out_df):,}';
        </script>
        """, unsafe_allow_html=True)
        
        st.success(f"✅ Success! Extracted {len(out_df):,} translations")
        
        st.markdown('<div class="quantum-card"><div class="section-title">📋 EXTRACTED TRANSLATIONS</div>', unsafe_allow_html=True)
        st.dataframe(out_df.head(250), use_container_width=True, height=500)
        st.markdown("</div>", unsafe_allow_html=True)
        
        col_d1, col_d2 = st.columns(2)
        
        with col_d1:
            out_xlsx = build_excel_from_df(out_df, output_sheet_name)
            safe_base = re.sub(r'[^a-zA-Z0-9_-]+', '_', uploaded.name.rsplit('.', 1)[0])
            out_name = f"translations_{safe_base}.xlsx"
            
            st.download_button(
                "💾 DOWNLOAD EXCEL",
                data=out_xlsx,
                file_name=out_name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="download_excel"
            )
        
        with col_d2:
            csv_data = out_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                "📄 DOWNLOAD CSV",
                data=csv_data,
                file_name="translations.csv",
                mime="text/csv",
                use_container_width=True,
                key="download_csv"
            )

st.markdown("""
<div style="text-align: center; margin-top: 40px; color: rgba(255, 255, 255, 0.6); font-size: 12px;">
    <div style="margin-bottom: 10px; color: rgba(255, 255, 255, 0.7);">⚡ Powered by Shabeer Ahmad Ahsas</div>
    <div style="color: rgba(255, 255, 255, 0.6);">© 2025 Translation Extractor Pro • v2.0</div>
</div>
""", unsafe_allow_html=True)
