import streamlit as st
import pandas as pd
import re
from io import BytesIO
import docx
import PyPDF2
import difflib
import zipfile
from docxtpl import DocxTemplate

# 1. CẤU HÌNH GIAO DIỆN & CSS TĂNG ĐỘ ĐẬM
st.set_page_config(page_title="Smart Tools Hub - Pro", layout="wide")

st.markdown("""
    <style>
    /* Nền tổng thể và Sidebar */
    .stApp { background-color: #f1f5f9; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #745af2 0%, #01caf1 100%); }
    [data-testid="stSidebarNav"] ul li div a span { color: white !important; font-size: 18px !important; font-weight: bold !important; }
    
    /* Nút bấm */
    div.stButton > button { border-radius: 8px; font-weight: bold; background-color: #745af2; color: white; border: none; width: 100%; }

    /* Khung Upload File */
    [data-testid="stFileUploader"] {
        background-color: #bdc3c7 !important;
        border: 2px dashed #ffffff;
        border-radius: 10px;
        padding: 10px;
    }

    /* --- TỐI ƯU ĐỘ ĐẬM CHO BẢNG NHẬP LIỆU --- */
    /* 1. Chữ trong các ô (Cells) */
    [data-testid="stDataEditor"] div[data-testid="stTable"] td, 
    [data-testid="stDataEditor"] input {
        color: #000000 !important;
        font-weight: 700 !important; /* Tăng lên Bold */
        font-size: 15px !important;
    }
    
    /* 2. Tiêu đề cột (Column Headers) */
    [data-testid="stDataEditor"] div[role="columnheader"] p {
        color: #000000 !important;
        font-weight: 900 !important; /* Siêu đậm */
        font-size: 16px !important;
        text-transform: uppercase;
    }

    /* 3. Tab menu */
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p { font-size: 16px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- CÁC HÀM HỖ TRỢ ---
def doc_so_thanh_chu_logic(so_tien_str):
    # Hàm xử lý giả định, bạn có thể thay bằng logic đọc số của bạn
    return f"Đã đọc: {so_tien_str}"

# --- HÀM TẠO FILE EXCEL MẪU ---
def tạo_excel_mẫu():
    cột_mẫu = ["So", "Ten", "ChucVu", "Luong", "TenKhach", "TenSuKien", "ThoiGian", "DiaDiem", "NgayCap", "LuongMoi", "LuongCu", "NgayHieuLuc", "MaNV", "Phongban"]
    data_mẫu = [["01", "Nguyễn Văn A", "Trưởng phòng", "20.000.000", "Lê Văn B", "Hội nghị", "08:00", "Hà Nội", "01/01", "25M", "20M", "15/02", "NV01", "Kế toán"]]
    df_mẫu = pd.DataFrame(data_mẫu, columns=cột_mẫu)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_mẫu.to_excel(writer, index=False, sheet_name='Mau')
    return output.getvalue()

# --- KHỞI TẠO BIẾN DỮ LIỆU ---
cột_yêu_cầu = ["So", "Ten", "ChucVu", "Luong", "TenKhach", "TenSuKien", "ThoiGian", "DiaDiem", "NgayCap", "LuongMoi", "LuongCu", "NgayHieuLuc", "MaNV", "Phongban"]
if 'df_merge' not in st.session_state:
    st.session_state.df_merge = pd.DataFrame(columns=cột_yêu_cầu)

# --- GIAO DIỆN TAB ---
tabs = st.tabs(["📊 Chuẩn hoá Excel", "🔍 So sánh đối soát", "🎭 Mail Merge (Trộn file)", "💰 Đọc Số Tiền", "📧 Check Email"])

with tabs[2]:
    st.header("🎭 Trộn Hồ Sơ & Hợp Đồng Chuyên Nghiệp")
    
    col_guide, col_download = st.columns([2, 1])
    with col_guide:
        st.markdown("**Hướng dẫn:** Tải file mẫu bên phải, nhập liệu rồi dán vào bảng dưới.")
    
    with col_download:
        st.download_button("📥 TẢI FILE EXCEL MẪU", tạo_excel_mẫu(), "Mau_SmartTools.xlsx", use_container_width=True)

    st.divider()

    c1, c2 = st.columns(2)
    with c1:
        word_template = st.file_uploader("📂 Tải file Word mẫu", type=["docx"], key="w_tpl")
    with c2:
        st.info("💡 **Mẹo:** Nhấn vào bảng rồi ấn **Ctrl + V** để dán dữ liệu từ Excel.")

    # Cấu hình bảng với tiêu đề đậm và chữ đen
    config = {col: st.column_config.TextColumn(label=col, width="medium", required=True) for col in cột_yêu_cầu}

    edited_df = st.data_editor(
        st.session_state.df_merge, 
        num_rows="dynamic", 
        use_container_width=True,
        column_config=config,
        key="pro_editor_high_contrast"
    )

    if st.button("🚀 XUẤT HÀNG LOẠT (.ZIP)", use_container_width=True):
        if word_template and not edited_df.empty:
            try:
                zip_buffer = BytesIO()
                with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                    for index, row in edited_df.iterrows():
                        doc = DocxTemplate(word_template)
                        context = row.to_dict()
                        if "LuongMoi" in context and context["LuongMoi"]:
                            context["LuongMoiChu"] = doc_so_thanh_chu_logic(context["LuongMoi"])
                        doc.render(context)
                        out_word = BytesIO()
                        doc.save(out_word)
                        fname = str(row.get('Ten', f'File_{index}')).replace(' ', '_')
                        zip_file.writestr(f"{fname}.docx", out_word.getvalue())
                
                st.success(f"✅ Đã xử lý {len(edited_df)} tài liệu!")
                st.download_button("📥 TẢI KẾT QUẢ (.ZIP)", zip_buffer.getvalue(), "Ket_Qua.zip")
            except Exception as e:
                st.error(f"❌ Lỗi: {e}")
