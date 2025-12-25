import streamlit as st
import pandas as pd
import re
import time
from io import BytesIO
from deep_translator import GoogleTranslator, MyMemoryTranslator

# ---------------------------
# Page config
# ---------------------------
st.set_page_config(
    page_title="Dari/Pashto Translator Pro (FREE)",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------------------
# CSS
# ---------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=JetBrains+Mono:wght@300;400&display=swap');
* { font-family: 'Poppins', sans-serif; }
.stApp {
    background: linear-gradient(135deg,#0a0f1a 0%,#121828 25%,#1a1a2e 50%,#16213e 75%,#0a0f1a 100%);
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
    text-shadow: 0 0 10px rgba(255,255,255,0.3),0 0 20px rgba(255,255,255,0.2),0 0 30px rgba(255,255,255,0.1);
}
.crystal-panel {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(25px) saturate(180%);
    -webkit-backdrop-filter: blur(25px) saturate(180%);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 28px;
    padding: 28px 34px;
    margin-bottom: 30px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.5),
                inset 0 1px 0 rgba(255,255,255,0.1),
                inset 0 -1px 0 rgba(0,0,0,0.5);
    position: relative;
    overflow: hidden;
}
.quantum-card {
    background: linear-gradient(145deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.04) 100%);
    backdrop-filter: blur(20px) saturate(160%);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 24px;
    padding: 24px 28px;
    margin-bottom: 24px;
}
.stats-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
    margin: 25px 0;
}
.neon-stat {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 20px;
    padding: 22px;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.stat-number {
    font-size: 42px;
    font-weight: 700;
    background: linear-gradient(135deg,#ffffff 0%,#64c8ff 50%,#ffffff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 10px 0;
    font-family: 'JetBrains Mono', monospace;
}
.stat-label {
    font-size: 14px;
    color: rgba(255,255,255,0.9);
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
    content: '🌐';
    font-size: 24px;
    color: #64c8ff;
    opacity: 0.9;
}
.holographic-divider {
    height: 2px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.5), rgba(100,200,255,0.5), rgba(255,255,255,0.5), transparent);
    margin: 32px 0;
    border: none;
    border-radius: 2px;
}
.language-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    margin-left: 10px;
}
.dari-badge {
    background: rgba(100,200,255,0.2);
    color: #64c8ff;
    border: 1px solid rgba(100,200,255,0.3);
}
.english-badge {
    background: rgba(100,255,100,0.2);
    color: #64ff64;
    border: 1px solid rgba(100,255,100,0.3);
}
.stButton > button, .stDownloadButton > button {
    background: linear-gradient(135deg, rgba(100,200,255,0.3) 0%, rgba(255,200,100,0.3) 100%) !important;
    color: #ffffff !important;
    border: 1px solid rgba(255,255,255,0.3) !important;
    padding: 16px 36px !important;
    border-radius: 16px !important;
    font-weight: 600 !important;
    font-size: 17px !important;
    width: 100% !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# Language detection regex
# ---------------------------
ARABIC_BLOCK_RE = re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]")
ENGLISH_RE = re.compile(r'[a-zA-Z]')

def detect_language(text):
    if pd.isna(text) or str(text).strip() == "":
        return "empty"
    s = str(text).strip()
    if ARABIC_BLOCK_RE.search(s):
        return "dari_pashto"
    if ENGLISH_RE.search(s):
        return "english"
    return "unknown"

# ---------------------------
# Do-not-translate protect/restore
# ---------------------------
def protect_phrases(text: str, phrases):
    token_map = {}
    protected = text
    for i, p in enumerate(sorted(phrases, key=len, reverse=True)):
        token = f"__DNT_{i}__"
        if p and p in protected:
            protected = protected.replace(p, token)
            token_map[token] = p
    return protected, token_map

def restore_phrases(text: str, token_map):
    restored = text
    for token, phrase in token_map.items():
        restored = restored.replace(token, phrase)
    return restored

# ---------------------------
# Heuristic: name/place vs sentence
# ---------------------------
def looks_like_name_or_place(s: str) -> bool:
    s = (s or "").strip()
    if not s:
        return False
    if len(s) > 40:
        return False
    if any(x in s for x in [".", "؟", "?", "!", "؛", ";", ":", "،", ","]):
        return False
    if len(s.split()) >= 6:
        return False
    return True

# ---------------------------
# Transliteration (Arabic script -> Latin)
# ---------------------------
AR2LAT = {
    "ا": "a", "آ": "a", "أ": "a", "إ": "e", "ء": "",
    "ب": "b", "پ": "p", "ت": "t", "ث": "s",
    "ج": "j", "چ": "ch", "ح": "h", "خ": "kh",
    "د": "d", "ذ": "z", "ر": "r", "ز": "z", "ژ": "zh",
    "س": "s", "ش": "sh", "ص": "s", "ض": "z",
    "ط": "t", "ظ": "z", "ع": "", "غ": "gh",
    "ف": "f", "ق": "q", "ک": "k", "گ": "g",
    "ل": "l", "م": "m", "ن": "n",
    "ه": "h", "ۀ": "a", "ة": "a",
    "و": "w", "ؤ": "o", "ی": "y", "ئ": "e", "ى": "a",
    "ځ": "dz", "څ": "ts", "ښ": "kh", "ڼ": "n", "ږ": "gh", "ډ": "d", "ټ": "t", "ړ": "r",
    "َ": "", "ُ": "", "ِ": "", "ّ": "", "ْ": "", "ً": "", "ٌ": "", "ٍ": "",
    "‌": " ", "ـ": "",
}

def transliterate_arabic_to_latin(text: str) -> str:
    if text is None:
        return ""
    s = str(text).strip()
    if not s:
        return s
    if detect_language(s) == "english":
        return s

    out = []
    for ch in s:
        out.append(AR2LAT.get(ch, ch))
    roman = "".join(out)
    roman = re.sub(r"\s+", " ", roman).strip()
    return roman

# ---------------------------
# Chunking + caching + robust translate
# ---------------------------
def chunk_text(s: str, max_len: int = 4500):
    s = s.strip()
    if len(s) <= max_len:
        return [s]

    parts = re.split(r"(\n+)", s)
    chunks, buf = [], ""
    for part in parts:
        if len(buf) + len(part) <= max_len:
            buf += part
        else:
            if buf.strip():
                chunks.append(buf)
            buf = part
    if buf.strip():
        chunks.append(buf)

    final = []
    for c in chunks:
        if len(c) <= max_len:
            final.append(c)
        else:
            for i in range(0, len(c), max_len):
                final.append(c[i:i+max_len])
    return final

@st.cache_data(show_spinner=False)
def cached_translate(provider: str, text: str, target: str = "en") -> str:
    if provider == "google":
        return GoogleTranslator(source="auto", target=target).translate(text)
    return MyMemoryTranslator(source="auto", target=target).translate(text)

def robust_translate(text: str, target: str, provider_order, retries=3, sleep_base=0.6) -> str:
    for provider in provider_order:
        for attempt in range(retries):
            try:
                chunks = chunk_text(text, max_len=4500)
                out = []
                for ch in chunks:
                    time.sleep(0.15)
                    out.append(cached_translate(provider, ch, target=target))
                return "".join(out).strip()
            except Exception:
                time.sleep(sleep_base * (2 ** attempt))
    return text

def translate_text(text, target="en", provider_order=None):
    if pd.isna(text) or str(text).strip() == "":
        return str(text) if not pd.isna(text) else ""
    s = str(text).strip()

    lang = detect_language(s)
    if lang == "english":
        return s
    if lang != "dari_pashto":
        return s

    if provider_order is None:
        provider_order = ["google", "mymemory"]

    return robust_translate(s, target=target, provider_order=provider_order)

# ---------------------------
# Export translation sheet
# ---------------------------
def create_translation_sheet(df, original_col, translated_col, key_col=None):
    translation_data = []
    for idx, row in df.iterrows():
        if key_col and key_col in df.columns and str(row.get(key_col, "")).strip():
            key_value = str(row[key_col]).strip()
        else:
            key_value = f"ROW_{idx+1:04d}"

        original = str(row.get(original_col, "") or "").strip()
        translated = str(row.get(translated_col, "") or "").strip()

        if original:
            translation_data.append({
                "Key": key_value,
                "Original_Value": original,
                "Translated_Value": translated
            })
    return pd.DataFrame(translation_data)

# ---------------------------
# UI App
# ---------------------------
def main():
    st.markdown("""
    <div class="crystal-panel">
        <div style="text-align: center; margin-bottom: 10px;">
            <h1 class="neon-glow" style="font-size: 46px; margin: 0; color: #ffffff;">🌐 DARI/PASHTO TRANSLATOR PRO</h1>
            <p style="color: rgba(255, 255, 255, 0.9); font-size: 18px; margin-top: 10px;">
                FREE Translators (Google + MyMemory Fallback) + Transliteration (Names/Places)
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="stats-grid">
        <div class="neon-stat">
            <div class="stat-label">Dataset Rows</div>
            <div class="stat-number" id="total-rows">0</div>
            <div style="color: rgba(255, 255, 255, 0.7); font-size: 12px;">Data Points</div>
        </div>
        <div class="neon-stat">
            <div class="stat-label">Columns</div>
            <div class="stat-number" id="total-columns">0</div>
            <div style="color: rgba(255, 255, 255, 0.7); font-size: 12px;">Data Fields</div>
        </div>
        <div class="neon-stat">
            <div class="stat-label">Translations</div>
            <div class="stat-number" id="total-translations">0</div>
            <div style="color: rgba(255, 255, 255, 0.7); font-size: 12px;">Processed</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="holographic-divider"></div>', unsafe_allow_html=True)

    st.markdown('<div class="quantum-card"><div class="section-title">📤 UPLOAD DATASET</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Drag & Drop or Click to Upload Excel/CSV File",
        type=["xlsx", "xls", "csv"],
        label_visibility="collapsed",
        key="file_uploader"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    if not uploaded_file:
        st.markdown("""
        <div style="text-align: center; padding: 60px; color: rgba(255, 255, 255, 0.8);">
            <div style="font-size: 64px; margin-bottom: 20px;">📊</div>
            <h3 style="color: #ffffff;">Ready for Translation</h3>
            <p style="color: rgba(255, 255, 255, 0.8);">Upload your dataset to begin Dari/Pashto processing</p>
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    try:
        if uploaded_file.name.lower().endswith(".csv"):
            df = pd.read_csv(uploaded_file, dtype=str, keep_default_na=False)
        else:
            df = pd.read_excel(uploaded_file, dtype=str, keep_default_na=False)
    except Exception as e:
        st.error(f"❌ Error reading file: {str(e)}")
        st.stop()

    st.markdown(f"""
    <script>
    document.getElementById('total-rows').textContent = '{len(df):,}';
    document.getElementById('total-columns').textContent = '{len(df.columns)}';
    </script>
    """, unsafe_allow_html=True)

    st.markdown('<div class="quantum-card"><div class="section-title">👁️ DATA PREVIEW</div>', unsafe_allow_html=True)
    st.dataframe(df.head(10), use_container_width=True, height=300)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="quantum-card"><div class="section-title">⚙️ TRANSLATION SETTINGS</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        column_to_translate = st.selectbox(
            "📝 SELECT COLUMN TO PROCESS",
            options=list(df.columns),
            help="Choose the column containing Dari/Pashto text (or names/places)"
        )

        key_column = st.selectbox(
            "🔑 SELECT KEY COLUMN (Optional)",
            options=["None"] + list(df.columns),
            help="Column to use as identifier in translation sheet"
        )
        if key_column == "None":
            key_column = None

        st.markdown("---")
        st.markdown("### 🔍 Language Detection (Sample)")
        sample_text = df[column_to_translate].iloc[0] if len(df) > 0 else ""
        if str(sample_text).strip():
            lang = detect_language(sample_text)
            if lang == "dari_pashto":
                st.markdown('<span class="language-badge dari-badge">Dari/Pashto Detected</span>', unsafe_allow_html=True)
            elif lang == "english":
                st.markdown('<span class="language-badge english-badge">English Detected</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span class="language-badge">Unknown Language</span>', unsafe_allow_html=True)

    with col2:
        st.markdown("### ✨ Output Mode")
        output_mode = st.selectbox(
            "How should the selected column be processed?",
            options=[
                "Translate to English (meaning)",
                "Transliterate only (Romanize names/places)",
                "Auto (Names -> Transliterate, Sentences -> Translate)"
            ],
            help="Use Transliterate for beneficiary names, province/district/village names."
        )

        st.markdown("### 🆓 Free Translator Providers")
        provider_mode = st.selectbox(
            "Choose provider strategy:",
            options=[
                "Google (Best quality, may rate-limit)",
                "Google + MyMemory fallback (Recommended)",
                "MyMemory only (Most stable free, sometimes weaker)"
            ],
            help="Fallback helps if Google temporarily blocks."
        )

        if provider_mode == "Google (Best quality, may rate-limit)":
            provider_order = ["google"]
        elif provider_mode == "MyMemory only (Most stable free, sometimes weaker)":
            provider_order = ["mymemory"]
        else:
            provider_order = ["google", "mymemory"]

        st.markdown("### 🛑 Do Not Translate (keep as-is)")
        dnt_text = st.text_area(
            "Enter words/phrases (one per line) that should NEVER be translated (e.g., province/village names):",
            value="",
            height=130
        )
        do_not_translate_list = [x.strip() for x in dnt_text.splitlines() if x.strip()]

        st.markdown("### 📥 EXPORT OPTIONS")
        export_option = st.radio(
            "Choose export format:",
            options=["Replace Original Values", "Add as New Column"],
            help="Replace original values or add results as new column"
        )

        batch_size = st.slider(
            "📊 BATCH SIZE",
            min_value=1,
            max_value=100,
            value=10,
            help="Smaller batch = less blocking risk."
        )

        delay_ms = st.slider(
            "⏱️ Delay per row (ms)",
            min_value=0,
            max_value=1500,
            value=150,
            step=50,
            help="Higher delay = more stable, slower."
        )

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="holographic-divider"></div>', unsafe_allow_html=True)

    if st.button("🚀 START PROCESS", type="primary", use_container_width=True):
        progress_bar = st.progress(0)
        status_text = st.empty()

        need_count = sum(1 for v in df[column_to_translate] if detect_language(v) == "dari_pashto")

        st.info(
            f"Total Rows: {len(df):,} | "
            f"Dari/Pashto rows: {need_count:,} | "
            f"English/Empty/Other: {len(df) - need_count:,}"
        )

        result_col_name = f"{column_to_translate}_OUT"
        df[result_col_name] = ""

        total_processed = 0

        for i in range(0, len(df), batch_size):
            batch = df.iloc[i:i + batch_size]

            for idx, row in batch.iterrows():
                original_text = str(row.get(column_to_translate, "") or "").strip()

                progress_bar.progress((idx + 1) / len(df))
                status_text.text(f"Processing row {idx+1} of {len(df)}...")

                if delay_ms > 0:
                    time.sleep(delay_ms / 1000.0)

                # Always keep phrases unchanged (for translation mode)
                protected_text, token_map = protect_phrases(original_text, do_not_translate_list)

                if output_mode == "Transliterate only (Romanize names/places)":
                    result = transliterate_arabic_to_latin(original_text)

                elif output_mode == "Auto (Names -> Transliterate, Sentences -> Translate)":
                    if detect_language(original_text) == "dari_pashto" and looks_like_name_or_place(original_text):
                        result = transliterate_arabic_to_latin(original_text)
                    else:
                        result = translate_text(protected_text, target="en", provider_order=provider_order)
                        result = restore_phrases(result, token_map)

                else:
                    # Translate meaning
                    result = translate_text(protected_text, target="en", provider_order=provider_order)
                    result = restore_phrases(result, token_map)

                df.at[idx, result_col_name] = result
                total_processed += 1

            st.markdown(f"""
            <script>
            document.getElementById('total-translations').textContent = '{total_processed:,}';
            </script>
            """, unsafe_allow_html=True)

        progress_bar.progress(1.0)
        status_text.text(f"✅ Completed! {total_processed} rows processed.")

        if export_option == "Replace Original Values":
            df[column_to_translate] = df[result_col_name]
            df.drop(columns=[result_col_name], inplace=True)
            result_col_name = column_to_translate

        st.success(f"🎉 Done! {total_processed} rows processed successfully.")

        st.markdown('<div class="quantum-card"><div class="section-title">📋 RESULTS PREVIEW</div>', unsafe_allow_html=True)
        preview_cols = [column_to_translate]
        if result_col_name != column_to_translate and result_col_name in df.columns:
            preview_cols.append(result_col_name)
        st.dataframe(df[preview_cols].head(20), use_container_width=True, height=400)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="quantum-card"><div class="section-title">📥 EXPORT</div>', unsafe_allow_html=True)
        col_exp1, col_exp2 = st.columns(2)

        safe_name = re.sub(r'[^a-zA-Z0-9_-]+', '_', uploaded_file.name.rsplit('.', 1)[0])

        with col_exp1:
            st.markdown("### 📊 Complete Dataset")
            output_complete = BytesIO()
            with pd.ExcelWriter(output_complete, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Processed_Data', index=False)

            st.download_button(
                label="💾 DOWNLOAD COMPLETE DATASET",
                data=output_complete.getvalue(),
                file_name=f"processed_{safe_name}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

        with col_exp2:
            st.markdown("### 📄 Output Sheet (Log)")
            src_col = column_to_translate
            dst_col = result_col_name if result_col_name in df.columns else column_to_translate

            log_df = create_translation_sheet(df, src_col, dst_col, key_column)

            output_log = BytesIO()
            with pd.ExcelWriter(output_log, engine='openpyxl') as writer:
                log_df.to_excel(writer, sheet_name='Output_Log', index=False)
                summary_data = pd.DataFrame({
                    'Metric': ['Total Rows', 'Processed Rows', 'Source Column', 'Key Column', 'Provider Strategy', 'Output Mode'],
                    'Value': [len(df), total_processed, src_col, key_column or 'Auto-generated', provider_mode, output_mode]
                })
                summary_data.to_excel(writer, sheet_name='Summary', index=False)

            st.download_button(
                label="📝 DOWNLOAD OUTPUT SHEET",
                data=output_log.getvalue(),
                file_name=f"output_log_{safe_name}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align: center; margin-top: 40px; color: rgba(255, 255, 255, 0.6); font-size: 12px;">
        <div style="margin-bottom: 10px; color: rgba(255, 255, 255, 0.7);">⚡ Powered by Streamlit + Free Translators</div>
        <div style="color: rgba(255, 255, 255, 0.6);">© 2025 Dari/Pashto Translator Pro • FREE Edition</div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
