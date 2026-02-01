import streamlit as st
import pandas as pd
import google.generativeai as genai
import re
from io import BytesIO

# 1. Cấu hình ban đầu & Giao diện đồng bộ
st.set_page_config(page_title="Smart Tools Hub - Pro", layout="wide")

# --- CSS ĐỒNG BỘ GIAO DIỆN & TÙY CHỈNH UPLOADER ---
st.markdown("""
    <style>
    .stApp { background-color: #f1f5f9; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #745af2 0%, #01caf1 100%); }
    [data-testid="stSidebarNav"] ul li div a span { color: white !important; font-size: 18px !important; font-weight: bold !important; }
    
    /* Nút bấm */
    div.stButton > button { border-radius: 8px; font-weight: 600; background-color: #745af2; color: white; border: none; width: 100%; }

    /* --- TÙY CHỈNH PHẦN KÉO THẢ FILE (UPLOAD FILE) --- */
    /* Màu nền xám nhạt cho khung uploader */
    [data-testid="stFileUploader"] {
        background-color: #e2e8f0; /* Màu xám nhạt hơn */
        border-radius: 15px;
        padding: 20px;
    }

    /* Màu chữ trắng cho các dòng thông báo trong khung */
    [data-testid="stFileUploader"] section div div {
        color: white !important;
    }
    
    /* Màu icon đám mây */
    [data-testid="stFileUploader"] svg {
        fill: white !important;
    }

    /* Tùy chỉnh chữ trên nút Browse files */
    [data-testid="stFileUploader"] button {
        background-color: #745af2 !important;
        color: white !important;
    }

    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p { font-size: 16px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

if st.sidebar.button("🏠 VỀ DASHBOARD TỔNG"):
    st.switch_page("app.py")

# --- HÀM XỬ LÝ CHUẨN HÓA EXCEL CHUYÊN SÂU ---
def chuan_hoa_excel_pro(df):
    df_clean = df.copy()
    
    for col in df_clean.columns:
        col_lower = col.lower()
        
        # 1. Chuẩn hóa Họ Tên (Viết hoa chữ cái đầu, xóa khoảng trắng thừa)
        if any(kw in col_lower for kw in ['tên', 'name', 'họ']):
            df_clean[col] = df_clean[col].apply(
                lambda x: " ".join(str(x).strip().title().split()) if pd.notnull(x) and str(x).strip() != "" else x
            )
            
        # 2. Chuẩn hóa Số điện thoại (Giữ số 0 đầu)
        elif any(kw in col_lower for kw in ['sđt', 'đt', 'phone', 'tel']):
            def clean_phone(p):
                n = re.sub(r'\D', '', str(p))
                if n.startswith('84'): n = '0' + n[2:]
                elif not n.startswith('0') and len(n) > 0: n = '0' + n
                return n[-10:] if len(n) > 10 else n
            df_clean[col] = df_clean[col].astype(str).apply(clean_phone)
            
        # 3. Chuẩn hóa Ngày tháng (dd/mm/yyyy)
        elif any(kw in col_lower for kw in ['ngày', 'date', 'thời gian']):
            temp_date = pd.to_datetime(df_clean[col], errors='coerce', dayfirst=True)
            df_clean[col] = temp_date.dt.strftime('%d/%m/%Y').fillna('')

    # --- XUẤT FILE VỚI ĐỊNH DẠNG FONT & BẢNG BIỂU ---
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_clean.to_excel(writer, index=False, sheet_name='Data_Da_Chuan_Hoa')
        workbook = writer.book
        worksheet = writer.sheets['Data_Da_Chuan_Hoa']

        # Định dạng Header
        header_fmt = workbook.add_format({
            'bold': True, 'bg_color': '#745af2', 'font_color': 'white',
            'border': 1, 'font_name': 'Arial', 'align': 'center', 'valign': 'vcenter'
        })
        
        # Định dạng Nội dung (Font Arial, Kẻ bảng)
        cell_fmt = workbook.add_format({
            'border': 1, 'font_name': 'Arial', 'font_size': 11, 'valign': 'vcenter'
        })

        # Áp dụng định dạng
        for col_num, value in enumerate(df_clean.columns.values):
            worksheet.write(0, col_num, value, header_fmt)
            max_len = max(df_clean[value].astype(str).map(len).max(), len(value)) + 2
            worksheet.set_column(col_num, col_num, min(max_len, 40), cell_fmt)
            
    return output.getvalue()

# --- GIAO DIỆN ---
st.title("CHUẨN HOÁ DỮ LIỆU EXCEL")
st.divider()

tabs = st.tabs(["📊 Chuẩn hoá Excel", "📍 Tách Địa Chỉ", "👤 Tách Họ Tên", "💰 Đọc Số Tiền", "📧 Check Email"])

# --- TAB 1: CHUẨN HÓA EXCEL ---
with tabs[0]:
    st.header("📊 Chuẩn hoá Excel")
    st.info("Chức năng: Tự động chuẩn hoá họ tên, ngày tháng năm, số điện thoại. Định dạng Font Arial và kẻ bảng biểu chuyên nghiệp.")
    
    uploaded_file = st.file_uploader("Tải lên file Excel cần xử lý (.xlsx)", type=["xlsx"])
    
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        st.subheader("Xem trước dữ liệu gốc")
        st.dataframe(df.head(10), use_container_width=True)
        
        if st.button("✨ Bắt đầu Chuẩn hoá & Định dạng"):
            with st.spinner('Đang xử lý font, bảng biểu và dữ liệu...'):
                processed_data = chuan_hoa_excel_pro(df)
                st.success("✅ Đã chuẩn hoá và định dạng thành công!")
                
                st.download_button(
                    label="📥 TẢI FILE KẾT QUẢ (FONT ARIAL + BẢNG)",
                    data=processed_data,
                    file_name=f"Chuan_Hoa_{uploaded_file.name}",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

# (Các Tab khác giữ nguyên logic cũ của bạn...)
