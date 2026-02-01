import streamlit as st
import pandas as pd
import google.generativeai as genai
import re
from io import BytesIO

# 1. Cấu hình ban đầu
st.set_page_config(page_title="Smart Tools Hub - Pro", layout="wide")

# CSS Tùy chỉnh Giao diện
st.markdown("""
    <style>
    .stApp { background-color: #f1f5f9; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #745af2 0%, #01caf1 100%); }
    [data-testid="stSidebarNav"] ul li div a span { color: white !important; font-size: 18px !important; font-weight: bold !important; }
    
    /* Nút bấm chính */
    div.stButton > button { border-radius: 8px; font-weight: 600; background-color: #745af2; color: white; border: none; }

    /* KHUNG UPLOAD FILE MÀU XÁM NHẠT + CHỮ TRẮNG */
    [data-testid="stFileUploader"] {
        background-color: #bdc3c7 !important; /* Màu xám nhạt chuyên nghiệp */
        border: 2px dashed #ffffff;
        border-radius: 10px;
        padding: 10px;
    }
    /* Ép tất cả các văn bản bên trong khung upload thành màu trắng */
    [data-testid="stFileUploader"] section div div {
        color: white !important;
    }
    [data-testid="stFileUploader"] label {
        color: #1e293b !important; /* Tiêu đề ngoài khung giữ màu tối cho dễ đọc */
    }
    [data-testid="stFileUploader"] svg {
        fill: white !important;
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
        
        # 1. Chuẩn hóa Họ Tên
        if any(kw in col_lower for kw in ['tên', 'name', 'họ']):
            df_clean[col] = df_clean[col].apply(
                lambda x: " ".join(str(x).strip().title().split()) if pd.notnull(x) and str(x).strip() != "" else x
            )
            
        # 2. Chuẩn hóa Số điện thoại
        elif any(kw in col_lower for kw in ['sđt', 'đt', 'phone', 'tel']):
            def clean_phone(p):
                n = re.sub(r'\D', '', str(p))
                if n.startswith('84'): n = '0' + n[2:]
                elif not n.startswith('0') and len(n) > 0: n = '0' + n
                return n[-10:] if len(n) > 10 else n
            df_clean[col] = df_clean[col].astype(str).apply(clean_phone)
            
        # 3. Chuẩn hóa Ngày tháng
        elif any(kw in col_lower for kw in ['ngày', 'date', 'thời gian']):
            temp_date = pd.to_datetime(df_clean[col], errors='coerce', dayfirst=True)
            df_clean[col] = temp_date.dt.strftime('%d/%m/%Y').fillna('')

    # --- XUẤT FILE VỚI ĐỊNH DẠNG FONT & BẢNG BIỂU ---
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_clean.to_excel(writer, index=False, sheet_name='Data_Da_Chuan_Hoa')
        workbook = writer.book
        worksheet = writer.sheets['Data_Da_Chuan_Hoa']

        header_fmt = workbook.add_format({
            'bold': True, 'bg_color': '#745af2', 'font_color': 'white',
            'border': 1, 'font_name': 'Arial', 'align': 'center', 'valign': 'vcenter'
        })
        
        cell_fmt = workbook.add_format({
            'border': 1, 'font_name': 'Arial', 'font_size': 11, 'valign': 'vcenter'
        })

        for col_num, value in enumerate(df_clean.columns.values):
            worksheet.write(0, col_num, value, header_fmt)
            max_len = max(df_clean[value].astype(str).map(len).max(), len(value)) + 2
            worksheet.set_column(col_num, col_num, min(max_len, 40), cell_fmt)
            
    return output.getvalue()

# --- GIAO DIỆN ---
st.title("🚀 SMART TOOLS HUB - EXCEL PRO")
st.divider()

tabs = st.tabs(["📊 Chuẩn hoá Excel", "📍 Tách Địa Chỉ", "👤 Tách Họ Tên", "💰 Đọc Số Tiền", "📧 Check Email"])

with tabs[0]:
    st.header("📊 Chuẩn hoá Dữ liệu Excel")
    st.info("Chức năng: Sửa Họ tên, Ngày tháng, SĐT. Định dạng Font Arial + Kẻ bảng tự động.")
    
    uploaded_file = st.file_uploader("Kéo và thả file Excel vào đây để bắt đầu", type=["xlsx"])
    
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        st.subheader("Xem trước dữ liệu (10 dòng đầu)")
        st.dataframe(df.head(10), use_container_width=True)
        
        if st.button("✨ BẮT ĐẦU CHUẨN HOÁ VÀ ĐỊNH DẠNG"):
            with st.spinner('Hệ thống đang xử lý dữ liệu và định dạng bảng biểu...'):
                # 1. Gọi hàm xử lý
                result_data = chuan_hoa_excel_pro(df)
                
                # 2. Hiển thị thông báo thành công
                st.success("✅ Đã hoàn thành! Vui lòng nhấn nút tải về bên dưới.")
                
                # 3. TRẢ KẾT QUẢ (Nút Download quan trọng nhất)
                st.download_button(
                    label="📥 TẢI FILE EXCEL ĐÃ CHUẨN HOÁ",
                    data=result_data,
                    file_name=f"Cleaned_{uploaded_file.name}",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
# --- HÀM XỬ LÝ TÁCH ĐỊA CHỈ BẰNG AI ---
def tach_dia_chi_bulk_ai(df, col_name):
    """Sử dụng AI để tách địa chỉ từ một cột trong DataFrame"""
    results = []
    
    # Chuẩn bị Prompt mẫu cho AI để đảm bảo đầu ra ổn định
    sample_format = '[{"Số nhà/Đường": "...", "Phường/Xã": "...", "Quận/Huyện": "...", "Tỉnh/Thành phố": "..."}]'
    
    # Lặp qua từng dòng địa chỉ (Giới hạn 10-20 dòng mỗi lần để tránh quá tải API)
    for addr in df[col_name]:
        if pd.isnull(addr) or str(addr).strip() == "":
            results.append({"Số nhà/Đường": "", "Phường/Xã": "", "Quận/Huyện": "", "Tỉnh/Thành phố": ""})
            continue
            
        prompt = f"""
        Phân tích địa chỉ Việt Nam sau: "{addr}"
        Tách thành 4 cột: "Số nhà/Đường", "Phường/Xã", "Quận/Huyện", "Tỉnh/Thành phố".
        Yêu cầu: 
        1. Trả về duy nhất 1 dòng định dạng JSON đúng cấu trúc: {sample_format}
        2. Nếu thông tin nào thiếu, hãy để trống "".
        3. Phải chuẩn hoá tên riêng (Ví dụ: 'hcm' thành 'TP. Hồ Chí Minh').
        """
        
        try:
            response = model.generate_content(prompt)
            # Làm sạch dữ liệu trả về để chỉ lấy phần JSON
            json_str = re.search(r'\[.*\]', response.text, re.DOTALL).group()
            item = pd.read_json(json_str).iloc[0].to_dict()
            results.append(item)
        except:
            # Nếu AI lỗi, trả về dòng trống để không làm lệch hàng
            results.append({"Số nhà/Đường": "Lỗi AI", "Phường/Xã": "", "Quận/Huyện": "", "Tỉnh/Thành phố": ""})
            
    # Chuyển kết quả thành DataFrame và nối vào DF gốc
    df_addr = pd.DataFrame(results)
    df_final = pd.concat([df.reset_index(drop=True), df_addr], axis=1)
    
    # Xuất file Excel định dạng chuyên nghiệp
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_final.to_excel(writer, index=False, sheet_name='Dia_Chi_Da_Tach')
        workbook = writer.book
        cell_fmt = workbook.add_format({'border': 1, 'font_name': 'Arial'})
        for col_num, value in enumerate(df_final.columns.values):
            writer.sheets['Dia_Chi_Da_Tach'].set_column(col_num, col_num, 25, cell_fmt)
            
    return output.getvalue(), df_final

# --- GIAO DIỆN TAB 2 ---
with tabs[1]:
    st.header("📍 Tách Địa Chỉ Thông Minh (AI)")
    st.info("💡 Chức năng: Tải lên file chứa cột địa chỉ viết liền, AI sẽ tự động tách thành Số nhà, Phường, Quận, Tỉnh.")
    
    file_addr = st.file_uploader("Tải lên file Excel chứa địa chỉ (.xlsx)", type=["xlsx"], key="addr_upload")
    
    if file_addr:
        df_origin = pd.read_excel(file_addr)
        st.write("Dữ liệu vừa tải lên:")
        st.dataframe(df_origin.head(5))
        
        # Cho người dùng chọn cột chứa địa chỉ
        column_to_process = st.selectbox("Chọn cột chứa địa chỉ cần tách:", df_origin.columns)
        
        if st.button("🚀 BẮT ĐẦU TÁCH ĐỊA CHỈ (AI)"):
            with st.spinner('AI đang đọc và phân tích từng địa chỉ... (Vui lòng đợi)'):
                # Xử lý
                excel_data, df_preview = tach_dia_chi_bulk_ai(df_origin, column_to_process)
                
                st.success("✅ Đã tách xong địa chỉ trên cùng hàng!")
                st.subheader("Kết quả sau khi tách:")
                st.dataframe(df_preview.head(10))
                
                st.download_button(
                    label="📥 TẢI FILE ĐỊA CHỈ ĐÃ CHỈNH SỬA",
                    data=excel_data,
                    file_name=f"Dia_Chi_Tach_{file_addr.name}",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
