import streamlit as st
import pandas as pd
import google.generativeai as genai
import re
from io import BytesIO
import docx
import PyPDF2

# 1. Cấu hình ban đầu
st.set_page_config(page_title="Smart Tools Hub - Pro", layout="wide")

# CSS Tùy chỉnh Giao diện (Xám nhạt cho Uploader, Chữ trắng)
st.markdown("""
    <style>
    .stApp { background-color: #f1f5f9; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #745af2 0%, #01caf1 100%); }
    [data-testid="stSidebarNav"] ul li div a span { color: white !important; font-size: 18px !important; font-weight: bold !important; }
    div.stButton > button { border-radius: 8px; font-weight: 600; background-color: #745af2; color: white; border: none; width: 100%; }

    /* KHUNG UPLOAD FILE MÀU XÁM NHẠT + CHỮ TRẮNG */
    [data-testid="stFileUploader"] {
        background-color: #bdc3c7 !important;
        border: 2px dashed #ffffff;
        border-radius: 10px;
        padding: 10px;
    }
    [data-testid="stFileUploader"] section div div { color: white !important; }
    [data-testid="stFileUploader"] svg { fill: white !important; }
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p { font-size: 16px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# Kết nối AI từ Secrets
if "GEMINI_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("Chưa cấu hình API Key trong Secrets!")
    st.stop()

if st.sidebar.button("🏠 VỀ DASHBOARD TỔNG"):
    st.switch_page("app.py")

# --- CÁC HÀM XỬ LÝ DỮ LIỆU ---

def read_file_content(uploaded_file):
    if uploaded_file is None: return ""
    suffix = uploaded_file.name.split('.')[-1].lower()
    if suffix == 'txt': return str(uploaded_file.read(), "utf-8")
    elif suffix in ['doc', 'docx']:
        doc = docx.Document(uploaded_file)
        return "\n".join([para.text for para in doc.paragraphs])
    elif suffix == 'pdf':
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        return "".join([page.extract_text() for page in pdf_reader.pages])
    elif suffix in ['xlsx', 'xls']:
        return pd.read_excel(uploaded_file).to_string()
    return ""

def chuan_hoa_excel_pro(df):
    df_clean = df.copy()
    for col in df_clean.columns:
        col_lower = col.lower()
        if any(kw in col_lower for kw in ['tên', 'name', 'họ']):
            df_clean[col] = df_clean[col].apply(lambda x: " ".join(str(x).strip().title().split()) if pd.notnull(x) else x)
        elif any(kw in col_lower for kw in ['sđt', 'đt', 'phone', 'tel']):
            def clean_phone(p):
                n = re.sub(r'\D', '', str(p))
                if n.startswith('84'): n = '0' + n[2:]
                elif not n.startswith('0') and len(n) > 0: n = '0' + n
                return n[-10:] if len(n) > 10 else n
            df_clean[col] = df_clean[col].astype(str).apply(clean_phone)
        elif any(kw in col_lower for kw in ['ngày', 'date']):
            temp_date = pd.to_datetime(df_clean[col], errors='coerce', dayfirst=True)
            df_clean[col] = temp_date.dt.strftime('%d/%m/%Y').fillna('')

    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_clean.to_excel(writer, index=False, sheet_name='Data_Da_Chuan_Hoa')
        workbook = writer.book
        header_fmt = workbook.add_format({'bold': True, 'bg_color': '#745af2', 'font_color': 'white', 'border': 1, 'font_name': 'Arial'})
        cell_fmt = workbook.add_format({'border': 1, 'font_name': 'Arial', 'font_size': 11})
        for col_num, value in enumerate(df_clean.columns.values):
            writer.sheets['Data_Da_Chuan_Hoa'].write(0, col_num, value, header_fmt)
            writer.sheets['Data_Da_Chuan_Hoa'].set_column(col_num, col_num, 20, cell_fmt)
    return output.getvalue()

# --- GIAO DIỆN CHÍNH ---
st.title("🚀 SMART TOOLS HUB - EXCEL PRO")
st.divider()

tabs = st.tabs(["📊 Chuẩn hoá Excel", "🔍 So sánh văn bản", "👤 Tách Họ Tên", "💰 Đọc Số Tiền", "📧 Check Email"])

# TAB 1: CHUẨN HOÁ EXCEL
with tabs[0]:
    st.header("📊 Chuẩn hoá Dữ liệu Excel")
    st.info("Chức năng: Sửa Họ tên, Ngày tháng, SĐT. Định dạng Font Arial + Kẻ bảng tự động.")
    uploaded_file = st.file_uploader("Kéo và thả file Excel vào đây", type=["xlsx"], key="excel_main")
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        st.dataframe(df.head(10), use_container_width=True)
        if st.button("✨ BẮT ĐẦU CHUẨN HOÁ", key="btn_excel"):
            res = chuan_hoa_excel_pro(df)
            st.success("✅ Đã hoàn thành!")
            st.download_button("📥 TẢI FILE KẾT QUẢ", res, f"Cleaned_{uploaded_file.name}")

# TAB 2: SO SÁNH VĂN BẢN (PDF, DOC, EXCEL...)
with tabs[1]:
    st.header("🔍 So Sánh Tài Liệu Thông Minh")
    st.info("So sánh nội dung giữa 2 file bất kỳ. AI sẽ chỉ ra các thay đổi.")
    c1, c2 = st.columns(2)
    with c1: f_a = st.file_uploader("Tài liệu Gốc (A)", type=["pdf", "docx", "txt", "xlsx"], key="fa")
    with c2: f_b = st.file_uploader("Tài liệu Mới (B)", type=["pdf", "docx", "txt", "xlsx"], key="fb")
    
    if st.button("🚀 BẮT ĐẦU ĐỐI CHIẾU"):
        if f_a and f_b:
            with st.spinner('AI đang phân tích...'):
                t_a, t_b = read_file_content(f_a), read_file_content(f_b)
                prompt = f"So sánh Bản A và Bản B. Liệt kê điểm khác biệt:\nBản A: {t_a[:2500]}\nBản B: {t_b[:2500]}"
                st.markdown(model.generate_content(prompt).text)
        else:
            st.warning("Vui lòng tải đủ 2 file!")

# (Các Tab 3, 4, 5 có thể thêm logic tương tự tùy nhu cầu)
