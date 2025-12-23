import streamlit as st
import pandas as pd
import re
from io import BytesIO

st.set_page_config(page_title="Missing Translation Extractor", page_icon="🗂️", layout="wide")

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

def extract_translation_list(df: pd.DataFrame, exclude_cols: list[str], remove_duplicates: bool):
    rows = []
    cols = [c for c in df.columns if c not in exclude_cols]

    for col in cols:
        for val in df[col]:
            if is_dari_pashto_text(val):
                rows.append(
                    {
                        "key": col,
                        "label": col,
                        "value": str(val).strip(),
                    }
                )

    out = pd.DataFrame(rows, columns=["key", "label", "value"])

    if remove_duplicates and not out.empty:
        out = out.drop_duplicates(subset=["key", "value"]).reset_index(drop=True)

    return out

def write_back_to_excel(original_file, selected_sheet, out_df, mode, output_sheet_name):
    import openpyxl

    original_file.seek(0)
    wb = openpyxl.load_workbook(original_file)

    target_sheet = selected_sheet
    if mode == "Create new sheet":
        base = output_sheet_name.strip() or "Translation_List"
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

st.markdown("## 🗂️ Missing Translation Extractor (Dari/Pashto)")
st.caption("Upload a dataset → select a sheet → (optional) exclude columns → export the translation list to Excel")

uploaded = st.file_uploader("📤 Upload Dataset (Excel .xlsx/.xlsm or CSV)", type=["xlsx", "xlsm", "csv"])

if not uploaded:
    st.stop()

try:
    meta = read_dataset(uploaded)
except Exception as e:
    st.error(str(e))
    st.stop()

exclude_cols = []
selected_sheet = None
df = None

left, right = st.columns([2, 1])

with left:
    if meta["type"] == "excel":
        selected_sheet = st.selectbox("📄 Select Sheet", meta["sheets"])
        df = pd.read_excel(meta["xls"], sheet_name=selected_sheet, dtype=str, keep_default_na=False)
    else:
        df = meta["df"]

    st.write("### Preview")
    st.dataframe(df.head(30), use_container_width=True)

with right:
    st.write("### Options")
    exclude_cols = st.multiselect(
        "🚫 Columns to Exclude (Optional)",
        options=list(df.columns),
        default=[],
        help="These columns will not be included in the exported translation list.",
    )

    if meta["type"] == "excel":
        write_mode = st.selectbox(
            "📝 Output Location",
            ["Overwrite selected sheet", "Create new sheet"],
            index=0,
        )
        output_sheet_name = st.text_input(
            "New Sheet Name (if creating a new sheet)",
            value="Translation_List",
        )
    else:
        write_mode = "Create new sheet"
        output_sheet_name = "Translation_List"

    remove_duplicates = st.checkbox("Remove duplicates (key+value)", value=True)

st.markdown("---")

if st.button("⚙️ Generate Master Translation List", type="primary"):
    out_df = extract_translation_list(df, exclude_cols, remove_duplicates)

    if out_df.empty:
        st.warning("No Dari/Pashto text was found (or all relevant columns were excluded).")
        st.stop()

    st.success(f"✅ Extracted: {len(out_df):,} rows")
    st.dataframe(out_df.head(200), use_container_width=True)

    if meta["type"] == "excel":
        out_file, target_sheet = write_back_to_excel(
            uploaded,
            selected_sheet,
            out_df,
            mode=write_mode,
            output_sheet_name=output_sheet_name,
        )
        st.download_button(
            "📥 Download Updated Excel",
            data=out_file,
            file_name=f"updated_{uploaded.name}",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        st.info(f"Output written to sheet: **{target_sheet}**")
    else:
        out_xlsx = BytesIO()
        with pd.ExcelWriter(out_xlsx, engine="openpyxl") as writer:
            out_df.to_excel(writer, sheet_name=output_sheet_name, index=False)
        out_xlsx.seek(0)
        st.download_button(
            "📥 Download Excel (Translation List)",
            data=out_xlsx,
            file_name="translation_list.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
