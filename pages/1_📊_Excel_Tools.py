import streamlit as st
import pandas as pd
import google.generativeai as genai
import re
from io import BytesIO

# 1. Cấu hình ban đầu & Giao diện đồng bộ
st.set_page_config(page_title="Smart Tools Hub - Pro", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f1f5f9; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #745af2 0%, #01caf1 100%); }
    [data-testid="stSidebarNav"] ul li div a span { color: white !important; font-size: 18px !important; font-weight: bold !important; }
    div.stButton > button { border-radius: 8px; font-weight: 600; background-color: #745af2; color: white; border: none; }
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p { font-size: 16px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

if st.sidebar.button("🏠 VỀ DASHBOARD TỔNG"):
    st.switch_page("app.py")

# Kết nối AI
if "GEMINI_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("Chưa cấu hình API Key!")
    st.stop()

# --- CÁC HÀM XỬ LÝ PHỤ TRỢ ---
def doc_so_thanh_chu(so):
    # Hàm mẫu đơn giản bằng AI để đọc số tiền tiếng Việt
    prompt = f"Chuyển số sau thành chữ tiếng Việt (đọc số tiền): {so}"
    res = model.generate_content(prompt)
    return res.text

# 2. Giao diện Chính
st.title("🚀 SMART TOOLS HUB - ADVANCED")
st.divider()

tabs = st.tabs(["📊 Excel", "📍 Tách Địa Chỉ", "👤 Tách Họ Tên", "💰 Đọc Số Tiền", "📧 Check Email"])

# --- TAB 1 & 2: GIỮ NGUYÊN NHƯ CODE TRƯỚC CỦA BẠN ---
with tabs[0]: st.write("Chức năng chuẩn hóa Excel cũ của bạn...")
with tabs[1]: st.write("Chức năng tách địa chỉ AI cũ của bạn...")

# --- TAB 3: TÁCH HỌ VÀ TÊN ---
with tabs[2]:
    st.markdown("#### 👤 Tách Họ và Tên riêng biệt")
    name_input = st.text_input("Nhập họ và tên đầy đủ:", placeholder="Ví dụ: Nguyễn Văn Minh")
    if name_input:
        parts = name_input.strip().split()
        if len(parts) > 1:
            ho = parts[0]
            ten = parts[-1]
            dem = " ".join(parts[1:-1])
            col1, col2, col3 = st.columns(3)
            col1.metric("Họ", ho)
            col2.metric("Tên đệm", dem)
            col3.metric("Tên chính", ten)
        else:
            st.warning("Vui lòng nhập đầy đủ cả họ và tên.")

# --- TAB 4: ĐỌC SỐ TIỀN ---
with tabs[3]:
    st.markdown("#### 💰 Chuyển số thành chữ (Hóa đơn)")
    amount = st.number_input("Nhập số tiền cần đọc:", min_value=0, step=1000)
    if st.button("Chuyển thành chữ"):
        with st.spinner('Đang dịch số...'):
            ket_qua = doc_so_thanh_chu(amount)
            st.success(f"Kết quả: {ket_qua}")

# --- TAB 5: KIỂM TRA EMAIL ---
with tabs[4]:
    st.markdown("#### 📧 Kiểm tra định dạng Email")
    email_list = st.text_area("Nhập danh sách email (mỗi email một dòng):")
    if st.button("Lọc Email hợp lệ"):
        emails = email_list.split('\n')
        valid_emails = []
        invalid_emails = []
        regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
        
        for e in emails:
            e = e.strip()
            if re.search(regex, e):
                valid_emails.append(e)
            elif e:
                invalid_emails.append(e)
        
        c1, c2 = st.columns(2)
        c1.success(f"Hợp lệ: {len(valid_emails)}")
        c1.write(valid_emails)
        c2.error(f"Sai định dạng: {len(invalid_emails)}")
        c2.write(invalid_emails)

st.divider()
st.caption("© 2026 Smart Tools Hub | Hỗ trợ: Zalo 0869611000")
