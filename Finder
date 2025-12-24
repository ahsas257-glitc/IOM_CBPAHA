import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

st.set_page_config(
    page_title="Entry Column Detector",
    page_icon="🔍",
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
        #0f172a 0%, 
        #1e293b 25%, 
        #0f172a 50%, 
        #1e293b 75%, 
        #0f172a 100%);
    background-size: 400% 400%;
    animation: gradientBG 20s ease infinite;
    min-height: 100vh;
}

@keyframes gradientBG {
    0% { background-position: 0% 50% }
    50% { background-position: 100% 50% }
    100% { background-position: 0% 50% }
}

.main-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

.glass-panel {
    background: rgba(255, 255, 255, 0.07);
    backdrop-filter: blur(15px);
    border-radius: 20px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    padding: 30px;
    margin-bottom: 25px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    transition: transform 0.3s ease;
}

.glass-panel:hover {
    transform: translateY(-2px);
    border-color: rgba(255, 255, 255, 0.2);
}

.title-section {
    text-align: center;
    margin-bottom: 30px;
}

.main-title {
    font-size: 42px;
    font-weight: 700;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 10px;
}

.subtitle {
    color: #cbd5e1;
    font-size: 18px;
    margin-bottom: 20px;
}

.stats-card {
    display: flex;
    justify-content: space-around;
    margin: 30px 0;
}

.stat-item {
    text-align: center;
    padding: 20px;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 15px;
    min-width: 200px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.stat-value {
    font-size: 36px;
    font-weight: 700;
    color: #60a5fa;
    margin: 10px 0;
}

.stat-label {
    color: #94a3b8;
    font-size: 14px;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.column-type {
    display: inline-block;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    margin-left: 10px;
}

.choice-column {
    background: rgba(34, 197, 94, 0.2);
    color: #22c55e;
    border: 1px solid rgba(34, 197, 94, 0.3);
}

.entry-column {
    background: rgba(239, 68, 68, 0.2);
    color: #ef4444;
    border: 1px solid rgba(239, 68, 68, 0.3);
}

.mixed-column {
    background: rgba(245, 158, 11, 0.2);
    color: #f59e0b;
    border: 1px solid rgba(245, 158, 11, 0.3);
}

.data-table {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.table-header {
    background: rgba(255, 255, 255, 0.1);
    padding: 15px;
    font-weight: 600;
    color: #ffffff;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.stButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 12px 30px;
    border-radius: 12px;
    font-weight: 600;
    transition: all 0.3s ease;
    width: 100%;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
}

.download-section {
    display: flex;
    gap: 15px;
    margin-top: 20px;
}

.download-btn {
    flex: 1;
}

.sample-data {
    background: rgba(255, 255, 255, 0.03);
    border-radius: 10px;
    padding: 15px;
    margin-top: 15px;
    border-left: 4px solid #667eea;
}

.insight-box {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 15px;
    padding: 20px;
    margin: 15px 0;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.insight-title {
    color: #60a5fa;
    font-weight: 600;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 10px;
}

.insight-content {
    color: #cbd5e1;
    line-height: 1.6;
}

.highlight {
    background: rgba(96, 165, 250, 0.2);
    padding: 2px 6px;
    border-radius: 4px;
    color: #60a5fa;
    font-weight: 500;
}

.stSelectbox > div > div,
.stMultiselect > div > div,
.stTextInput > div > div > input {
    background: rgba(255, 255, 255, 0.08) !important;
    color: #ffffff !important;
    border-color: rgba(255, 255, 255, 0.2) !important;
}

.stCheckbox > label {
    color: #cbd5e1 !important;
}

.stDataFrame {
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 10px !important;
}

</style>
""", unsafe_allow_html=True)

def detect_column_type(column_data, sample_size=100):
    """
    تشخیص نوع ستون: چویس (Choice) یا انتری (Entry)
    
    معیارهای تشخیص:
    1. ستون‌های Choice: مقادیر محدود و تکراری
    2. ستون‌های Entry: مقادیر متنوع و منحصربه‌فرد
    3. ستون‌های Mixed: ترکیبی از هر دو
    """
    # نمونه‌گیری از داده‌ها
    sample = column_data.dropna().head(sample_size)
    if len(sample) == 0:
        return "Empty", 0, 0
    
    # تبدیل به رشته برای پردازش
    sample_str = sample.astype(str).str.strip()
    
    # محاسبه تعداد مقادیر منحصربه‌فرد
    unique_count = sample_str.nunique()
    total_count = len(sample_str)
    
    # محاسبه درصد تکرار
    unique_ratio = unique_count / total_count if total_count > 0 else 0
    
    # محاسبه طول متوسط متن
    avg_length = sample_str.str.len().mean()
    
    # بررسی وجود کلمات کلیدی ریزن/دلایل
    reason_keywords = ['reason', 'ریزن', 'دلایل', 'توضیح', 'شرح', 'explain', 'comment', 'نظر', 'سایر']
    contains_reason = any(keyword in str(column_data.name).lower() for keyword in reason_keywords)
    
    # تشخیص نوع ستون
    if unique_ratio <= 0.3 and avg_length < 50:
        # تعداد مقادیر منحصربه‌فرد کم و متن کوتاه = Choice
        return "Choice", unique_count, total_count
    elif unique_ratio >= 0.7 or avg_length > 100 or contains_reason:
        # مقادیر متنوع یا متن طولانی یا شامل کلمات کلیدی = Entry
        return "Entry", unique_count, total_count
    else:
        # حالت بینابینی
        return "Mixed", unique_count, total_count

def analyze_dataset(df):
    """آنالیز کامل دیتاست و تشخیص ستون‌های Entry"""
    results = []
    
    for column in df.columns:
        column_data = df[column]
        col_type, unique_count, total_count = detect_column_type(column_data)
        
        # نمونه‌ای از داده‌ها برای نمایش
        sample_values = column_data.dropna().head(5).tolist()
        
        # استخراج کلمات کلیدی از نام ستون
        column_lower = str(column).lower()
        
        results.append({
            'Column Name': column,
            'Type': col_type,
            'Unique Values': unique_count,
            'Total Values': total_count,
            'Uniqueness Ratio': f"{(unique_count/max(total_count, 1))*100:.1f}%",
            'Sample Values': str(sample_values[:3]) if sample_values else "No Data",
            'Contains Reason Keywords': any(keyword in column_lower for keyword in 
                                         ['reason', 'ریزن', 'دلایل', 'توضیح', 'شرح'])
        })
    
    results_df = pd.DataFrame(results)
    
    # محاسبه آمار کلی
    total_columns = len(results_df)
    entry_columns = len(results_df[results_df['Type'] == 'Entry'])
    choice_columns = len(results_df[results_df['Type'] == 'Choice'])
    mixed_columns = len(results_df[results_df['Type'] == 'Mixed'])
    
    # شناسایی ستون‌های با اولویت بالا برای انتری
    high_priority = []
    for idx, row in results_df.iterrows():
        if row['Type'] == 'Entry' and row['Contains Reason Keywords']:
            high_priority.append(row['Column Name'])
    
    return results_df, {
        'total_columns': total_columns,
        'entry_columns': entry_columns,
        'choice_columns': choice_columns,
        'mixed_columns': mixed_columns,
        'high_priority_entries': high_priority
    }

def create_summary_report(results_df, stats):
    """ایجاد گزارش خلاصه"""
    report = f"""
# 📊 گزارش تحلیل ستون‌های دیتاست

## 📈 آمار کلی
- **تعداد کل ستون‌ها:** {stats['total_columns']}
- **ستون‌های Choice (چویس):** {stats['choice_columns']} ({stats['choice_columns']/max(stats['total_columns'], 1)*100:.1f}%)
- **ستون‌های Entry (نیاز به انتری):** {stats['entry_columns']} ({stats['entry_columns']/max(stats['total_columns'], 1)*100:.1f}%)
- **ستون‌های Mixed (ترکیبی):** {stats['mixed_columns']} ({stats['mixed_columns']/max(stats['total_columns'], 1)*100:.1f}%)

## 🎯 ستون‌های با اولویت بالا برای انتری
"""
    
    if stats['high_priority_entries']:
        for col in stats['high_priority_entries']:
            report += f"- **{col}** (شامل کلمات کلیدی ریزن/دلایل)\n"
    else:
        report += "❌ هیچ ستون با اولویت بالا یافت نشد\n"
    
    report += "\n## 🔍 توصیه‌ها\n"
    
    if stats['entry_columns'] > stats['choice_columns']:
        report += "⚠️ این دیتاست بیشتر شامل سوالات باز (Entry) است. نیاز به زمان بیشتری برای انتری دارد.\n"
    else:
        report += "✅ این دیتاست بیشتر شامل سوالات بسته (Choice) است. روند انتری سریع‌تر خواهد بود.\n"
    
    return report

def main():
    st.markdown("""
    <div class="title-section">
        <h1 class="main-title">🔍 Entry Column Detector</h1>
        <p class="subtitle">شناسایی ستون‌های نیازمند انتری در دیتاست‌های نظرسنجی</p>
    </div>
    """, unsafe_allow_html=True)
    
    # آپلود فایل
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    st.markdown('<h3 style="color: #ffffff; margin-bottom: 20px;">📁 آپلود دیتاست</h3>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "فایل Excel یا CSV خود را آپلود کنید",
        type=["xlsx", "xls", "csv"],
        help="فایل نظرسنجی حاوی سوالات Choice و Entry را آپلود کنید"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    if not uploaded_file:
        st.info("👈 لطفاً فایل دیتاست خود را آپلود کنید")
        return
    
    # خواندن فایل
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"خطا در خواندن فایل: {str(e)}")
        return
    
    # نمایش پیش‌نمایش داده
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    st.markdown('<h3 style="color: #ffffff; margin-bottom: 20px;">👁️ پیش‌نمایش داده</h3>', unsafe_allow_html=True)
    st.dataframe(df.head(), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # آنالیز دیتاست
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    st.markdown('<h3 style="color: #ffffff; margin-bottom: 20px;">⚙️ تحلیل ستون‌ها</h3>', unsafe_allow_html=True)
    
    if st.button("🚀 شروع تحلیل", use_container_width=True):
        with st.spinner("در حال تحلیل ستون‌ها..."):
            results_df, stats = analyze_dataset(df)
            
            # نمایش آمار
            st.markdown('<div class="stats-card">', unsafe_allow_html=True)
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="stat-item">
                    <div class="stat-value">{stats['total_columns']}</div>
                    <div class="stat-label">کل ستون‌ها</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="stat-item">
                    <div class="stat-value" style="color: #22c55e;">{stats['choice_columns']}</div>
                    <div class="stat-label">ستون‌های Choice</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="stat-item">
                    <div class="stat-value" style="color: #ef4444;">{stats['entry_columns']}</div>
                    <div class="stat-label">ستون‌های Entry</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="stat-item">
                    <div class="stat-value" style="color: #f59e0b;">{stats['mixed_columns']}</div>
                    <div class="stat-label">ستون‌های Mixed</div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # نمایش جدول نتایج
            st.markdown('<h4 style="color: #ffffff; margin: 20px 0;">📋 نتایج تحلیل</h4>', unsafe_allow_html=True)
            
            # ایجاد یک کپی از DataFrame برای نمایش با فرمت بهتر
            display_df = results_df.copy()
            
            # افزودن استایل به ستون Type
            def color_column_type(val):
                if val == 'Choice':
                    return 'color: #22c55e; font-weight: bold;'
                elif val == 'Entry':
                    return 'color: #ef4444; font-weight: bold;'
                else:
                    return 'color: #f59e0b; font-weight: bold;'
            
            styled_df = display_df.style.applymap(color_column_type, subset=['Type'])
            st.dataframe(styled_df, use_container_width=True, height=400)
            
            # نمایش بینش‌ها
            st.markdown('<div class="insight-box">', unsafe_allow_html=True)
            st.markdown('<div class="insight-title">💡 بینش‌های تحلیل</div>', unsafe_allow_html=True)
            
            if stats['high_priority_entries']:
                st.markdown(f"""
                <div class="insight-content">
                <p>🎯 <span class="highlight">{len(stats['high_priority_entries'])} ستون با اولویت بالا</span> شناسایی شد که احتمالاً نیاز به انتری ریزن/دلایل دارند:</p>
                <ul>
                """, unsafe_allow_html=True)
                for col in stats['high_priority_entries']:
                    st.markdown(f"<li><b>{col}</b></li>", unsafe_allow_html=True)
                st.markdown("</ul></div>", unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="insight-content">
                <p>ℹ️ هیچ ستونی با کلمات کلیدی ریزن/دلایل شناسایی نشد. برای شناسایی دقیق‌تر ستون‌های Entry، به نمونه داده‌ها دقت کنید.</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # دانلود نتایج
            st.markdown('<div class="insight-box">', unsafe_allow_html=True)
            st.markdown('<div class="insight-title">📥 دانلود نتایج</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # دانلود به صورت Excel
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    results_df.to_excel(writer, sheet_name='Column Analysis', index=False)
                    
                    # ایجاد گزارش خلاصه
                    summary_df = pd.DataFrame([{
                        'Metric': 'Total Columns',
                        'Value': stats['total_columns']
                    }, {
                        'Metric': 'Choice Columns',
                        'Value': stats['choice_columns']
                    }, {
                        'Metric': 'Entry Columns',
                        'Value': stats['entry_columns']
                    }, {
                        'Metric': 'Mixed Columns',
                        'Value': stats['mixed_columns']
                    }])
                    summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                st.download_button(
                    label="📊 دانلود نتایج (Excel)",
                    data=output.getvalue(),
                    file_name="column_analysis.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            
            with col2:
                # دانلود گزارش متنی
                report_text = create_summary_report(results_df, stats)
                st.download_button(
                    label="📄 دانلود گزارش (Text)",
                    data=report_text.encode('utf-8'),
                    file_name="analysis_report.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # راهنمای استفاده
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    st.markdown('<h3 style="color: #ffffff; margin-bottom: 15px;">📖 راهنمای استفاده</h3>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="insight-content">
    <h4>🎯 انواع ستون‌ها:</h4>
    <p><span class="highlight">Choice (چویس)</span>: سوالات چندگزینه‌ای با پاسخ‌های محدود</p>
    <p><span class="highlight">Entry (انتری)</span>: سوالات باز که نیاز به وارد کردن متن دارند</p>
    <p><span class="highlight">Mixed (ترکیبی)</span>: ترکیبی از پاسخ‌های Choice و Entry</p>
    
    <h4>🔍 معیارهای تشخیص:</h4>
    <ul>
    <li>تعداد مقادیر منحصربه‌فرد</li>
    <li>طول متوسط پاسخ‌ها</li>
    <li>وجود کلمات کلیدی مانند: ریزن، دلایل، توضیح، نظر</li>
    <li>نوع داده و فرمت ستون</li>
    </ul>
    
    <h4>💡 نکات مهم:</h4>
    <ul>
    <li>ستون‌های با کلمه "ریزن" یا "دلایل" اولویت بالاتری دارند</li>
    <li>ستون‌های Entry نیاز به زمان بیشتری برای وارد کردن داده دارند</li>
    <li>برای دقت بیشتر، نمونه داده‌های هر ستون را بررسی کنید</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
