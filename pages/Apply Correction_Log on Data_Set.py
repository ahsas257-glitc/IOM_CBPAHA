import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread.utils import rowcol_to_a1
from datetime import datetime

# ===================== PAGE CONFIG (MUST BE FIRST) =====================
st.set_page_config(page_title="Apply Corrections | IOM_CBPAHA", page_icon="🛠️", layout="wide")

# ===================== LIQUID GLASS STYLES =====================
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
  padding: 28px 30px;
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
  padding: 18px 18px;
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
  margin: 18px 0;
  border: none;
}

.small-note{
  color: rgba(255,255,255,0.65);
  font-size: 0.9rem;
}
</style>
""", unsafe_allow_html=True)

# ===================== HERO =====================
st.markdown("""
<div class="glass-hero">
  <div style="text-align:center;">
    <h1 style="margin:0; font-size:2.4rem;" class="gradient-text">🛠️ Apply Corrections — IOM_CBPAHA</h1>
    <div style="display:flex; justify-content:center; align-items:center; margin-top:10px;">
      <span class="pulse-dot"></span>
      <span style="color:rgba(255,255,255,0.75); letter-spacing:2px;">DATA QUALITY & CORRECTION WORKFLOW</span>
      <span class="pulse-dot"></span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ===================== SIDEBAR CONTROLS =====================
st.sidebar.markdown("### ⚙️ Settings")
mode = st.sidebar.selectbox("Apply Mode", ["Apply new_value only", "Apply even if empty (overwrite)"], index=0)
show_only_pending = st.sidebar.checkbox("Show only corrections with new_value", value=True)
preview_rows = st.sidebar.slider("Preview rows", 5, 50, 10)
st.sidebar.markdown("---")
run_confirm = st.sidebar.checkbox("I confirm I want to update Google Sheet", value=False)

# ===================== CONFIG =====================
# ✅ برای لوکال:
json_path = r"D:\IOM_CBPAHA\iomcbpaha-37221bb23bb2.json"
sheet_id = "1AHTDIC9eAAitXwlR6wL_ruiTfZx6ytIuzJrV7GkHjQE"
data_sheet_name = "Data_Set"
correction_sheet_name = "Correction_Log"
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

# ===================== AUTH (Local OR Secrets) =====================
def get_gspread_client():
    """
    Uses Streamlit Cloud secrets if available,
    otherwise falls back to local JSON file (for local development).
    """
    try:
        use_secrets = "gcp_service_account" in st.secrets
    except Exception:
        use_secrets = False

    if use_secrets:
        creds = ServiceAccountCredentials.from_json_keyfile_dict(
            st.secrets["gcp_service_account"], scope
        )
    else:
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            json_path, scope
        )

    return gspread.authorize(creds)


@st.cache_resource(show_spinner=False)
def load_worksheets():
    client = get_gspread_client()
    sh = client.open_by_key(sheet_id)
    return (
        sh.worksheet(data_sheet_name),
        sh.worksheet(correction_sheet_name)
    )

@st.cache_data(show_spinner=False, ttl=60)
def load_sheet_as_df(_ws):
    values = _ws.get_all_values()
    if not values or len(values) < 1:
        return pd.DataFrame()
    headers = values[0]
    rows = values[1:] if len(values) > 1 else []
    return pd.DataFrame(rows, columns=headers)


# ===================== LOAD =====================
with st.spinner("🔄 Connecting to Google Sheet..."):
    data_ws, corr_ws = load_worksheets()
    data_df = load_sheet_as_df(data_ws)
    corr_df = load_sheet_as_df(corr_ws)

if data_df.empty:
    st.warning("Data_Set is empty.")
    st.stop()

if corr_df.empty:
    st.warning("Correction_Log is empty or has no data.")
    st.stop()

# ===================== VALIDATION =====================
uuid_col = next((c for c in data_df.columns if c.startswith("_uuid")), None)
if uuid_col is None:
    st.error("Data_Set does not have a _uuid column.")
    st.stop()

required_cols = ["_uuid", "Question"]
missing = [c for c in required_cols if c not in corr_df.columns]
if missing:
    st.error(f"Correction_Log is missing required columns: {missing}")
    st.stop()

if "new_value" not in corr_df.columns:
    st.error("Correction_Log must contain a column named: new_value")
    st.stop()

# ===================== FILTER CORRECTIONS =====================
corr_df["_new_value_str"] = corr_df["new_value"].astype(str).fillna("").str.strip()
if show_only_pending:
    corr_view = corr_df[corr_df["_new_value_str"] != ""].copy()
else:
    corr_view = corr_df.copy()

# ===================== TOP SUMMARY CARDS =====================
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="card">
      <div class="badge badge-blue">DATA_SET</div>
      <div style="font-size:1.6rem; color:#fff; font-weight:800;">{len(data_df):,}</div>
      <div class="small-note">Total records</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="card">
      <div class="badge badge-purple">CORRECTIONS</div>
      <div style="font-size:1.6rem; color:#fff; font-weight:800;">{len(corr_df):,}</div>
      <div class="small-note">Rows in Correction_Log</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="card">
      <div class="badge badge-green">PENDING</div>
      <div style="font-size:1.6rem; color:#fff; font-weight:800;">{len(corr_view):,}</div>
      <div class="small-note">Has new_value</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="card">
      <div class="badge badge-orange">MODE</div>
      <div style="font-size:1.05rem; color:#fff; font-weight:800;">{mode}</div>
      <div class="small-note">Overwrite rule</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ===================== PREVIEWS =====================
left, right = st.columns([1, 1])

with left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 📁 Data_Set Preview")
    st.dataframe(data_df.head(preview_rows), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 📄 Correction_Log Preview")
    st.dataframe(corr_view.head(preview_rows), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ===================== APPLY CORRECTIONS =====================
st.markdown("""
<div class="card">
  <div class="badge badge-green">ACTION</div>
  <h3 style="margin: 8px 0 0 0; color:#a8edea;">Apply Corrections to Data_Set</h3>
  <p class="small-note" style="margin-top:8px;">
    این ابزار با استفاده از <b>_uuid</b> رکورد را پیدا می‌کند و ستون <b>Question</b> را با مقدار <b>new_value</b> آپدیت می‌کند.
  </p>
</div>
""", unsafe_allow_html=True)

apply_clicked = st.button("⬆️ Apply Corrections + Update Google Sheet", type="primary")

if apply_clicked:
    if not run_confirm:
        st.error("برای جلوگیری از اشتباه، از سایدبار تیک «I confirm…» را فعال کن.")
        st.stop()

    if corr_view.empty:
        st.info("هیچ new_value برای اعمال وجود ندارد.")
        st.stop()

    progress = st.progress(0)
    status = st.empty()

    applied_cells = 0
    applied_rows = 0
    errors = []

    # Track changes for reporting
    change_log = []

    total = len(corr_view)
    for i, corr_row in corr_view.reset_index(drop=True).iterrows():
        uuid = str(corr_row["_uuid"]).strip()
        question = str(corr_row["Question"]).strip()
        new_value = str(corr_row.get("new_value", "")).strip()

        # mode: overwrite rule
        if mode == "Apply new_value only" and new_value == "":
            continue

        if question not in data_df.columns:
            errors.append(f"Column not found in Data_Set: {question}")
            progress.progress(min(1.0, (i + 1) / total))
            continue

        mask = data_df[uuid_col].astype(str).str.strip() == uuid
        if not mask.any():
            errors.append(f"_uuid not found in Data_Set: {uuid}")
            progress.progress(min(1.0, (i + 1) / total))
            continue

        # Apply on all matched rows (usually 1 row, but safe)
        old_values = data_df.loc[mask, question].tolist()
        data_df.loc[mask, question] = new_value

        applied_rows += int(mask.sum())
        applied_cells += int(mask.sum())

        change_log.append({
            "_uuid": uuid,
            "Question": question,
            "old_value_sample": old_values[0] if old_values else "",
            "new_value": new_value
        })

        status.write(f"✅ Applying: {uuid} → {question}")
        progress.progress(min(1.0, (i + 1) / total))

    if applied_cells == 0:
        st.info("هیچ تغییری اعمال نشد.")
        if errors:
            st.warning("⚠️ Issues found:")
            st.write(errors[:20])
        st.stop()

    st.success(f"✅ Applied {applied_cells} updates.")

    # ---------------- UPDATE GOOGLE SHEET ----------------
    with st.spinner("📤 Updating Google Sheet (Data_Set)..."):
        all_data = [data_df.columns.tolist()] + data_df.values.tolist()
        end_cell = rowcol_to_a1(len(all_data), len(data_df.columns))
        data_ws.update(f"A1:{end_cell}", all_data)

    st.success("✅ Data_Set updated successfully in Google Sheet.")

    # ---------------- REPORTING ----------------
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    r1, r2 = st.columns([1, 1])
    with r1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🧾 Change Log (sample)")
        log_df = pd.DataFrame(change_log)
        st.dataframe(log_df.head(50), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with r2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### ⚠️ Errors (if any)")
        if errors:
            st.write(errors[:200])
        else:
            st.write("No errors ✅")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 📁 Updated Data_Set Preview")
    st.dataframe(data_df.head(preview_rows), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.caption(f"Last run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
