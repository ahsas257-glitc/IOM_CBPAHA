import streamlit as st
import pandas as pd
import numpy as np
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import plotly.express as px
import warnings

warnings.filterwarnings("ignore")

# ---------------- OPTIONAL LIBS (NO-ERROR IMPORT) ----------------
ALTair_OK = True
MPL_OK = True
SNS_OK = True
SCIPY_OK = True

try:
    import altair as alt
except Exception:
    ALTair_OK = False

try:
    import matplotlib.pyplot as plt
except Exception:
    MPL_OK = False

try:
    import seaborn as sns
except Exception:
    SNS_OK = False

try:
    from scipy import stats
except Exception:
    SCIPY_OK = False


# ---------------- CONFIG ----------------
json_path = r"D:\IOM_CBPAHA\iomcbpaha-37221bb23bb2.json"
sheet_id = "1AHTDIC9eAAitXwlR6wL_ruiTfZx6ytIuzJrV7GkHjQE"
DATA_SHEET = "Data_Set"

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# ---------------- PAGE CONFIG ----------------
st.set_page_config("Data Visualization Suite | Liquid Glass", "🔮", layout="wide")

# ---------------- LIQUID GLASS UI STYLING ----------------
st.markdown(
    """
<style>
@keyframes gradientFlow { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }

.stApp{
  background: linear-gradient(-45deg, #0a0a14, #15152a, #1a1a35, #0f172a);
  background-size: 400% 400%;
  animation: gradientFlow 20s ease infinite;
  min-height: 100vh;
}

.glass-header{
  background: linear-gradient(135deg, rgba(255,255,255,0.09) 0%, rgba(255,255,255,0.03) 100%);
  border-radius: 24px;
  padding: 25px 30px;
  margin: 0 0 25px 0;
  border: 1px solid rgba(255,255,255,0.12);
  box-shadow: 0 20px 40px rgba(0,0,0,0.3), 0 0 60px rgba(100,150,255,0.1), inset 0 1px 0 rgba(255,255,255,0.1);
  backdrop-filter: blur(20px);
  position: relative;
  overflow: hidden;
}

.glass-header::before{
  content:'';
  position:absolute;
  top:0; left:-100%;
  width:100%; height:100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.05), transparent);
  animation: shine 4s infinite;
}
@keyframes shine { 0% { left:-100%; } 20%,100% { left:100%; } }

.glass-card{
  background: linear-gradient(145deg, rgba(255,255,255,0.07) 0%, rgba(255,255,255,0.04) 100%);
  border-radius: 20px;
  padding: 22px 24px;
  margin: 16px 0;
  border: 1px solid rgba(255,255,255,0.1);
  box-shadow: 0 15px 35px rgba(0,0,0,0.2), 0 5px 15px rgba(0,0,0,0.1), inset 0 1px 0 rgba(255,255,255,0.05);
  backdrop-filter: blur(15px);
  transition: all 0.3s ease;
}
.glass-card:hover{
  border-color: rgba(100,200,255,0.3);
  box-shadow: 0 20px 40px rgba(0,0,0,0.25), 0 0 30px rgba(100,200,255,0.1);
  transform: translateY(-2px);
}
.glass-card.active{
  border-color: rgba(100,220,255,0.4);
  background: linear-gradient(145deg, rgba(100,200,255,0.08) 0%, rgba(100,200,255,0.03) 100%);
  box-shadow: 0 20px 40px rgba(0,0,0,0.25), 0 0 40px rgba(100,220,255,0.15);
}

.chip{
  display:inline-flex;
  align-items:center;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.5px;
  margin: 0 6px 6px 0;
  backdrop-filter: blur(10px);
}
.chip-numeric{ background: linear-gradient(135deg, rgba(120,220,120,0.2), rgba(80,180,80,0.1)); border:1px solid rgba(120,220,120,0.3); color:#aaffaa; }
.chip-categorical{ background: linear-gradient(135deg, rgba(120,180,255,0.2), rgba(80,140,220,0.1)); border:1px solid rgba(120,180,255,0.3); color:#aaccff; }
.chip-text{ background: linear-gradient(135deg, rgba(220,180,255,0.2), rgba(160,120,220,0.1)); border:1px solid rgba(220,180,255,0.3); color:#e5ccff; }
.chip-date{ background: linear-gradient(135deg, rgba(255,180,120,0.2), rgba(220,140,80,0.1)); border:1px solid rgba(255,180,120,0.3); color:#ffccaa; }
.chip-unknown{ background: rgba(255,255,255,0.08); border:1px solid rgba(255,255,255,0.15); color: rgba(255,255,255,0.7); }

.stat-card{
  background: rgba(0,0,0,0.2);
  border-radius: 16px;
  padding: 18px;
  border: 1px solid rgba(255,255,255,0.1);
  text-align: center;
  transition: all 0.3s ease;
}
.stat-card:hover{
  background: rgba(0,0,0,0.3);
  border-color: rgba(100,200,255,0.3);
  transform: translateY(-3px);
}
.stat-value{
  font-size: 28px;
  font-weight: 700;
  margin: 8px 0;
  background: linear-gradient(135deg, #4ecdc4, #45b7d1);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.stat-label{
  font-size: 12px;
  color: rgba(255,255,255,0.6);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.divider{
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), rgba(100,200,255,0.3), rgba(255,255,255,0.1), transparent);
  margin: 25px 0;
  border: none;
}
</style>
""",
    unsafe_allow_html=True,
)

# ---------------- HELPERS ----------------
def load_df(ws):
    v = ws.get_all_values()
    return pd.DataFrame(v[1:], columns=v[0])

def to_numeric(s: pd.Series) -> pd.Series:
    if pd.api.types.is_numeric_dtype(s):
        return s

    s = s.astype(str)
    s = s.replace({"": np.nan, "nan": np.nan, "None": np.nan, "NULL": np.nan})
    s = s.str.replace(",", "", regex=False)
    return pd.to_numeric(s, errors="coerce")

def detect_column_type(series: pd.Series) -> str:
    # اگر کل ستون عددی است
    if pd.api.types.is_numeric_dtype(series):
        return "numeric"

    # اگر datetime است
    if pd.api.types.is_datetime64_any_dtype(series):
        return "date"

    # تبدیل امن به string
    s = series.dropna()
    if s.empty:
        return "unknown"

    s = s.astype(str)

    # تلاش برای تاریخ
    try:
        parsed = pd.to_datetime(s, errors="coerce")
        if parsed.notna().mean() >= 0.7:
            return "date"
    except Exception:
        pass

    # تلاش برای عدد
    num = pd.to_numeric(s.str.replace(",", "", regex=False), errors="coerce")
    if num.notna().mean() >= 0.7:
        return "numeric"

    # categorical
    if s.nunique() / len(s) <= 0.3:
        return "categorical"

    return "text"


def chip_class(t: str) -> str:
    if t in ("numeric", "categorical", "text", "date", "unknown"):
        return t
    return "unknown"

def get_chart_options(x_type, y_type, libs_ok):
    # libs_ok: dict with install flags
    charts = []

    # Plotly (always available because installed with your app)
    plotly = [
        "Scatter Plot",
        "Line Chart",
        "Bar Chart",
        "Histogram",
        "Box Plot",
        "Violin Plot",
        "Heatmap",
        "Density Contour",
        "Pie Chart",
        "Sunburst Chart",
        "Treemap",
        "Scatter Matrix",
    ]
    charts += [f"Plotly Charts: {c}" for c in plotly]

    if libs_ok["altair"]:
        charts += [f"Altair Charts: {c}" for c in [
            "Altair: Scatter",
            "Altair: Bar",
            "Altair: Line",
            "Altair: Area",
            "Altair: Histogram",
        ]]

    if libs_ok["mpl"] or libs_ok["sns"]:
        # فقط وقتی نمایش بده که نصب باشد
        mpl_sns = []
        if libs_ok["mpl"]:
            mpl_sns += ["Matplotlib: Scatter"]
        if libs_ok["sns"]:
            mpl_sns += ["Seaborn: Heatmap"]
        charts += [f"Matplotlib/Seaborn: {c}" for c in mpl_sns]

    if libs_ok["scipy"]:
        charts += [f"Statistical Charts: {c}" for c in [
            "Regression Plot",
            "QQ Plot",
        ]]

    # فیلتر سازگاری با نوع ستون‌ها (برای جلوگیری از ارور)
    def ok(chart_name: str) -> bool:
        # pie/sunburst/treemap بهتر است حداقل یک categorical داشته باشد
        if any(k in chart_name for k in ["Pie Chart", "Sunburst", "Treemap"]):
            return (x_type == "categorical") or (y_type == "categorical")
        # scatter/line بهتر است y numeric باشد، یا هر دو numeric
        if any(k in chart_name for k in ["Scatter Plot", "Line Chart", "Regression Plot"]):
            return (x_type == "numeric" and y_type == "numeric")
        # box/violin خوب است یکی categorical و یکی numeric یا هر دو numeric
        if any(k in chart_name for k in ["Box Plot", "Violin Plot"]):
            return (x_type == "numeric" and y_type == "numeric") or \
                   (x_type == "categorical" and y_type == "numeric") or \
                   (x_type == "numeric" and y_type == "categorical")
        # heatmap: یا هر دو categorical (crosstab) یا هر دو numeric (density heatmap)
        if "Heatmap" in chart_name:
            return (x_type == "categorical" and y_type == "categorical") or \
                   (x_type == "numeric" and y_type == "numeric")
        # histogram: حداقل یکی numeric
        if "Histogram" in chart_name:
            return (x_type == "numeric") or (y_type == "numeric")
        # scatter matrix: فقط numeric
        if "Scatter Matrix" in chart_name:
            return (x_type == "numeric" and y_type == "numeric")
        return True

    return [c for c in charts if ok(c)]

def get_aggregation_operations(x_type, y_type, libs_ok):
    ops = ["Count", "Unique Count", "Mode"]

    if x_type == "numeric" or y_type == "numeric":
        ops += ["Sum", "Mean", "Median", "Min", "Max", "Std Deviation", "Range", "Skewness", "Kurtosis"]

    if x_type == "numeric" and y_type == "numeric":
        ops += ["Correlation"]
        if libs_ok["scipy"]:
            ops += ["Linear Regression"]

    # unique preserve
    seen, out = set(), []
    for o in ops:
        if o not in seen:
            out.append(o)
            seen.add(o)
    return out if out else ["Count"]


# ---------------- HEADER ----------------
st.markdown(
    """
<div class="glass-header">
  <div style="display:flex; align-items:center; justify-content:space-between;">
    <div>
      <h1 style="margin:0;font-size:2.6rem;background:linear-gradient(135deg,#4ecdc4,#45b7d1,#a8edea);-webkit-background-clip:text;-webkit-text-fill-color:transparent;letter-spacing:1px;">
        🔮 Advanced Data Visualization Suite
      </h1>
      <p style="color:rgba(255,255,255,0.7);margin-top:10px;font-size:1.05rem;">
        Liquid Glass UI • Safe charting (no-crash) • Works with your Google Sheet
      </p>
    </div>
    <div style="text-align:right;">
      <div style="font-size:0.9rem;color:rgba(255,255,255,0.6);margin-bottom:5px;">ENGINE STATUS</div>
      <div style="display:inline-flex;background:rgba(0,0,0,0.2);border-radius:16px;padding:8px 16px;border:1px solid rgba(255,255,255,0.1);">
        <span style="font-size:20px;margin-right:8px;">✦</span>
        <span style="color:rgba(255,255,255,0.8);">Ready</span>
      </div>
    </div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# ---------------- DATA LOADING ----------------
try:
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

    ws = client.open_by_key(sheet_id).worksheet(DATA_SHEET)
    df = load_df(ws)

    if df.empty:
        st.error("Dataset is empty.")
        st.stop()

    col_types = {c: detect_column_type(df[c]) for c in df.columns}

except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

libs_ok = {"altair": ALTair_OK, "mpl": MPL_OK, "sns": SNS_OK, "scipy": SCIPY_OK}

# ---------------- CONTROL PANEL ----------------
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown(
    """
<div style="display:flex; align-items:center; margin-bottom:16px;">
  <h3 style="margin:0;color:#a8edea;">🎛️ Control Panel</h3>
  <span class="chip chip-numeric" style="margin-left:15px;">Interactive</span>
  <span class="chip chip-categorical">Safe Mode</span>
</div>
""",
    unsafe_allow_html=True,
)

c1, c2, c3, c4 = st.columns([2, 2, 2, 1])

with c1:
    x_col = st.selectbox("X-Axis Column", df.columns, index=0)
    x_type = col_types[x_col]
    st.caption(f"Type: <span class='chip chip-{chip_class(x_type)}'>{x_type}</span>", unsafe_allow_html=True)

with c2:
    y_col = st.selectbox("Y-Axis Column", df.columns, index=min(1, len(df.columns) - 1))
    y_type = col_types[y_col]
    st.caption(f"Type: <span class='chip chip-{chip_class(y_type)}'>{y_type}</span>", unsafe_allow_html=True)

with c3:
    output_mode = st.selectbox(
        "Output Mode",
        ["Single Chart", "Chart + Table", "Chart + Statistics", "Multi-Chart Dashboard", "Full Analysis"],
        index=0,
    )

with c4:
    top_n = st.slider("Top N", 5, 100, 20)

st.markdown("</div>", unsafe_allow_html=True)

# ---------------- CHART SELECTION ----------------
st.markdown('<div class="glass-card">', unsafe_allow_html=True)

available_charts = get_chart_options(x_type, y_type, libs_ok)

# فقط کتابخانه‌های نصب شده
library_options = ["Plotly"]
if ALTair_OK:
    library_options.append("Altair")
if MPL_OK or SNS_OK:
    library_options.append("Matplotlib/Seaborn")
if SCIPY_OK:
    library_options.append("Statistical")

cc1, cc2 = st.columns(2)
with cc1:
    chart_library = st.selectbox("Chart Library", library_options, index=0)

    # فیلتر چارت‌ها برای همان کتابخانه
    if chart_library == "Plotly":
        library_charts = [c for c in available_charts if c.startswith("Plotly Charts:")]
    elif chart_library == "Altair":
        library_charts = [c for c in available_charts if c.startswith("Altair Charts:")]
    elif chart_library == "Matplotlib/Seaborn":
        library_charts = [c for c in available_charts if c.startswith("Matplotlib/Seaborn:")]
    else:
        library_charts = [c for c in available_charts if c.startswith("Statistical Charts:")]

    if not library_charts:
        # fallback امن
        library_charts = ["Plotly Charts: Scatter Plot"]

with cc2:
    selected_chart = st.selectbox(f"Select Chart Type ({len(library_charts)} available)", library_charts, index=0)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ---------------- OPERATIONS ----------------
st.markdown("<h4 style='color:#a8edea;margin-bottom:15px;'>📈 Operations</h4>", unsafe_allow_html=True)

available_ops = get_aggregation_operations(x_type, y_type, libs_ok)

g1, g2, g3 = st.columns(3)

with g1:
    st.markdown("**Basic**")
    basic_options = [op for op in ["Count", "Sum", "Mean", "Median", "Min", "Max"] if op in available_ops]
    basic_selected = st.multiselect("", basic_options, default=[op for op in ["Mean", "Median"] if op in basic_options], key="basic_ops")

with g2:
    st.markdown("**Advanced**")
    advanced_options = [op for op in ["Std Deviation", "Range", "Skewness", "Kurtosis", "Correlation"] if op in available_ops]
    advanced_selected = st.multiselect("", advanced_options, default=[], key="adv_ops")

with g3:
    st.markdown("**Tests**")
    test_options = [op for op in ["Linear Regression"] if op in available_ops]
    test_selected = st.multiselect("", test_options, default=[], key="test_ops")

selected_operations = basic_selected + advanced_selected + test_selected

o1, o2, o3 = st.columns(3)
with o1:
    apply_filters = st.checkbox("Drop missing (safe)", value=True, key="dropna_cb")
with o2:
    show_trendline = st.checkbox("Show trendline (only numeric-numeric)", value=True, key="trend_cb")
with o3:
    color_by = st.selectbox("Color By", ["None"] + [c for c in df.columns if c not in [x_col, y_col]], index=0, key="color_by")

st.markdown("</div>", unsafe_allow_html=True)

# ---------------- DATA PREP ----------------
data = df[[x_col, y_col]].copy()

if x_type == "numeric":
    data[x_col] = to_numeric(data[x_col])
if y_type == "numeric":
    data[y_col] = to_numeric(data[y_col])

if apply_filters:
    data = data.dropna(subset=[x_col, y_col])

# Limit categories
if x_type == "categorical" and data[x_col].nunique(dropna=True) > top_n:
    top_cats = data[x_col].value_counts().head(top_n).index
    data = data[data[x_col].isin(top_cats)]

if y_type == "categorical" and data[y_col].nunique(dropna=True) > top_n:
    top_cats = data[y_col].value_counts().head(top_n).index
    data = data[data[y_col].isin(top_cats)]

if data.empty:
    st.warning("No data after filtering. Change columns or disable filters.")
    st.stop()

# ---------------- CHART RENDERERS ----------------
def render_plotly(chart_name: str):
    # امن‌سازی trendline
    trend = "ols" if (show_trendline and x_type == "numeric" and y_type == "numeric") else None

    if chart_name == "Scatter Plot":
        fig = px.scatter(data, x=x_col, y=y_col, color=None if color_by == "None" else color_by, trendline=trend, title=f"{y_col} vs {x_col}")

    elif chart_name == "Line Chart":
        # فقط اگر x قابل sort باشد
        fig = px.line(data.sort_values(by=x_col), x=x_col, y=y_col, title=f"{y_col} over {x_col}")

    elif chart_name == "Bar Chart":
        if y_type == "numeric" and x_type == "categorical":
            agg = data.groupby(x_col, dropna=False)[y_col].mean().reset_index()
            fig = px.bar(agg, x=x_col, y=y_col, title=f"Mean {y_col} by {x_col}")
        else:
            counts = data[x_col].astype(str).value_counts().reset_index()
            counts.columns = [x_col, "Count"]
            fig = px.bar(counts, x=x_col, y="Count", title=f"Count of {x_col}")

    elif chart_name == "Histogram":
        target = x_col if x_type == "numeric" else y_col
        fig = px.histogram(data, x=target, title=f"Distribution of {target}")

    elif chart_name == "Box Plot":
        if x_type == "categorical" and y_type == "numeric":
            fig = px.box(data, x=x_col, y=y_col, title="Box Plot")
        elif x_type == "numeric" and y_type == "categorical":
            fig = px.box(data, x=y_col, y=x_col, title="Box Plot")
        else:
            fig = px.box(data, y=y_col, title="Box Plot")

    elif chart_name == "Violin Plot":
        if x_type == "categorical" and y_type == "numeric":
            fig = px.violin(data, x=x_col, y=y_col, box=True, title="Violin Plot")
        elif x_type == "numeric" and y_type == "categorical":
            fig = px.violin(data, x=y_col, y=x_col, box=True, title="Violin Plot")
        else:
            fig = px.violin(data, y=y_col, box=True, title="Violin Plot")

    elif chart_name == "Heatmap":
        if x_type == "categorical" and y_type == "categorical":
            ct = pd.crosstab(data[x_col].astype(str), data[y_col].astype(str))
            fig = px.imshow(ct, title=f"Heatmap: {x_col} × {y_col}", aspect="auto")
        else:
            fig = px.density_heatmap(data, x=x_col, y=y_col, title="Density Heatmap")

    elif chart_name == "Density Contour":
        fig = px.density_contour(data, x=x_col, y=y_col, title="Density Contour")

    elif chart_name == "Pie Chart":
        cat = x_col if x_type == "categorical" else y_col
        counts = data[cat].astype(str).value_counts().reset_index()
        counts.columns = [cat, "Count"]
        fig = px.pie(counts, names=cat, values="Count", title=f"Pie: {cat}")

    elif chart_name == "Sunburst Chart":
        cat = x_col if x_type == "categorical" else y_col
        counts = data[cat].astype(str).value_counts().reset_index()
        counts.columns = [cat, "Count"]
        fig = px.sunburst(counts, path=[cat], values="Count", title=f"Sunburst: {cat}")

    elif chart_name == "Treemap":
        cat = x_col if x_type == "categorical" else y_col
        counts = data[cat].astype(str).value_counts().reset_index()
        counts.columns = [cat, "Count"]
        fig = px.treemap(counts, path=[cat], values="Count", title=f"Treemap: {cat}")

    elif chart_name == "Scatter Matrix":
        # فقط وقتی هر دو numeric هستند (اینجا فقط دو ستون داریم)
        fig = px.scatter(data, x=x_col, y=y_col, title="Scatter Matrix (simplified)")

    else:
        fig = px.scatter(data, x=x_col, y=y_col, title=f"{y_col} vs {x_col}")

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        hoverlabel=dict(bgcolor="rgba(20,20,30,0.8)"),
    )
    return fig

def calculate_operations():
    results = {}
    sX = data[x_col]
    sY = data[y_col]

    for op in selected_operations:
        try:
            if op == "Count":
                results["Count(rows)"] = int(len(data))

            elif op == "Unique Count":
                results[f"Unique({x_col})"] = int(sX.nunique(dropna=True))
                results[f"Unique({y_col})"] = int(sY.nunique(dropna=True))

            elif op == "Mode":
                results[f"Mode({x_col})"] = sX.mode(dropna=True).iloc[0] if not sX.mode(dropna=True).empty else "—"
                results[f"Mode({y_col})"] = sY.mode(dropna=True).iloc[0] if not sY.mode(dropna=True).empty else "—"

            elif op in ("Sum", "Mean", "Median", "Min", "Max", "Std Deviation", "Skewness", "Kurtosis", "Range"):
                if x_type == "numeric":
                    if op == "Sum": results[f"Sum({x_col})"] = float(sX.sum())
                    if op == "Mean": results[f"Mean({x_col})"] = float(sX.mean())
                    if op == "Median": results[f"Median({x_col})"] = float(sX.median())
                    if op == "Min": results[f"Min({x_col})"] = float(sX.min())
                    if op == "Max": results[f"Max({x_col})"] = float(sX.max())
                    if op == "Std Deviation": results[f"Std({x_col})"] = float(sX.std())
                    if op == "Skewness": results[f"Skew({x_col})"] = float(sX.skew())
                    if op == "Kurtosis": results[f"Kurt({x_col})"] = float(sX.kurtosis())
                    if op == "Range": results[f"Range({x_col})"] = float(sX.max() - sX.min())

                if y_type == "numeric":
                    if op == "Sum": results[f"Sum({y_col})"] = float(sY.sum())
                    if op == "Mean": results[f"Mean({y_col})"] = float(sY.mean())
                    if op == "Median": results[f"Median({y_col})"] = float(sY.median())
                    if op == "Min": results[f"Min({y_col})"] = float(sY.min())
                    if op == "Max": results[f"Max({y_col})"] = float(sY.max())
                    if op == "Std Deviation": results[f"Std({y_col})"] = float(sY.std())
                    if op == "Skewness": results[f"Skew({y_col})"] = float(sY.skew())
                    if op == "Kurtosis": results[f"Kurt({y_col})"] = float(sY.kurtosis())
                    if op == "Range": results[f"Range({y_col})"] = float(sY.max() - sY.min())

            elif op == "Correlation":
                if x_type == "numeric" and y_type == "numeric":
                    pair = data[[x_col, y_col]].dropna()
                    results["Correlation(X,Y)"] = float(pair[x_col].corr(pair[y_col])) if len(pair) >= 2 else np.nan

            elif op == "Linear Regression":
                if SCIPY_OK and x_type == "numeric" and y_type == "numeric":
                    pair = data[[x_col, y_col]].dropna()
                    if len(pair) >= 2:
                        slope, intercept, r_value, p_value, std_err = stats.linregress(pair[x_col], pair[y_col])
                        results["Slope"] = float(slope)
                        results["Intercept"] = float(intercept)
                        results["R-squared"] = float(r_value ** 2)
                        results["P-value"] = float(p_value)
                    else:
                        results["Linear Regression"] = "Not enough data"

        except Exception as e:
            results[f"{op} (error)"] = str(e)

    return results


# ---------------- MAIN VIEW ----------------
if output_mode in ["Multi-Chart Dashboard", "Full Analysis"]:
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Main Chart", "📈 Statistics", "📋 Data Table", "🔍 Advanced"])
else:
    tab1, tab2 = st.tabs(["📊 Chart", "📈 Statistics"])

with tab1:
    st.markdown('<div class="glass-card active">', unsafe_allow_html=True)

    if selected_chart.startswith("Plotly Charts:"):
        chart_name = selected_chart.replace("Plotly Charts: ", "").strip()
        fig = render_plotly(chart_name)
        st.plotly_chart(fig, use_container_width=True, theme="streamlit")

    elif selected_chart.startswith("Altair Charts:"):
        if not ALTair_OK:
            st.warning("Altair is not installed. Install: pip install altair")
        else:
            chart_name = selected_chart.replace("Altair Charts: ", "").strip()
            # 최소 و امن: Scatter/Bar/Line
            if chart_name == "Altair: Scatter" and x_type == "numeric" and y_type == "numeric":
                ch = alt.Chart(data).mark_circle().encode(x=x_col, y=y_col, tooltip=[x_col, y_col]).interactive()
                st.altair_chart(ch, use_container_width=True)
            elif chart_name == "Altair: Bar" and x_type == "categorical" and y_type == "numeric":
                agg = data.groupby(x_col)[y_col].mean().reset_index()
                ch = alt.Chart(agg).mark_bar().encode(x=x_col, y=y_col, tooltip=[x_col, y_col]).interactive()
                st.altair_chart(ch, use_container_width=True)
            else:
                st.info("This Altair chart is not compatible with selected column types.")

    elif selected_chart.startswith("Matplotlib/Seaborn:"):
        st.warning("Matplotlib/Seaborn charts are disabled unless installed. پیشنهاد: فقط Plotly استفاده کنید.")

    elif selected_chart.startswith("Statistical Charts:"):
        st.warning("Statistical charts need SciPy installed. Install: pip install scipy")

    # Info cards
    st.markdown(
        f"""
<div style="margin-top:20px; padding:15px; background:rgba(0,0,0,0.2); border-radius:12px;">
  <div style="display:flex; justify-content:space-between; gap:12px;">
    <div><small style="color:rgba(255,255,255,0.6);">Rows</small><div style="font-size:20px;font-weight:bold;color:#4ecdc4;">{len(data):,}</div></div>
    <div><small style="color:rgba(255,255,255,0.6);">X Unique</small><div style="font-size:20px;font-weight:bold;color:#4ecdc4;">{data[x_col].nunique():,}</div></div>
    <div><small style="color:rgba(255,255,255,0.6);">Y Unique</small><div style="font-size:20px;font-weight:bold;color:#4ecdc4;">{data[y_col].nunique():,}</div></div>
    <div><small style="color:rgba(255,255,255,0.6);">Missing</small><div style="font-size:20px;font-weight:bold;color:#ff6b6b;">{int(df[[x_col,y_col]].isna().sum().sum()):,}</div></div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

    if selected_operations:
        results = calculate_operations()
        st.markdown(f"<h4 style='color:#a8edea;'>📊 Calculated Operations ({len(results)})</h4>", unsafe_allow_html=True)

        cols = st.columns(3)
        i = 0
        for k, v in results.items():
            with cols[i % 3]:
                if isinstance(v, (int, float, np.floating)) and not (pd.isna(v)):
                    show_v = f"{float(v):.4f}"
                else:
                    show_v = str(v)

                st.markdown(
                    f"""
<div class="stat-card">
  <div class="stat-label">{k}</div>
  <div class="stat-value">{show_v}</div>
</div>
""",
                    unsafe_allow_html=True,
                )
            i += 1

        # download results
        res_df = pd.DataFrame(list(results.items()), columns=["Operation", "Value"])
        st.download_button(
            "📥 Download Results",
            data=res_df.to_csv(index=False),
            file_name=f"operations_{x_col}_{y_col}.csv",
            mime="text/csv",
            type="primary",
        )
    else:
        st.info("Select operations from the control panel to see calculated statistics.")

    st.markdown("</div>", unsafe_allow_html=True)

if output_mode in ["Multi-Chart Dashboard", "Full Analysis"]:
    with tab3:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.dataframe(data.head(200), use_container_width=True, height=420)

        st.markdown("**Data Summary**")
        st.dataframe(data.describe(include="all").transpose().round(3), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab4:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        # Advanced: فقط چیزهای امن
        if x_type == "numeric":
            st.plotly_chart(px.histogram(data, x=x_col, marginal="box", title=f"Distribution of {x_col}").update_layout(template="plotly_dark"), use_container_width=True)
        if y_type == "numeric":
            st.plotly_chart(px.histogram(data, x=y_col, marginal="box", title=f"Distribution of {y_col}").update_layout(template="plotly_dark"), use_container_width=True)

        if x_type == "numeric" and y_type == "numeric":
            corr = data[[x_col, y_col]].dropna().corr()
            st.plotly_chart(px.imshow(corr, text_auto=True, aspect="auto", title="Correlation Matrix").update_layout(template="plotly_dark"), use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

# ---------------- FOOTER ----------------
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown(
    """
<div class="glass-card" style="text-align:center;padding:20px;">
  <div style="color:rgba(255,255,255,0.4);font-size:0.9rem;">
    🔮 Advanced Visualization Suite • Liquid Glass UI • No-Crash Mode
    <br>
    <span style="font-size:0.8rem;">Plotly always available • Altair/Matplotlib/Seaborn/SciPy optional</span>
  </div>
</div>
""",
    unsafe_allow_html=True,
)
