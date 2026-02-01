import streamlit as st
import pandas as pd
import re
from io import BytesIO
import docx
import PyPDF2
import difflib
import zipfile
from docxtpl import DocxTemplate
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

# 1. CẤU HÌNH GIAO DIỆN
st.set_page_config(page_title="Smart Tools Hub - Pro", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f1f5f9; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #745af2 0%, #01caf1 100%); }
    [data-testid="stSidebarNav"] ul li div a span { color: white !important; font-size: 18px !important; font-weight: bold !important; }
    div.stButton > button { border-radius: 8px; font-weight: 600; background-color: #745af2; color: white; border: none; width: 100%; }

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
def tao_file_word_mau_hop_dong():
    doc = Document()
    # Thiết lập Font chữ
    style = doc.styles['Normal']
    style.font.name = 'Times New Roman'
    style.font.size = Pt(12)

    # Tiêu ngữ
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM\n")
    run.bold = True
    run = p.add_run("Độc lập - Tự do - Hạnh phúc\n")
    run.bold = True
    p.add_run("---------------")

    # Tên hợp đồng
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run("\nHỢP ĐỒNG LAO ĐỘNG")
    run.bold = True
    run.font.size = Pt(16)

    # Nội dung
    doc.add_paragraph(f"\nChúng tôi, một bên là Công ty: ").add_run("{{TenCongTy}}").bold = True
    doc.add_paragraph(f"Và một bên là Ông/Bà: ").add_run("{{Ten}}").bold = True
    
    p = doc.add_paragraph("Mã nhân viên: ")
    p.add_run("{{MaNV}}")
    
    p = doc.add_paragraph("Chức vụ: ")
    p.add_run("{{ChucVu}}")
    
    p = doc.add_paragraph("Mức lương chính thức: ")
    p.add_run("{{Luong}}")
    
    p = doc.add_paragraph("Đơn vị công tác: ")
    p.add_run("{{Phongban}}")
    
    p = doc.add_paragraph("Ngày có hiệu lực: ")
    p.add_run("{{NgayHieuLuc}}")

    doc.add_paragraph("\nCác điều khoản khác được thực hiện theo quy định của pháp luật lao động hiện hành.")

    # Ký tên
    doc.add_paragraph("\n")
    table = doc.add_table(rows=1, cols=2)
    table.cell(0,0).text = "NGƯỜI LAO ĐỘNG\n(Ký và ghi rõ họ tên)"
    table.cell(0,1).text = "ĐẠI DIỆN CÔNG TY\n(Ký và đóng dấu)"
    
    target_stream = BytesIO()
    doc.save(target_stream)
    return target_stream.getvalue()
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

# --- GIAO DIỆN TAB 3 ---
with tabs[2]:
    st.header("🎭 Trộn Hồ Sơ & Hợp Đồng Chuyên Nghiệp")
    
    # Khu vực Tải mẫu - Chia làm 3 cột
    st.subheader("📁 Bước 1: Tải file mẫu hệ thống")
    col_dl1, col_dl2, col_dl3 = st.columns(3)
    
    with col_dl1:
        st.download_button(
            label="📊 TẢI EXCEL NHẬP LIỆU",
            data=tạo_excel_mẫu(),
            file_name="1_Mau_Data_Tong_Hop.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        
    with col_dl2:
        st.download_button(
            label="📄 TẢI MẪU GIẤY MỜI",
            data=tao_file_word_mau_giay_moi(),
            file_name="2_Mau_Giay_Moi_Su_Kien.docx",
            use_container_width=True
        )
        
    with col_dl3:
        st.download_button(
            label="📝 TẢI MẪU HỢP ĐỒNG",
            data=tao_file_word_mau_hop_dong(),
            file_name="3_Mau_Hop_Dong_Lao_Dong.docx",
            use_container_width=True
        )

    st.divider()

    # Bước 2 & 3: Tải file của khách và Nhập liệu
    st.subheader("🚀 Bước 2: Tải file Word đã chỉnh sửa & Dán dữ liệu")
    c1, c2 = st.columns(2)
    with c1:
        word_template = st.file_uploader("📂 Tải lên bản Word mẫu của bạn", type=["docx"], key="user_word_tpl")
    with c2:
        st.info("💡 **Gợi ý:** Bạn có thể tải mẫu ở Bước 1, chỉnh sửa thêm logo công ty rồi tải ngược lại lên đây.")

    # Bảng nhập liệu (Đã được làm đậm chữ đen như yêu cầu trước)
    st.write("📝 **Bảng nhập liệu (Chữ đen đậm):**")
    edited_df = st.data_editor(
        st.session_state.df_merge, 
        num_rows="dynamic", 
        use_container_width=True,
        key="pro_editor_v4"
    )
    
    # Nút thực hiện trộn
    if st.button("🔥 BẮT ĐẦU TRỘN & XUẤT ZIP", use_container_width=True):
        # ... (Phần logic xử lý Zip giữ nguyên như bản trước) ...

with tabs[3]: st.write("Chức năng đang phát triển...")
with tabs[4]: st.write("Chức năng đang phát triển...")
