import streamlit as st
import pandas as pd
import re
from io import BytesIO
import docx
import PyPDF2
import difflib

# 1. CẤU HÌNH GIAO DIỆN
st.set_page_config(page_title="Smart Tools Hub - Pro", layout="wide")

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

if st.sidebar.button("🏠 VỀ DASHBOARD TỔNG"):
    st.switch_page("app.py")

# --- HÀM XỬ LÝ ĐỌC FILE ---
def read_file_content(uploaded_file):
    if uploaded_file is None: return ""
    try:
        suffix = uploaded_file.name.split('.')[-1].lower()
        if suffix == 'txt': 
            return str(uploaded_file.read(), "utf-8")
        elif suffix in ['doc', 'docx']:
            doc = docx.Document(uploaded_file)
            return "\n".join([para.text for para in doc.paragraphs])
        elif suffix == 'pdf':
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        elif suffix in ['xlsx', 'xls']:
            df = pd.read_excel(uploaded_file)
            return df.to_string()
    except Exception as e:
        return f"Lỗi đọc file: {e}"
    return ""

# --- HÀM CHUẨN HÓA EXCEL ---
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
        df_clean.to_excel(writer, index=False, sheet_name='Clean_Data')
        workbook = writer.book
        header_fmt = workbook.add_format({'bold': True, 'bg_color': '#745af2', 'font_color': 'white', 'border': 1, 'font_name': 'Arial', 'align': 'center'})
        cell_fmt = workbook.add_format({'border': 1, 'font_name': 'Arial', 'font_size': 11})
        for col_num, value in enumerate(df_clean.columns.values):
            writer.sheets['Clean_Data'].write(0, col_num, value, header_fmt)
            writer.sheets['Clean_Data'].set_column(col_num, col_num, 25, cell_fmt)
    return output.getvalue()

# --- GIAO DIỆN CHÍNH ---
st.title("🚀 SMART TOOLS HUB - EXCEL & DOC PRO")
st.divider()

tabs = st.tabs(["📊 Chuẩn hoá Excel", "🔍 So sánh đối soát", "👤 Tách Họ Tên", "💰 Đọc Số Tiền", "📧 Check Email"])

# TAB 1: CHUẨN HÓA EXCEL
with tabs[0]:
    st.header("📊 Chuẩn hoá Dữ liệu Excel")
    file_ex = st.file_uploader("Kéo thả file Excel tại đây", type=["xlsx"], key="excel_tab")
    if file_ex:
        df = pd.read_excel(file_ex)
        st.subheader("Dữ liệu gốc")
        st.dataframe(df.head(10), use_container_width=True)
        if st.button("✨ BẮT ĐẦU CHUẨN HOÁ", key="btn_clean"):
            with st.spinner("Đang xử lý..."):
                res = chuan_hoa_excel_pro(df)
                st.success("✅ Đã hoàn thành chuẩn hóa!")
                st.download_button("📥 TẢI FILE EXCEL SẠCH", res, f"Cleaned_{file_ex.name}")

# TAB 2: SO SÁNH VĂN BẢN (KHÔNG DÙNG AI)
with tabs[1]:
    st.header("🔍 Đối Soát Văn Bản Offline")
    st.info("So sánh từng dòng giữa 2 file. Dòng xanh (+) là mới, dòng đỏ (-) là bị xóa.")
    c1, c2 = st.columns(2)
    with c1: f_a = st.file_uploader("Bản Gốc (A)", type=["pdf", "docx", "txt", "xlsx"], key="fa_pure")
    with c2: f_b = st.file_uploader("Bản Mới (B)", type=["pdf", "docx", "txt", "xlsx"], key="fb_pure")
    
    if st.button("🚀 BẮT ĐẦU SO SÁNH", key="btn_compare"):
        if f_a and f_b:
            with st.spinner('Đang đối soát dữ liệu...'):
                t_a = read_file_content(f_a)
                t_b = read_file_content(f_b)
                
                diff = list(difflib.Differ().compare(t_a.splitlines(), t_b.splitlines()))
                
                st.subheader("Kết quả chi tiết:")
                has_diff = False
                for line in diff:
                    if line.startswith('+ '):
                        st.markdown(f"🟢 **Thêm:** `{line[2:]}`")
                        has_diff = True
                    elif line.startswith('- '):
                        st.markdown(f"🔴 **Xóa:** ~~{line[2:]}~~")
                        has_diff = True
                
                if not has_diff:
                    st.success("✅ Hai tài liệu nội dung giống hệt nhau!")
        else:
            st.warning("Vui lòng tải đủ 2 bản A và B!")

with tabs[2]: st.write("Chức năng đang phát triển...")
with tabs[3]: st.write("Chức năng đang phát triển...")
with tabs[4]: st.write("Chức năng đang phát triển...")
