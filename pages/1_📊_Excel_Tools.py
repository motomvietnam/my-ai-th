import streamlit as st
import pandas as pd
import google.generativeai as genai
import re
from io import BytesIO

# 1. Cấu hình ban đầu & Giao diện đồng bộ
st.set_page_config(page_title="Tinh chỉnh file excel", layout="wide")

# --- CSS ĐỒNG BỘ GIAO DIỆN ---
st.markdown("""
    <style>
    /* Nền tổng thể */
    .stApp { background-color: #f1f5f9; }
    
    /* --- TÙY CHỈNH SIDEBAR BÊN TRÁI --- */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #745af2 0%, #01caf1 100%);
    }
    
    /* Cỡ chữ, màu sắc và độ đậm của Menu Sidebar */
    [data-testid="stSidebarNav"] ul li div a span {
        color: white !important;
        font-size: 18px !important;
        font-weight: bold !important;
    }
    
    /* Hiệu ứng khi di chuột qua menu bên trái */
    [data-testid="stSidebarNav"] ul li div:hover {
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }

    /* Tùy chỉnh các nút bấm */
    div.stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: 0.2s;
        background-color: #745af2;
        color: white;
        border: none;
    }
    
    div.stButton > button:hover {
        background-color: #5a44c7;
        color: white;
        border: none;
    }

    /* Tab header chỉnh lại cho rõ ràng */
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 18px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# Nút quay lại Dashboard nhanh trên Sidebar
if st.sidebar.button("🏠 VỀ DASHBOARD TỔNG"):
    st.switch_page("app.py")

# Kết nối AI
if "GEMINI_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("Chưa cấu hình API Key trong Secrets!")
    st.stop()

# 2. Hàm xử lý dữ liệu
def hieu_chinh_excel(df):
    df_clean = df.copy()

    for col in df_clean.columns:
        col_lower = col.lower()
        
        # A. Chuẩn hóa Họ Tên
        if any(keyword in col_lower for keyword in ['tên', 'name', 'ho ten']):
            df_clean[col] = df_clean[col].apply(
                lambda x: " ".join(str(x).strip().title().split()) if pd.notnull(x) and str(x).strip() != "" else x
            )
        
        # B. Chuẩn hóa Số điện thoại
        elif any(keyword in col_lower for keyword in ['sđt', 'điện thoại', 'phone', 'tel']):
            def clean_p(p):
                if pd.isnull(p) or str(p).strip() == "" or str(p).lower() == "nan": return ""
                n = re.sub(r'\D', '', str(p)) 
                
                if n.startswith('84'): 
                    n = '0' + n[2:]
                elif not n.startswith('0') and len(n) > 0:
                    n = '0' + n
                
                if len(n) > 10: 
                    return n[-10:]
                return n
            
            df_clean[col] = df_clean[col].astype(str).apply(clean_p)
            
        # C. Chuẩn hóa Ngày tháng
        elif any(keyword in col_lower for keyword in ['ngày', 'date']):
            temp_date = pd.to_datetime(df_clean[col], errors='coerce', dayfirst=True)
            df_clean[col] = temp_date.dt.strftime('%d/%m/%Y').fillna('')

    # --- TẠO FILE EXCEL ---
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_clean.to_excel(writer, index=False, sheet_name='Data')
        workbook  = writer.book
        worksheet = writer.sheets['Data']

        fmt_header = workbook.add_format({'bold': True, 'bg_color': '#1e3a8a', 'font_color': 'white', 'border': 1, 'font_name': 'Arial', 'align': 'center'})
        text_format = workbook.add_format({'border': 1, 'font_name': 'Arial', 'num_format': '@'})

        for col_num, value in enumerate(df_clean.columns.values):
            worksheet.write(0, col_num, value, fmt_header)
            max_len = max(df_clean[value].astype(str).map(len).max(), len(value)) + 2
            worksheet.set_column(col_num, col_num, min(max_len, 50), text_format)
            
    return output.getvalue()

# 3. Giao diện Chính
st.title("🚀 SMART TOOLS HUB")
st.markdown("### Công cụ Hiệu chỉnh Dữ liệu & AI Marketing")
st.divider()

tab1, tab2 = st.tabs(["📊 Hiệu chỉnh Excel", "🤖 AI Content"])

with tab1:
    st.info("Tải file Excel (xlsx) để tự động sửa lỗi họ tên, thêm số 0 vào SĐT và định dạng ngày tháng.")
    file = st.file_uploader("Chọn file Excel từ máy tính", type=["xlsx"])
    if file:
        df = pd.read_excel(file)
        st.dataframe
