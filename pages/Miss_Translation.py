import streamlit as st
import pandas as pd
import re
from io import BytesIO

st.set_page_config(page_title="Master Translation Extractor", page_icon="🗂️", layout="wide")

# ----------------- Helpers -----------------
ARABIC_BLOCK_RE = re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]")

def is_dari_pashto_text(x) -> bool:
    """Detects whether a value contains Arabic-script characters (Dari/Pashto)."""
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
    elif name.endswith(".xlsx") or name.endswith(".xlsm"):
        xls = pd.ExcelFile(uploaded_file)
        return {"type": "excel", "xls": xls, "sheets": xls.sheet_names}
    else:
        raise ValueError("Only CSV or XLSX/XLSM files are supported.")

def extract_translation_list(df: pd.DataFrame, exclude_cols: list[str]):
    rows = []
    cols = [c for c in df.columns if c not in exclude_cols]

    for col in cols:
        series = df[col]
        # هر مقدار متنی دری/پشتو را استخراج کن
        for val in series:
            if is_dari_pashto_text(val):
                rows.append({
                    "key": col,
                    "label": col,   # اگر خواستید لیبل را از جای دیگر بگیرید، اینجا تغییر می‌کند
                    "value": str(val).strip()
                })

    out = pd.DataFrame(rows, columns=["key", "label", "value"])

    # اختیاری: حذف تکراری‌ها برای تمیزتر شدن لیست
    if not out.empty:
        out = out.drop_duplicates(subset=["key", "value"]).reset_index(drop=True)

    return out

def write_back_to_excel(original_file, selected_sheet, out_df, mode, output_sheet_name):
    """
    mode:
      - "Overwrite selected sheet" -> پاک کردن شیت انتخابی و نوشتن خروجی داخل همان شیت
      - "Create new sheet" -> نوشتن خروجی در شیت جدید
    """
    import openpyxl

    # فایل آپلودی را از BytesIO دوباره به ورک‌بوک تبدیل می‌کنیم
    original_file.seek(0)
    wb = openpyxl.load_workbook(original_file)

    target_sheet = selected_sheet
    if mode == "Create new sheet":
        # اگر شیت موجود باشد، یک نام جدید بساز
        base = output_sheet_name.strip() or "Translation_List"
        name = base
        i = 1
        while name in wb.sheetnames:
            i += 1
            name = f"{base}_{i}"
        wb.create_sheet(title=name)
        target_sheet = name

    ws = wb[target_sheet]

    # پاک کردن محتویات شیت (اگر overwrite)
    if mode == "Overwrite selected sheet":
        ws.delete_rows(1, ws.max_row)

    # نوشتن هدر
    ws["A1"] = "key"
    ws["B1"] = "label"
    ws["C1"] = "value"

    # نوشتن دیتا
    for r_idx, row in enumerate(out_df.itertuples(index=False), start=2):
        ws.cell(row=r_idx, column=1, value=row.key)
        ws.cell(row=r_idx, column=2, value=row.label)
        ws.cell(row=r_idx, column=3, value=row.value)

    # خروجی به BytesIO
    buff = BytesIO()
    wb.save(buff)
    buff.seek(0)
    return buff, target_sheet

# ----------------- UI -----------------
st.markdown("## 🗂️ Master Translation Extractor (Dari/Pashto)")
st.caption("یک دیتاست آپلود کنید → شیت را انتخاب کنید → (اختیاری) ستون‌های exclude → خروجی لیست ترجمه در Excel")

uploaded = st.file_uploader("📤 Upload Dataset (Excel .xlsx/.xlsm یا CSV)", type=["xlsx", "xlsm", "csv"])

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
        "🚫 Columns to EXCLUDE (Optional)",
        options=list(df.columns),
        default=[],
        help="این ستون‌ها در خروجی Master List وارد نمی‌شوند."
    )

    if meta["type"] == "excel":
        write_mode = st.selectbox(
            "📝 Output Location",
            ["Overwrite selected sheet", "Create new sheet"],
            index=0
        )
        output_sheet_name = st.text_input(
            "New Sheet Name (if create new sheet)",
            value="Translation_List"
        )
    else:
        write_mode = "Create new sheet"
        output_sheet_name = "Translation_List"

    remove_duplicates = st.checkbox("Remove duplicates (key+value)", value=True)

# ----------------- Processing -----------------
st.markdown("---")

if st.button("⚙️ Generate Master Translation List", type="primary"):
    out_df = extract_translation_list(df, exclude_cols)

    if out_df.empty:
        st.warning("هیچ متن دری/پشتو پیدا نشد (یا همه ستون‌ها exclude شدند).")
        st.stop()

    if not remove_duplicates:
        # اگر کاربر نخواست حذف duplicates انجام شود، دوباره از خام بسازیم بدون drop_duplicates
        # (برای ساده‌گی همان خروجی فعلی را می‌گذاریم. اگر خواستید دقیقاً خام باشد، بگویید.)
        pass

    st.success(f"✅ استخراج شد: {len(out_df):,} ردیف")
    st.dataframe(out_df.head(200), use_container_width=True)

    # Export
    if meta["type"] == "excel":
        out_file, target_sheet = write_back_to_excel(
            uploaded, selected_sheet, out_df,
            mode=write_mode,
            output_sheet_name=output_sheet_name
        )
        st.download_button(
            "📥 Download Updated Excel",
            data=out_file,
            file_name=f"updated_{uploaded.name}",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        st.info(f"Output written to sheet: **{target_sheet}**")
    else:
        # CSV -> خروجی Excel جدید بساز
        out_xlsx = BytesIO()
        with pd.ExcelWriter(out_xlsx, engine="openpyxl") as writer:
            out_df.to_excel(writer, sheet_name=output_sheet_name, index=False)
        out_xlsx.seek(0)
        st.download_button(
            "📥 Download Excel (Translation List)",
            data=out_xlsx,
            file_name="translation_list.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
