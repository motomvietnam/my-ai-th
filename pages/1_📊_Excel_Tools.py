import streamlit as st
import pandas as pd
import re
from io import BytesIO
import docx
import PyPDF2
import difflib
import zipfile
from docxtpl import DocxTemplate

# 1. CẤU HÌNH GIAO DIỆN
st.set_page_config(page_title="Smart Tools Hub - Pro", layout="wide")

st.markdown("""
    <style>
    /* 1. Nền tổng thể và Sidebar */
    .stApp { background-color: #f1f5f9; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #745af2 0%, #01caf1 100%); }
    [data-testid="stSidebarNav"] ul li div a span { color: white !important; font-size: 18px !important; font-weight: bold !important; }
    
    /* 2. Nút bấm */
    div.stButton > button { border-radius: 8px; font-weight: 600; background-color: #745af2; color: white; border: none; width: 100%; }

    /* 3. Khung Upload File (Giữ màu trắng cho tiêu đề để nổi trên nền xám) */
    [data-testid="stFileUploader"] {
        background-color: #bdc3c7 !important;
        border: 2px dashed #ffffff;
        border-radius: 10px;
        padding: 10px;
    }
    [data-testid="stFileUploader"] section div div { color: white !important; }
    [data-testid="stFileUploader"] svg { fill: white !important; }

    /* 4. CHỮ TRONG BẢNG NHẬP LIỆU (Ép màu đen đậm) */
    /* Màu chữ trong các ô */
    [data-testid="stDataEditor"] div[data-testid="stTable"] td, 
    [data-testid="stDataEditor"] input {
        color: #000000 !important;
        font-weight: 500 !important;
    }
    /* Màu chữ tiêu đề cột trong bảng */
    [data-testid="stDataEditor"] div[role="columnheader"] p {
        color: #000000 !important;
        font-weight: bold !important;
    }

    /* 5. Tab menu */
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p { font-size: 16px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

if st.sidebar.button("🏠 VỀ DASHBOARD TỔNG"):
    st.switch_page("app.py")

# --- CÁC HÀM HỖ TRỢ ---
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
            text = "".join([page.extract_text() for page in pdf_reader.pages])
            return text
        elif suffix in ['xlsx', 'xls']:
            df = pd.read_excel(uploaded_file)
            return df.to_string()
    except Exception as e:
        return f"Lỗi đọc file: {e}"
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

tabs = st.tabs(["📊 Chuẩn hoá Excel", "🔍 So sánh đối soát", "🎭 Mail Merge (Trộn file)", "💰 Đọc Số Tiền", "📧 Check Email"])

# --- TAB 1: CHUẨN HÓA EXCEL ---
with tabs[0]:
    st.header("📊 Chuẩn hoá Dữ liệu Excel")
    file_ex = st.file_uploader("Kéo thả file Excel tại đây", type=["xlsx"], key="excel_tab")
    if file_ex:
        df = pd.read_excel(file_ex)
        st.dataframe(df.head(10), use_container_width=True)
        if st.button("✨ BẮT ĐẦU CHUẨN HOÁ", key="btn_clean"):
            with st.spinner("Đang xử lý..."):
                res = chuan_hoa_excel_pro(df)
                st.success("✅ Thành công!")
                st.download_button("📥 TẢI FILE EXCEL SẠCH", res, f"Cleaned_{file_ex.name}")

# --- TAB 2: SO SÁNH VĂN BẢN ---
with tabs[1]:
    st.header("🔍 Đối Soát Văn Bản Offline")
    c1, c2 = st.columns(2)
    with c1: f_a = st.file_uploader("Bản Gốc (A)", type=["pdf", "docx", "txt", "xlsx"], key="fa")
    with c2: f_b = st.file_uploader("Bản Mới (B)", type=["pdf", "docx", "txt", "xlsx"], key="fb")
    
    if st.button("🚀 BẮT ĐẦU SO SÁNH"):
        if f_a and f_b:
            t_a, t_b = read_file_content(f_a), read_file_content(f_b)
            diff = list(difflib.Differ().compare(t_a.splitlines(), t_b.splitlines()))
            for line in diff:
                if line.startswith('+ '): st.markdown(f"🟢 **Thêm:** `{line[2:]}`")
                elif line.startswith('- '): st.markdown(f"🔴 **Xóa:** ~~{line[2:]}~~")
        else: st.warning("Vui lòng tải đủ 2 bản!")

# --- HÀM TẠO FILE EXCEL MẪU ---
def tạo_excel_mẫu():
    # Danh sách các cột theo ảnh bạn gửi
    cột_mẫu = [
        "So", "Ten", "ChucVu", "Luong", "TenKhach", "TenSuKien", 
        "ThoiGian", "DiaDiem", "NgayCap", "LuongMoi", "LuongCu", 
        "NgayHieuLuc", "MaNV", "Phongban"
    ]
    
    # Dữ liệu mẫu ban đầu
    data_mẫu = [
        ["01", "Nguyễn Văn A", "Trưởng phòng", "20.000.000", "Lê Văn B", "Hội nghị khách hàng", 
         "08:00 01/02/2026", "Hà Nội", "01/01/2026", "25.000.000", "20.000.000", 
         "15/02/2026", "NV001", "Kinh doanh"]
    ]
    
    df_mẫu = pd.DataFrame(data_mẫu, columns=cột_mẫu)
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_mẫu.to_excel(writer, index=False, sheet_name='Mau_Nhap_Lieu')
        # Định dạng một chút cho đẹp
        workbook = writer.book
        header_fmt = workbook.add_format({'bold': True, 'bg_color': '#2ecc71', 'font_color': 'white', 'border': 1})
        for col_num, value in enumerate(df_mẫu.columns.values):
            writer.sheets['Mau_Nhap_Lieu'].write(0, col_num, value, header_fmt)
            writer.sheets['Mau_Nhap_Lieu'].set_column(col_num, col_num, 15)
            
    return output.getvalue()



# --- HÀM TẠO FILE EXCEL MẪU ---
def tạo_excel_mẫu():
    # Danh sách các cột theo ảnh bạn gửi
    cột_mẫu = [
        "So", "Ten", "ChucVu", "Luong", "TenKhach", "TenSuKien", 
        "ThoiGian", "DiaDiem", "NgayCap", "LuongMoi", "LuongCu", 
        "NgayHieuLuc", "MaNV", "Phongban"
    ]
    
    # Dữ liệu mẫu ban đầu
    data_mẫu = [
        ["01", "Nguyễn Văn A", "Trưởng phòng", "20.000.000", "Lê Văn B", "Hội nghị khách hàng", 
         "08:00 01/02/2026", "Hà Nội", "01/01/2026", "25.000.000", "20.000.000", 
         "15/02/2026", "NV001", "Kinh doanh"]
    ]
    
    df_mẫu = pd.DataFrame(data_mẫu, columns=cột_mẫu)
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_mẫu.to_excel(writer, index=False, sheet_name='Mau_Nhap_Lieu')
        # Định dạng một chút cho đẹp
        workbook = writer.book
        header_fmt = workbook.add_format({'bold': True, 'bg_color': '#2ecc71', 'font_color': 'white', 'border': 1})
        for col_num, value in enumerate(df_mẫu.columns.values):
            writer.sheets['Mau_Nhap_Lieu'].write(0, col_num, value, header_fmt)
            writer.sheets['Mau_Nhap_Lieu'].set_column(col_num, col_num, 15)
            
    return output.getvalue()

# --- GIAO DIỆN TAB 3 ---
with tabs[2]:
    st.header("🎭 Trộn Hồ Sơ & Hợp Đồng Chuyên Nghiệp")
    
    # Khu vực hướng dẫn & Tải mẫu
    col_guide, col_download = st.columns([2, 1])
    with col_guide:
        st.markdown("""
        **Quy trình sử dụng:**
        1. Tải **File Excel Mẫu** về và điền thông tin (hoặc dán vào bảng dưới).
        2. Tải **File Word Mẫu** lên (các từ khóa phải nằm trong `{{ }}`).
        3. Nhấn **Xuất Zip** để nhận kết quả.
        """)
    
    with col_download:
        excel_mẫu = tạo_excel_mẫu()
        st.download_button(
            label="📥 TẢI FILE EXCEL MẪU",
            data=excel_mẫu,
            file_name="Mau_nhap_lieu_SmartTools.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    st.divider()

    # Khu vực nhập liệu chính
    c1, c2 = st.columns(2)
    with c1:
        word_template = st.file_uploader("📂 Tải file Word mẫu", type=["docx"], key="w_tpl")
    with c2:
        st.info("💡 Bạn có thể dán (Ctrl+V) dữ liệu trực tiếp vào bảng phía dưới.")

    # Khởi tạo bảng nhập liệu với đúng các cột yêu cầu
    cột_yêu_cầu = [
        "So", "Ten", "ChucVu", "Luong", "TenKhach", "TenSuKien", 
        "ThoiGian", "DiaDiem", "NgayCap", "LuongMoi", "LuongCu", 
        "NgayHieuLuc", "MaNV", "Phongban"
    ]
    
    if 'df_merge' not in st.session_state:
        st.session_state.df_merge = pd.DataFrame(columns=cột_yêu_cầu)

    # Bảng nhập liệu thông minh (Data Editor)
    edited_df = st.data_editor(
        st.session_state.df_merge, 
        num_rows="dynamic", 
        use_container_width=True,
        key="pro_editor"
    )

    # Xử lý trộn file
    if st.button("🚀 XUẤT HÀNG LOẠT (.ZIP)", use_container_width=True):
        if word_template and not edited_df.empty:
            try:
                zip_buffer = BytesIO()
                with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                    for index, row in edited_df.iterrows():
                        doc = DocxTemplate(word_template)
                        context = row.to_dict()
                        
                        # Tự động thêm cột Số Tiền Chữ nếu có cột Luong hoặc LuongMoi
                        if "LuongMoi" in context and context["LuongMoi"]:
                            context["LuongMoiChu"] = doc_so_thanh_chu_logic(context["LuongMoi"])
                        
                        doc.render(context)
                        out_word = BytesIO()
                        doc.save(out_word)
                        
                        # Tên file: ưu tiên cột Ten, nếu không có lấy So
                        fname = str(row.get('Ten', row.get('So', f'File_{index}'))).replace(' ', '_')
                        zip_file.writestr(f"{fname}.docx", out_word.getvalue())
                
                st.success(f"✅ Đã xử lý {len(edited_df)} tài liệu!")
                st.download_button("📥 TẢI KẾT QUẢ (.ZIP)", zip_buffer.getvalue(), "Ket_Qua.zip", "application/zip")
            except Exception as e:
                st.error(f"❌ Lỗi: {e}")
        else:
            st.warning("⚠️ Vui lòng cung cấp file Word mẫu và nhập ít nhất 1 dòng dữ liệu!")

with tabs[3]: st.write("Chức năng đang phát triển...")
with tabs[4]: st.write("Chức năng đang phát triển...")
