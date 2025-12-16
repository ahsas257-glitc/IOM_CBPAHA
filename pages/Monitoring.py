import streamlit as st
import pandas as pd
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ---------------- CONFIG ----------------
json_path = r"D:\IOM_CBPAHA\iomcbpaha-37221bb23bb2.json"
sheet_id = "1AHTDIC9eAAitXwlR6wL_ruiTfZx6ytIuzJrV7GkHjQE"

DATA_SHEET = "Data_Set"
CORR_SHEET = "Correction_Log_1"
HIDE_SHEET = "Not_Show_in_form"     # ✅ NEW
HIDE_LABEL_COL = "Labels"           # ✅ NEW

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# ---------------- AUTH ----------------
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
sheet = client.open_by_key(sheet_id).worksheet(sheet_name)


data_ws = sh.worksheet(DATA_SHEET)

try:
    corr_ws = sh.worksheet(CORR_SHEET)
except gspread.exceptions.WorksheetNotFound:
    corr_ws = sh.add_worksheet(title=CORR_SHEET, rows="3000", cols="10")
    corr_ws.update("A1:E1", [["_uuid", "Question", "old_value", "new_value", "Edited_By"]])


# ---------------- HELPERS ----------------
def contains_persoarabic(text):
    # Persian/Arabic block (covers Dari/Pashto/Arabic)
    return bool(re.search(r'[\u0600-\u06FF]', str(text)))


def load_df(ws):
    v = ws.get_all_values()
    if not v or len(v) < 2:
        return pd.DataFrame()
    return pd.DataFrame(v[1:], columns=v[0])


def normalize_val(x):
    if x is None:
        return ""
    # keep as string, trimmed
    return str(x).strip()


@st.cache_data(show_spinner=False, ttl=120)
def load_hide_labels() -> set:
    """
    Loads Labels column from Not_Show_in_form sheet.
    Any value in Labels = a column name to hide in the form.
    """
    try:
        ws_hide = sh.worksheet(HIDE_SHEET)
    except gspread.exceptions.WorksheetNotFound:
        return set()

    df_hide = load_df(ws_hide)
    if df_hide.empty or HIDE_LABEL_COL not in df_hide.columns:
        return set()

    labels = (
        df_hide[HIDE_LABEL_COL]
        .astype(str)
        .map(lambda x: x.strip())
        .replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})
        .dropna()
        .tolist()
    )

    # Allow comma-separated labels in a single cell
    out = set()
    for item in labels:
        for part in str(item).split(","):
            p = part.strip()
            if p:
                out.add(p)
    return out


def needs_attention(old_val: str) -> bool:
    """
    Filter Mode logic:
    show only if empty-like OR contains Dari/Pashto/Arabic script.
    """
    v = normalize_val(old_val)
    if not v:
        return True
    if v.strip().lower() in ["n/a", "na", "null", "none", "nan", "-", "--"]:
        return True
    if contains_persoarabic(v):
        return True
    return False


# ---------------- LIQUID GLASS UI ----------------
st.set_page_config("Data Refinery | Cleaning Form", "🔮", layout="wide")

# ✅ Standardized sizes (Current/New)
CURRENT_MIN_H = 100
CURRENT_MAX_H = 200
NEW_TEXT_H = 100

st.markdown(f"""
<style>
@keyframes gradientShift {{
    0% {{ background-position: 0% 50%; }}
    50% {{ background-position: 100% 50%; }}
    100% {{ background-position: 0% 50%; }}
}}

.stApp {{
    background: linear-gradient(-45deg,
        #0a0a14 0%,
        #15152a 25%,
        #1a1a35 50%,
        #0f172a 75%,
        #0a0a14 100%);
    background-size: 400% 400%;
    animation: gradientShift 18s ease infinite;
    min-height: 100vh;
}}

.glass-header {{
    background: linear-gradient(135deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.03) 100%);
    border-radius: 24px;
    padding: 25px 30px;
    margin: 20px 0 30px 0;
    border: 1px solid rgba(255,255,255,0.12);
    box-shadow:
        0 20px 40px rgba(0,0,0,0.3),
        0 0 60px rgba(100,150,255,0.1),
        inset 0 1px 0 rgba(255,255,255,0.1);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    position: relative;
    overflow: hidden;
}}

.glass-card {{
    background: linear-gradient(145deg, rgba(255,255,255,0.07) 0%, rgba(255,255,255,0.04) 100%);
    border-radius: 20px;
    padding: 22px 24px;
    margin: 16px 0;
    border: 1px solid rgba(255,255,255,0.1);
    box-shadow:
        0 15px 35px rgba(0,0,0,0.2),
        0 5px 15px rgba(0,0,0,0.1),
        inset 0 1px 0 rgba(255,255,255,0.05);
    backdrop-filter: blur(15px);
    -webkit-backdrop-filter: blur(15px);
}}

.status-badge {{
    display: inline-flex;
    align-items: center;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.5px;
    margin-left: 10px;
    backdrop-filter: blur(10px);
}}

.badge-choice {{
    background: linear-gradient(135deg, rgba(120,220,120,0.2), rgba(80,180,80,0.1));
    border: 1px solid rgba(120,220,120,0.3);
    color: #aaffaa;
}}
.badge-text {{
    background: linear-gradient(135deg, rgba(120,180,255,0.2), rgba(80,140,220,0.1));
    border: 1px solid rgba(120,180,255,0.3);
    color: #aaccff;
}}
.badge-rtl {{
    background: linear-gradient(135deg, rgba(255,180,120,0.2), rgba(220,140,80,0.1));
    border: 1px solid rgba(255,180,120,0.3);
    color: #ffccaa;
    margin-left: 8px;
}}

/* ✅ Standardized Current Value Box */
.current-value-display {{
    background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(245,245,255,0.98) 100%) !important;
    border-radius: 16px;
    padding: 18px !important;
    border: 2px solid rgba(255,255,255,0.9) !important;
    color: #1a1a1a !important;
    font-size: 15px !important;
    line-height: 1.6 !important;
    min-height: {CURRENT_MIN_H}px;
    max-height: {CURRENT_MAX_H}px;
    overflow: auto;
    white-space: pre-wrap;
    word-break: break-word;
    position: relative;
}}

.current-value-display.rtl-text {{
    text-align: right;
    direction: rtl;
}}

.current-label {{
    position: absolute;         /* ✅ حتماً مقدار داشته باشد */
    top: 8px;                   
    left: 14px;
    background: linear-gradient(135deg, #4ecdc4, #45b7d1);
    color: #ffffff !important;
    padding: 4px 12px;
    border-radius: 10px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    box-shadow: 0 4px 12px rgba(78, 205, 196, 0.35);
    z-index: 5;
    pointer-events: none;
}}

.value-length {{
    position: absolute;
    bottom: 8px;
    right: 12px;
    font-size: 11px;
    color: #666;
    background: rgba(255,255,255,0.7);
    padding: 2px 8px;
    border-radius: 10px;
}}

/* ✅ New value area */
.new-value-area {{
    background: rgba(20,30,50,0.30);
    border-radius: 16px;
    border: 1px solid rgba(100,200,255,0.25);
    padding: 16px;
}}

/* Buttons */
.stButton > button {{
    background: linear-gradient(135deg, rgba(100,200,255,0.9) 0%, rgba(80,180,240,0.9) 100%) !important;
    border: none !important;
    color: white !important;
    padding: 14px 32px !important;
    border-radius: 16px !important;
    font-weight: 600 !important;
}}

/* Input */
.stTextInput > div > div > input {{
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 14px !important;
    color: white !important;
    padding: 14px !important;
    font-size: 15px !important;
}}

.divider {{
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), rgba(100,200,255,0.3), rgba(255,255,255,0.1), transparent);
    margin: 25px 0;
    border: none;
}}
</style>
""", unsafe_allow_html=True)


# ---------------- HERO HEADER ----------------
st.markdown("""
<div class="glass-header">
    <div style="display:flex; align-items:center; justify-content:space-between;">
        <div>
            <h1 style="margin:0;font-size:2.8rem;background:linear-gradient(135deg,#4ecdc4,#45b7d1,#a8edea);-webkit-background-clip:text;-webkit-text-fill-color:transparent;letter-spacing:1px;">
                🔮 Data Refinery
            </h1>
            <p style="color:rgba(255,255,255,0.7);margin-top:10px;font-size:1.1rem;">
                Precision Cleaning Interface with Liquid Glass UI
            </p>
        </div>
        <div style="text-align:right;">
            <div style="font-size:0.9rem;color:rgba(255,255,255,0.6);margin-bottom:5px;">SESSION ACTIVE</div>
            <div style="display:inline-flex;background:rgba(0,0,0,0.2);border-radius:16px;padding:8px 16px;border:1px solid rgba(255,255,255,0.1);">
                <span style="font-size:20px;margin-right:8px;">✦</span>
                <span style="color:rgba(255,255,255,0.8);">Live Editing</span>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------- SESSION INPUT ----------------
st.markdown('<div class="glass-card" style="margin-top:-10px;">', unsafe_allow_html=True)
st.markdown("<h3 style='margin-top:0;color:#a8edea;'>📋 Session Configuration</h3>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns([2, 2, 1, 1])

with col1:
    uuid_input = st.text_input("Record Identifier", placeholder="Enter _uuid ...", key="uuid_input")

with col2:
    editor_name = st.text_input("Editor Profile", placeholder="Your name ...", key="editor_name")

with col3:
    st.markdown("<br>", unsafe_allow_html=True)
    show_only_needed = st.toggle("Filter Mode", value=False, help="Show only fields needing attention (empty/NA or Dari/Pashto)")

with col4:
    st.markdown("<br>", unsafe_allow_html=True)
    auto_save = st.toggle("Auto-save", value=True, help="Save on submit (safe).")

st.markdown("</div>", unsafe_allow_html=True)

if not uuid_input or not editor_name:
    st.info("Please enter _uuid and your name to begin.")
    st.stop()


# ---------------- LOAD DATA ----------------
df = load_df(data_ws)

if df.empty:
    st.error("❌ Data_Set is empty.")
    st.stop()

if "_uuid" not in df.columns:
    st.error("❌ Data_Set sheet must contain _uuid column.")
    st.stop()

if uuid_input not in df["_uuid"].astype(str).values:
    st.error("❌ _uuid not found in Data_Set.")
    st.stop()

# ✅ Load hidden labels and remove those columns from questions
hidden_labels = load_hide_labels()
hidden_labels_lower = {x.strip().lower() for x in hidden_labels}

row = df[df["_uuid"].astype(str) == str(uuid_input)].iloc[0]

# ✅ Exclude hidden columns
questions_all = [c for c in df.columns if c != "_uuid"]
questions = [c for c in questions_all if c.strip().lower() not in hidden_labels_lower]

# ---------------- ANALYZE QUESTIONS ----------------
question_types = {}
for q in questions:
    # safe unique extraction
    uniq = (
        df[q].astype(str).map(lambda x: x.strip())
        .replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})
        .dropna()
        .unique()
        .tolist()
    )

    if len(uniq) <= 7:
        question_types[q] = ("select", sorted(uniq))
    else:
        question_types[q] = ("text", None)

# ---------------- PANEL HEADER ----------------
st.markdown(f"""
<div class="glass-card">
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <div>
            <h3 style="margin:0;color:#a8edea;">📊 Record Panel</h3>
            <p style="margin:5px 0 0 0;color:rgba(255,255,255,0.6);">
                UUID: <code style="background:rgba(100,200,255,0.1);padding:2px 8px;border-radius:6px;">{str(uuid_input)[:12]}...</code>
            </p>
            <p style="margin:8px 0 0 0;color:rgba(255,255,255,0.5);font-size:0.9rem;">
                Hidden columns loaded from <b>{HIDE_SHEET}</b>: <b>{len(hidden_labels)}</b>
            </p>
        </div>
        <div style="background:rgba(0,0,0,0.2);border-radius:16px;padding:10px 18px;border:1px solid rgba(255,255,255,0.1);">
            <div style="font-size:22px;font-weight:700;color:#4ecdc4;">{len(questions)}</div>
            <div style="font-size:12px;color:rgba(255,255,255,0.6);letter-spacing:1px;text-transform:uppercase;">Fields</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ---------------- FORM ----------------
changes = []
edited_count = 0

# ✅ GLOBAL EDIT CONTROLS
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
cA, cB, cC = st.columns([2, 2, 2])

with cA:
    edit_all = st.toggle("✏️ Edit ALL fields", value=False, key="edit_all_toggle")

with cB:
    lock_all = st.toggle("🔒 Lock ALL fields", value=False, key="lock_all_toggle")

with cC:
    st.caption("اگر Edit All روشن باشد، دیگر نیازی به تیک زدن تک‌تک سوال‌ها نیست.")

st.markdown("</div>", unsafe_allow_html=True)
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

with st.form("cleaning_form", clear_on_submit=False):

    for idx, q in enumerate(questions):
        old_val = normalize_val(row[q])
        q_type, options = question_types[q]
        rtl = contains_persoarabic(old_val)

        # ✅ Filter Mode only hides fields not needing attention
        if show_only_needed and not needs_attention(old_val):
            continue

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)

        head1, head2 = st.columns([4, 1])
        with head1:
            badge_type = "CHOICE" if q_type == "select" else "TEXT"
            badge_class = "badge-choice" if q_type == "select" else "badge-text"
            st.markdown(f"""
            <div style="display:flex; align-items:center;">
                <h4 style="margin:0;color:#ffffff;font-weight:500;">{q}</h4>
                <span class="status-badge {badge_class}">{badge_type}</span>
                {('<span class="status-badge badge-rtl">RTL</span>' if rtl else '')}
            </div>
            """, unsafe_allow_html=True)

        # ✅ per-field edit flag with stable session_state
        field_key = f"do_{q}"

        # initialize state
        if field_key not in st.session_state:
            st.session_state[field_key] = False

        # apply global toggles
        if lock_all:
            st.session_state[field_key] = False
        elif edit_all:
            st.session_state[field_key] = True

        with head2:
            st.checkbox("✏️ Edit", key=field_key)

        do_edit = st.session_state[field_key]

        colA, colB = st.columns(2)

        # -------- Current value --------
        with colA:
            st.markdown("<div style='color:rgba(255,255,255,0.8);margin-bottom:8px;'>Current Value</div>", unsafe_allow_html=True)
            display_class = "current-value-display" + (" rtl-text" if rtl else "")
            value_length = len(old_val) if old_val else 0
            safe_old_val = str(old_val).replace("<", "&lt;").replace(">", "&gt;")

            st.markdown(f"""
            <div class="{display_class}">
                <div class="current-label">ORIGINAL</div>
                <div style="padding-top:10px;">{safe_old_val if safe_old_val else '<span style="color:#888;font-style:italic;">Empty value</span>'}</div>
                <div class="value-length">{value_length} chars</div>
            </div>
            """, unsafe_allow_html=True)

        # -------- New value --------
        with colB:
            st.markdown("<div style='color:rgba(255,255,255,0.8);margin-bottom:8px;'>Refined Value</div>", unsafe_allow_html=True)

            new_val = old_val

            if do_edit:
                edited_count += 1
                st.markdown('<div class="new-value-area">', unsafe_allow_html=True)

                if q_type == "select":
                    safe_options = list(dict.fromkeys([old_val] + (options if options else [])))
                    if not safe_options:
                        safe_options = [""]

                    idx_option = safe_options.index(old_val) if old_val in safe_options else 0

                    new_val = st.selectbox(
                        "Select refined value",
                        safe_options,
                        index=idx_option,
                        key=f"sel_{q}",
                        label_visibility="collapsed"
                    )
                else:
                    new_val = st.text_area(
                        "Type refined text",
                        value=old_val,
                        height=NEW_TEXT_H,
                        key=f"txt_{q}",
                        label_visibility="collapsed"
                    )

                st.markdown("</div>", unsafe_allow_html=True)

            else:
                st.markdown("""
                <div style="background:rgba(255,255,255,0.03);border-radius:16px;padding:34px;text-align:center;border:2px dashed rgba(255,255,255,0.12);">
                    <div style="font-size:2rem;margin-bottom:10px;">🔒</div>
                    <div style="color:rgba(255,255,255,0.5);">Editing disabled (Turn on Edit / Edit All)</div>
                </div>
                """, unsafe_allow_html=True)

        # ✅ Track changes only if actually changed
        if do_edit and normalize_val(new_val) != normalize_val(old_val):
            changes.append([uuid_input, q, old_val, new_val, editor_name])

        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    submitted = st.form_submit_button("🚀 COMPLETE REFINEMENT & SAVE CHANGES", type="primary", use_container_width=True)

# ---------------- SAVE ----------------
if submitted:
    if not changes:
        st.warning("No changes detected.")
    else:
        # ✅ Save once (safe, no duplication from per-field writes)
        corr_ws.append_rows(changes, value_input_option="RAW")
        st.success(f"✅ Saved: {len(changes)} change(s) | Editor: {editor_name}")
        st.caption(f"Hidden columns applied from {HIDE_SHEET}: {len(hidden_labels)}")
