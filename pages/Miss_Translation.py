import streamlit as st
import pandas as pd
import re
from io import BytesIO

st.set_page_config(page_title="Missing Translation Extractor", page_icon="🗂️", layout="wide")

st.markdown(
    """
<style>
.stApp{
  background: linear-gradient(135deg, #f7f9ff 0%, #eef3ff 35%, #f9fbff 100%);
}
.block-container{ padding-top: 1.5rem; }

.glass-header{
  background: rgba(255,255,255,0.55);
  border: 1px solid rgba(255,255,255,0.75);
  border-radius: 22px;
  padding: 18px 22px;
  box-shadow: 0 14px 30px rgba(30,60,120,0.10);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
}
.glass-card{
  background: rgba(255,255,255,0.50);
  border: 1px solid rgba(255,255,255,0.70);
  border-radius: 18px;
  padding: 16px 18px;
  box-shadow: 0 10px 22px rgba(30,60,120,0.10);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
}
.small-help{ color: rgba(20,30,60,0.65); font-size: 0.92rem; }
.hr{
  height: 1px;
  margin: 14px 0 18px 0;
  background: linear-gradient(90deg, transparent, rgba(120,140,200,0.35), transparent);
  border: none;
}
div[data-testid="stDataFrame"]{
  background: rgba(255,255,255,0.35);
  border-radius: 14px;
  border: 1px solid rgba(255,255,255,0.55);
}
</style>
""",
    unsafe_allow_html=True,
)

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
        return {"type": "csv", "df": df, "sheets": None}
    if name.endswith(".xlsx") or name.endswith(".xlsm"):
        xls = pd.ExcelFile(uploaded_file)
        return {"type": "excel", "xls": xls, "sheets": xls.sheet_names}
    raise ValueError("Only CSV or XLSX/XLSM files are supported.")

def columns_with_dari_pashto(df: pd.DataFrame, limit_scan: int = 2000) -> list[str]:
    cols = []
    n = min(len(df), limit_scan)
    if n == 0:
        return cols
    sample = df.head(n)
    for c in sample.columns:
        s = sample[c]
        found = False
        for v in s:
            if is_dari_pashto_text(v):
                found = True
                break
        if found:
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

def write_back_to_excel(original_file, selected_sheet, out_df, mode, output_sheet_name):
    import openpyxl

    original_file.seek(0)
    wb = openpyxl.load_workbook(original_file)

    target_sheet = selected_sheet
    if mode == "Create new sheet":
        base = (output_sheet_name or "").strip() or "Translation_List"
        name = base
        i = 1
        while name in wb.sheetnames:
            i += 1
            name = f"{base}_{i}"
        wb.create_sheet(title=name)
        target_sheet = name

    ws = wb[target_sheet]

    if mode == "Overwrite selected sheet":
        ws.delete_rows(1, ws.max_row)

    ws["A1"] = "key"
    ws["B1"] = "label"
    ws["C1"] = "value"

    for r_idx, row in enumerate(out_df.itertuples(index=False), start=2):
        ws.cell(row=r_idx, column=1, value=row.key)
        ws.cell(row=r_idx, column=2, value=row.label)
        ws.cell(row=r_idx, column=3, value=row.value)

    buff = BytesIO()
    wb.save(buff)
    buff.seek(0)
    return buff, target_sheet

def build_excel_from_df(out_df: pd.DataFrame, sheet_name: str):
    buff = BytesIO()
    with pd.ExcelWriter(buff, engine="openpyxl") as writer:
        out_df.to_excel(writer, sheet_name=sheet_name or "Translation_List", index=False)
    buff.seek(0)
    return buff

st.markdown(
    """
<div class="glass-header">
  <div style="display:flex;align-items:center;justify-content:space-between;gap:14px;">
    <div>
      <div style="font-size:28px;font-weight:800;color:rgba(20,30,60,0.92);">🗂️ Missing Translation Extractor</div>
      <div class="small-help">Upload dataset → choose sheet → choose key column → exclude only columns that contain Dari/Pashto → download Excel</div>
    </div>
    <div style="padding:10px 14px;border-radius:16px;border:1px solid rgba(255,255,255,0.7);background:rgba(255,255,255,0.45);">
      <div style="font-size:12px;color:rgba(20,30,60,0.65);letter-spacing:1px;">LIQUID GLASS</div>
      <div style="font-weight:700;color:rgba(20,30,60,0.85);">Light Theme</div>
    </div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown("<div class='hr'></div>", unsafe_allow_html=True)

uploaded = st.file_uploader("📤 Upload Dataset (Excel .xlsx/.xlsm or CSV)", type=["xlsx", "xlsm", "csv"])

if not uploaded:
    st.stop()

try:
    meta = read_dataset(uploaded)
except Exception as e:
    st.error(str(e))
    st.stop()

selected_sheet = None
df = None

left, right = st.columns([2, 1], gap="large")

with left:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

    if meta["type"] == "excel":
        selected_sheet = st.selectbox("📄 Select Sheet", meta["sheets"])
        df = pd.read_excel(meta["xls"], sheet_name=selected_sheet, dtype=str, keep_default_na=False)
    else:
        df = meta["df"]

    st.write("### Preview")
    st.dataframe(df.head(40), use_container_width=True, height=360)

    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.write("### Settings")

    key_col = st.selectbox(
        "🔑 Key Column",
        options=list(df.columns),
        index=0,
        help="This column will be used as the key in the exported list.",
    )

    cols_dp = columns_with_dari_pashto(df, limit_scan=2000)

    if cols_dp:
        exclude_cols = st.multiselect(
            "🚫 Exclude Columns (only columns that contain Dari/Pashto)",
            options=cols_dp,
            default=[],
            help="Only columns that include Dari/Pashto text appear here.",
        )
    else:
        exclude_cols = []
        st.info("No columns with Dari/Pashto text were detected in this dataset.")

    if meta["type"] == "excel":
        write_mode = st.selectbox(
            "📝 Output Location",
            ["Create new sheet", "Overwrite selected sheet"],
            index=0,
        )
        output_sheet_name = st.text_input("Output Sheet Name", value="Translation_List")
    else:
        write_mode = "Create new sheet"
        output_sheet_name = "Translation_List"

    remove_duplicates = st.checkbox("Remove duplicates (key+label+value)", value=True)

    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='hr'></div>", unsafe_allow_html=True)

if st.button("⚙️ Generate Master Translation List", type="primary"):
    out_df = extract_translation_list(df, key_col, exclude_cols, remove_duplicates)

    if out_df.empty:
        st.warning("No Dari/Pashto text was found (or all relevant columns were excluded).")
        st.stop()

    st.success(f"✅ Extracted: {len(out_df):,} rows")
    st.dataframe(out_df.head(250), use_container_width=True, height=420)

    if meta["type"] == "excel":
        out_file, target_sheet = write_back_to_excel(
            uploaded,
            selected_sheet,
            out_df,
            mode=write_mode,
            output_sheet_name=output_sheet_name,
        )
        st.download_button(
            "📥 Download Excel",
            data=out_file,
            file_name=f"translations_{uploaded.name}",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        st.info(f"Output written to sheet: **{target_sheet}**")
    else:
        out_xlsx = build_excel_from_df(out_df, output_sheet_name)
        st.download_button(
            "📥 Download Excel",
            data=out_xlsx,
            file_name="translation_list.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
