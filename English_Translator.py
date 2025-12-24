import streamlit as st
import pandas as pd
import re
from io import BytesIO
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY", ""))

st.set_page_config(
    page_title="Dari/Pashto Translator Pro",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=JetBrains+Mono:wght@300;400&display=swap');

* {
    font-family: 'Poppins', sans-serif;
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
        rgba(100, 200, 255, 0.2), 
        rgba(255, 255, 255, 0.3), 
        rgba(255, 200, 100, 0.2));
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
        rgba(100, 200, 255, 0.3), 
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
        #ffffff 0%, #64c8ff 50%, #ffffff 100%);
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
    content: '🌐';
    font-size: 24px;
    color: #64c8ff;
    opacity: 0.9;
}

.stButton > button {
    background: linear-gradient(135deg, 
        rgba(100, 200, 255, 0.3) 0%, 
        rgba(255, 200, 100, 0.3) 100%);
    color: #ffffff;
    border: 1px solid rgba(255, 255, 255, 0.3);
    padding: 16px 36px;
    border-radius: 16px;
    font-weight: 600;
    font-size: 17px;
    transition: all 0.3s ease;
    box-shadow: 0 8px 32px rgba(100, 200, 255, 0.2);
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
    box-shadow: 0 15px 40px rgba(100, 200, 255, 0.3);
    background: linear-gradient(135deg, 
        rgba(100, 200, 255, 0.4) 0%, 
        rgba(255, 200, 100, 0.4) 100%);
}

.holographic-divider {
    height: 2px;
    background: linear-gradient(90deg, 
        transparent, 
        rgba(255, 255, 255, 0.5), 
        rgba(100, 200, 255, 0.5), 
        rgba(255, 255, 255, 0.5), 
        transparent);
    margin: 32px 0;
    border: none;
    border-radius: 2px;
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
    background: #64c8ff !important;
}

.stSuccess {
    background: rgba(100, 200, 255, 0.1) !important;
    color: #ffffff !important;
    border: 1px solid rgba(100, 200, 255, 0.3) !important;
}

.stInfo {
    background: rgba(255, 255, 255, 0.1) !important;
    color: #ffffff !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
}

.stWarning {
    background: rgba(255, 200, 100, 0.1) !important;
    color: #ffffff !important;
    border: 1px solid rgba(255, 200, 100, 0.3) !important;
}

.stError {
    background: rgba(255, 100, 100, 0.1) !important;
    color: #ffffff !important;
    border: 1px solid rgba(255, 100, 100, 0.3) !important;
}

.stSpinner > div {
    color: #64c8ff !important;
}

.stDownloadButton > button {
    background: linear-gradient(135deg, 
        rgba(100, 200, 255, 0.3) 0%, 
        rgba(255, 200, 100, 0.3) 100%) !important;
    color: #ffffff !important;
    border: 1px solid rgba(255, 255, 255, 0.3) !important;
}

.stDownloadButton > button:hover {
    background: linear-gradient(135deg, 
        rgba(100, 200, 255, 0.4) 0%, 
        rgba(255, 200, 100, 0.4) 100%) !important;
    border-color: rgba(255, 255, 255, 0.4) !important;
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
    background: rgba(100, 200, 255, 0.2);
    color: #64c8ff;
    border: 1px solid rgba(100, 200, 255, 0.3);
}

.pashto-badge {
    background: rgba(255, 200, 100, 0.2);
    color: #ffc864;
    border: 1px solid rgba(255, 200, 100, 0.3);
}

.english-badge {
    background: rgba(100, 255, 100, 0.2);
    color: #64ff64;
    border: 1px solid rgba(100, 255, 100, 0.3);
}

.preview-table {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    overflow: hidden;
}

.progress-container {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 10px;
    padding: 20px;
    margin: 20px 0;
}

.progress-bar {
    height: 10px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 5px;
    overflow: hidden;
    margin: 10px 0;
}

.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #64c8ff, #ffc864);
    border-radius: 5px;
    transition: width 0.3s ease;
}

</style>
""", unsafe_allow_html=True)

# Regex patterns for language detection
ARABIC_BLOCK_RE = re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]")
ENGLISH_RE = re.compile(r'[a-zA-Z]')

def detect_language(text):
    """Detect if text is Dari/Pashto or English"""
    if pd.isna(text) or str(text).strip() == "":
        return "empty"
    
    text_str = str(text).strip()
    
    # Check for Arabic script (Dari/Pashto)
    if ARABIC_BLOCK_RE.search(text_str):
        return "dari_pashto"
    
    # Check for English
    elif ENGLISH_RE.search(text_str):
        return "english"
    
    return "unknown"

def translate_text(text, model="gpt-4.1-mini"):
    """Translate Dari/Pashto text to English using OpenAI"""
    if pd.isna(text) or str(text).strip() == "":
        return text
    
    text_str = str(text).strip()
    
    # Check if it's already English
    if detect_language(text_str) == "english":
        return text_str
    
    try:
        prompt = f"""
        Detect the language of this text (Dari, Pashto, or English).
        If the text is Dari or Pashto, translate it into simple, human, non-native English.
        Do NOT normalize or paraphrase. Keep the meaning exactly as is.
        If the text is already in English, return it as is.
        
        Text to translate:
        "{text_str}"
        
        Translation:
        """
        
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=500
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        st.error(f"Translation error: {str(e)}")
        return text_str

def create_translation_sheet(df, original_col, translated_col, key_col=None):
    """Create a separate sheet with key, old value, new value format"""
    translation_data = []
    
    for idx, row in df.iterrows():
        key_value = ""
        if key_col and key_col in df.columns:
            key_value = str(row[key_col]) if not pd.isna(row[key_col]) else f"ROW_{idx+1:04d}"
        else:
            key_value = f"ROW_{idx+1:04d}"
        
        original = str(row[original_col]) if not pd.isna(row[original_col]) else ""
        translated = str(row[translated_col]) if not pd.isna(row[translated_col]) else ""
        
        if original.strip():  # Only add if there's original content
            translation_data.append({
                "Key": key_value,
                "Original_Value": original,
                "Translated_Value": translated
            })
    
    return pd.DataFrame(translation_data)

def main():
    # Header
    st.markdown("""
    <div class="crystal-panel">
        <div style="text-align: center; margin-bottom: 10px;">
            <h1 class="neon-glow" style="font-size: 48px; margin: 0; color: #ffffff;">🌐 DARI/PASHTO TRANSLATOR PRO</h1>
            <p style="color: rgba(255, 255, 255, 0.9); font-size: 18px; margin-top: 10px;">
                AI-Powered Translation Engine for Dari & Pashto Datasets
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # API Key Check
    if not st.secrets.get("OPENAI_API_KEY"):
        st.error("⚠️ OpenAI API Key is not configured. Please add it to your Streamlit secrets.")
        st.stop()
    
    # Stats Grid
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
            <div style="color: rgba(255, 255, 255, 0.7); font-size: 12px;">AI Processed</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="holographic-divider"></div>', unsafe_allow_html=True)
    
    # File Upload Section
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
            <p style="color: rgba(255, 255, 255, 0.8);">Upload your dataset to begin Dari/Pashto to English translation</p>
        </div>
        """, unsafe_allow_html=True)
        st.stop()
    
    # Read Dataset
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, dtype=str, keep_default_na=False)
        else:
            df = pd.read_excel(uploaded_file, dtype=str, keep_default_na=False)
    except Exception as e:
        st.error(f"❌ Error reading file: {str(e)}")
        st.stop()
    
    # Update stats
    st.markdown(f"""
    <script>
    document.getElementById('total-rows').textContent = '{len(df):,}';
    document.getElementById('total-columns').textContent = '{len(df.columns)}';
    </script>
    """, unsafe_allow_html=True)
    
    # Data Preview
    st.markdown('<div class="quantum-card"><div class="section-title">👁️ DATA PREVIEW</div>', unsafe_allow_html=True)
    st.dataframe(df.head(10), use_container_width=True, height=300)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Translation Settings
    st.markdown('<div class="quantum-card"><div class="section-title">⚙️ TRANSLATION SETTINGS</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Column selection
        column_to_translate = st.selectbox(
            "📝 SELECT COLUMN TO TRANSLATE",
            options=df.columns,
            help="Choose the column containing Dari/Pashto text"
        )
        
        # Key column selection
        key_column = st.selectbox(
            "🔑 SELECT KEY COLUMN (Optional)",
            options=["None"] + list(df.columns),
            help="Column to use as identifier in translation sheet"
        )
        if key_column == "None":
            key_column = None
        
        # Language detection preview
        st.markdown("---")
        st.markdown("### 🔍 Language Detection")
        sample_text = df[column_to_translate].iloc[0] if len(df) > 0 else ""
        if str(sample_text).strip():
            lang = detect_language(sample_text)
            if lang == "dari_pashto":
                st.markdown(f'<span class="language-badge dari-badge">Dari/Pashto Detected</span>', unsafe_allow_html=True)
            elif lang == "english":
                st.markdown(f'<span class="language-badge english-badge">English Detected</span>', unsafe_allow_html=True)
            else:
                st.markdown(f'<span class="language-badge">Unknown Language</span>', unsafe_allow_html=True)
    
    with col2:
        # Model selection
        model = st.selectbox(
            "🤖 SELECT AI MODEL",
            options=["gpt-4.1-mini", "gpt-3.5-turbo", "gpt-4"],
            help="Choose the OpenAI model for translation"
        )
        
        # Export options
        st.markdown("### 📥 EXPORT OPTIONS")
        export_option = st.radio(
            "Choose export format:",
            options=["Replace Original Values", "Add as New Column"],
            help="Replace original values or add translations as new column"
        )
        
        # Translation batch size
        batch_size = st.slider(
            "📊 BATCH SIZE",
            min_value=1,
            max_value=100,
            value=10,
            help="Number of rows to translate at once"
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Start Translation Button
    st.markdown('<div class="holographic-divider"></div>', unsafe_allow_html=True)
    
    if st.button("🚀 START TRANSLATION PROCESS", type="primary", use_container_width=True):
        if not column_to_translate:
            st.warning("Please select a column to translate")
            st.stop()
        
        # Create progress tracker
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Count Dari/Pashto rows
        dari_pashto_rows = 0
        for val in df[column_to_translate]:
            if detect_language(val) == "dari_pashto":
                dari_pashto_rows += 1
        
        st.markdown(f"""
        <div class="progress-container">
            <p style="color: #ffffff; margin-bottom: 10px;">
                📊 <b>Translation Summary:</b>
            </p>
            <p style="color: rgba(255, 255, 255, 0.8);">
                Total Rows: {len(df):,}<br>
                Dari/Pashto Rows to Translate: {dari_pashto_rows:,}<br>
                English/Empty Rows: {len(df) - dari_pashto_rows:,}
            </p>
            <div class="progress-bar">
                <div class="progress-fill" style="width: 0%"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Initialize translation column
        translated_col_name = f"{column_to_translate}_EN"
        df[translated_col_name] = ""
        
        # Perform translation in batches
        total_translated = 0
        for i in range(0, len(df), batch_size):
            batch = df.iloc[i:i+batch_size]
            
            for idx, row in batch.iterrows():
                original_text = row[column_to_translate]
                
                # Update progress
                progress = (i + idx - i + 1) / len(df)
                progress_bar.progress(progress)
                status_text.text(f"Translating row {idx+1} of {len(df)}...")
                
                # Translate if needed
                if detect_language(original_text) == "dari_pashto":
                    translated = translate_text(original_text, model)
                    df.at[idx, translated_col_name] = translated
                    total_translated += 1
                else:
                    df.at[idx, translated_col_name] = str(original_text)
            
            # Update stats dynamically
            st.markdown(f"""
            <script>
            document.getElementById('total-translations').textContent = '{total_translated:,}';
            </script>
            """, unsafe_allow_html=True)
        
        progress_bar.progress(1.0)
        status_text.text(f"✅ Translation completed! {total_translated} rows translated.")
        
        # Apply export option
        if export_option == "Replace Original Values":
            df[column_to_translate] = df[translated_col_name]
            df = df.drop(columns=[translated_col_name])
            translated_col_name = column_to_translate
        
        st.success(f"🎉 Translation completed successfully! {total_translated} Dari/Pashto texts translated to English.")
        
        # Show Results
        st.markdown('<div class="quantum-card"><div class="section-title">📋 TRANSLATION RESULTS</div>', unsafe_allow_html=True)
        
        # Create preview dataframe with both versions
        preview_df = df[[column_to_translate]].copy()
        if translated_col_name != column_to_translate:
            preview_df[translated_col_name] = df[translated_col_name]
        
        st.dataframe(preview_df.head(20), use_container_width=True, height=400)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Export Section
        st.markdown('<div class="quantum-card"><div class="section-title">📥 EXPORT TRANSLATIONS</div>', unsafe_allow_html=True)
        
        col_exp1, col_exp2 = st.columns(2)
        
        with col_exp1:
            st.markdown("### 📊 Complete Dataset")
            st.markdown("""
            <div class="insight-content" style="margin-bottom: 20px;">
                <p>Export the entire dataset with translations applied.</p>
                <p><b>Format:</b> Original dataset with translations</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Create complete dataset export
            output_complete = BytesIO()
            with pd.ExcelWriter(output_complete, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Translated_Data', index=False)
            
            safe_name = re.sub(r'[^a-zA-Z0-9_-]+', '_', uploaded_file.name.rsplit('.', 1)[0])
            
            st.download_button(
                label="💾 DOWNLOAD COMPLETE DATASET",
                data=output_complete.getvalue(),
                file_name=f"translated_{safe_name}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        with col_exp2:
            st.markdown("### 📄 Translation Sheet")
            st.markdown("""
            <div class="insight-content" style="margin-bottom: 20px;">
                <p>Export only the translations in a clean format.</p>
                <p><b>Format:</b> Key, Old Value, New Value</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Create translation sheet
            translation_df = create_translation_sheet(
                df, 
                column_to_translate, 
                translated_col_name if translated_col_name != column_to_translate else column_to_translate,
                key_column
            )
            
            output_translation = BytesIO()
            with pd.ExcelWriter(output_translation, engine='openpyxl') as writer:
                translation_df.to_excel(writer, sheet_name='Translation_Log', index=False)
                
                # Add summary sheet
                summary_data = pd.DataFrame({
                    'Metric': ['Total Rows', 'Translated Rows', 'Source Column', 'Key Column'],
                    'Value': [len(df), total_translated, column_to_translate, key_column or 'Auto-generated']
                })
                summary_data.to_excel(writer, sheet_name='Summary', index=False)
            
            st.download_button(
                label="📝 DOWNLOAD TRANSLATION SHEET",
                data=output_translation.getvalue(),
                file_name=f"translation_log_{safe_name}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div style="text-align: center; margin-top: 40px; color: rgba(255, 255, 255, 0.6); font-size: 12px;">
        <div style="margin-bottom: 10px; color: rgba(255, 255, 255, 0.7);">⚡ Powered by OpenAI GPT & Streamlit</div>
        <div style="color: rgba(255, 255, 255, 0.6);">© 2025 Dari/Pashto Translator Pro • v3.0</div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
