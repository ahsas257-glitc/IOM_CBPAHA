import streamlit as st
import pandas as pd
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ===================== PAGE CONFIG (MUST BE FIRST) =====================
st.set_page_config(page_title="Correction Log Helper", page_icon="📝", layout="wide")

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

# ===================== HERO =====================
st.markdown("""
<div class="glass-hero">
  <div style="text-align:center;">
    <h1 style="margin:0; font-size:2.35rem;" class="gradient-text">📝 Correction Log Helper</h1>
    <div style="display:flex; justify-content:center; align-items:center; margin-top:10px;">
      <span class="pulse-dot"></span>
      <span style="color:rgba(255,255,255,0.75); letter-spacing:2px;">DETECT DARI / PASHTO → PUSH TO CORRECTION_LOG</span>
      <span class="pulse-dot"></span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ----------------- CONFIG -----------------
json_path = r"D:\IOM_CBPAHA\iomcbpaha-37221bb23bb2.json"
sheet_id = "1AHTDIC9eAAitXwlR6wL_ruiTfZx6ytIuzJrV7GkHjQE"

data_sheet_name = "Data_Set"
correction_sheet_name = "Correction_Log"

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# ----------------- AUTH -----------------
def get_gspread_client():
    try:
        use_secrets = "gcp_service_account" in st.secrets
    except Exception:
        use_secrets = False

    if use_secrets:
        creds = ServiceAccountCredentials.from_json_keyfile_dict(
            st.secrets["gcp_service_account"], scope
        )
    else:
        creds = ServiceAccountCredentials.from_json_keyfile_name(json_path, scope)

    return gspread.authorize(creds)

client = get_gspread_client()



# ----------------- Helpers -----------------
def make_unique_headers(header_row):
    seen = {}
    new_cols = []
    for c in header_row:
        key = c if c is not None else ""
        if key in seen:
            seen[key] += 1
            new_cols.append(f"{key}_{seen[key]}")
        else:
            seen[key] = 0
            new_cols.append(key)
    return new_cols


def contains_persoarabic(text):
    if text is None:
        return False
    return bool(re.search(r'[\u0600-\u06FF]+', str(text)))


def load_sheet_dataframe(ws):
    values = ws.get_all_values()
    if not values:
        return pd.DataFrame()

    header = make_unique_headers(values[0])
    data = values[1:]

    if not data:
        return pd.DataFrame(columns=header)

    return pd.DataFrame(data, columns=header)


# ----------------- LOAD SHEETS -----------------
data_ws = client.open_by_key(sheet_id).worksheet(data_sheet_name)

# Load Correction_Log sheet or create if missing
try:
    corr_ws = client.open_by_key(sheet_id).worksheet(correction_sheet_name)
except gspread.exceptions.WorksheetNotFound:
    sh = client.open_by_key(sheet_id)
    corr_ws = sh.add_worksheet(title=correction_sheet_name, rows="2000", cols="20")

# Load Data_Set as DataFrame
df_data = load_sheet_dataframe(data_ws)

# ===================== TOP SUMMARY (UI ONLY) =====================
if df_data.empty:
    st.warning("Data_Set sheet is empty.")
    st.stop()

uuid_col = next((c for c in df_data.columns if c.startswith("_uuid")), None)
if uuid_col is None:
    st.error("Column '_uuid' not found in Data_Set.")
    st.stop()

# ----------------- Build detected records -----------------
records = []

for _, row in df_data.iterrows():
    row_uuid = str(row.get(uuid_col, "")).strip()
    if not row_uuid:
        continue

    for col in df_data.columns:
        if col == uuid_col:
            continue

        val = row[col]
        if contains_persoarabic(val):
            records.append({
                "_uuid": row_uuid,
                "Question": col,
                "old_value": val
            })

# ===================== SUMMARY CARDS (UI ONLY) =====================
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f"""
    <div class="card">
      <div class="badge badge-blue">DATA_SET</div>
      <div style="font-size:1.65rem; font-weight:800; color:#fff;">{len(df_data):,}</div>
      <div class="small-note">Total rows loaded</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="card">
      <div class="badge badge-purple">UUID COLUMN</div>
      <div style="font-size:1.1rem; font-weight:800; color:#fff;">{uuid_col}</div>
      <div class="small-note">Detected key field</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="card">
      <div class="badge badge-green">DETECTED</div>
      <div style="font-size:1.65rem; font-weight:800; color:#fff;">{len(records):,}</div>
      <div class="small-note">Cells containing Dari/Pashto</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ===================== PREVIEWS (UI ONLY) =====================
left, right = st.columns([1, 1])

with left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📁 Data_Set Preview")
    st.dataframe(df_data.head(), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("ℹ️ What this page does")
    st.markdown("""
   This tool scans the <b>Data_Set</b> and detects any cell containing
<b>Dari/Pashto</b> text. Each detected item is prepared in the format
(<b>_uuid, Question, old_value</b>) to be added to the <b>Correction_Log</b>.
<br><br>
When clicking <b>Add to Correction_Log</b>, only <b>new</b> records will be added.

    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ===================== DETECTED TABLE =====================
if not records:
    st.info("No Dari/Pashto text found.")
    st.stop()

out_df = pd.DataFrame(records).sort_values("Question")

st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("🔎 Detected Dari/Pashto Records (sorted by Question)")
st.dataframe(out_df, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

st.markdown("""
<div class="card">
  <div class="badge badge-orange">NOTE</div>
  <div class="small-note">
    When you click <b>Add to Correction_Log</b>, only <b>NEW</b> records will be added.
  </div>
</div>
""", unsafe_allow_html=True)

# ----------------- SAVE TO GOOGLE SHEET -----------------
if st.button("⬆️ Add to Correction_Log", type="primary"):

    existing = corr_ws.get_all_values()

    # If sheet is brand new → create header
    if not existing:
        header = ["_uuid", "Question", "old_value"]
        corr_ws.update("A1:C1", [header])
        existing = [header]

    # Load existing rows into dataframe
    corr_df = pd.DataFrame(existing[1:], columns=existing[0])

    # Build lookup set
    existing_keys = {
        f"{r['_uuid']}|{r['Question']}|{r['old_value']}"
        for _, r in corr_df.iterrows()
    }

    # Identify new rows to add
    rows_to_append = []
    for rec in records:
        key = f"{rec['_uuid']}|{rec['Question']}|{rec['old_value']}"
        if key not in existing_keys:
            rows_to_append.append([
                rec["_uuid"],
                rec["Question"],
                rec["old_value"]
            ])
            existing_keys.add(key)

    if not rows_to_append:
        st.warning("No NEW records. Everything already exists.")
    else:
        # Sort rows by Question before appending
        rows_to_append.sort(key=lambda x: x[1])

        next_row = len(existing) + 1
        corr_ws.update(
            f"A{next_row}:C{next_row + len(rows_to_append) - 1}",
            rows_to_append
        )

        st.success(f"✅ {len(rows_to_append)} new records added!")

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("✅ Newly Added Rows (sorted by Question)")
        st.dataframe(
            pd.DataFrame(rows_to_append, columns=["_uuid", "Question", "old_value"]).sort_values("Question"),
            use_container_width=True
        )
        st.markdown("</div>", unsafe_allow_html=True)
