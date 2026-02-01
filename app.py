import streamlit as st

# 1. Cấu hình trang rộng và tiêu đề
st.set_page_config(layout="wide", page_title="Smart Tools Hub - Dashboard")

# 2. CSS nâng cao: Tùy chỉnh Dashboard và SIDEBAR BÊN TRÁI
st.markdown("""
    <style>
    /* Nền tổng thể */
    .stApp { background-color: #f1f5f9; }
    
    /* --- TÙY CHỈNH SIDEBAR BÊN TRÁI --- */
    /* Màu nền Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #745af2 0%, #01caf1 100%);
    }
    
    /* Cỡ chữ, màu sắc và độ đậm của Menu Sidebar */
    [data-testid="stSidebarNav"] ul li div a span {
        color: white !important;
        font-size: 18px !important; /* Tăng cỡ chữ */
        font-weight: bold !important; /* Chữ đậm */
    }
    
    /* Hiệu ứng khi di chuột qua menu bên trái */
    [data-testid="stSidebarNav"] ul li div:hover {
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }

    /* --- CẤU TRÚC CARD TRÊN TRANG CHÍNH --- */
    .tool-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        text-align: center;
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease-in-out;
        height: 180px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        margin-bottom: 10px;
    }
    
    .tool-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        border-color: #745af2;
    }

    .icon { font-size: 45px; margin-bottom: 10px; }
    .tool-name { font-weight: bold; color: #1e293b; margin-bottom: 5px; }
    .status-tag { font-size: 12px; color: #94a3b8; }
    .demo { opacity: 0.6; background-color: #fafafa; border-style: dashed; }

    div.stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: 0.2s;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Header
st.title("Smart Tools Admin Dashboard")
st.write("Hệ sinh thái công cụ tự động hóa đa năng. Vui lòng chọn một công cụ bên dưới:")
st.divider()

# 4. Danh sách 16 Tools
tools = [
    {"name": "Dữ liệu Excel", "icon": "📊", "path": "pages/1_📊_Excel_Tools.py", "status": "Active"},
    {"name": "Content AI", "icon": "🤖", "path": "pages/2_🤖_AI_Marketing.py", "status": "Active"},
    {"name": "Quản lý kho", "icon": "📦", "path": "pages/3_📦_Warehouse.py", "status": "Active"},
    {"name": "Gửi SMS", "icon": "💬", "path": "pages/4_💎_Nâng_Cấp_VIP.py", "status": "Demo"},
    {"name": "Quét Website", "icon": "🌐", "path": "pages/4_💎_Nâng_Cấp_VIP.py", "status": "Demo"},
    {"name": "Chuyển PDF", "icon": "📄", "path": "pages/4_💎_Nâng_Cấp_VIP.py", "status": "Demo"},
    {"name": "Tài chính", "icon": "💰", "path": "pages/4_💎_Nâng_Cấp_VIP.py", "status": "Demo"},
    {"name": "Lịch hẹn", "icon": "📅", "path": "pages/4_💎_Nâng_Cấp_VIP.py", "status": "Demo"},
    {"name": "Rút gọn link", "icon": "🔗", "path": "pages/4_💎_Nâng_Cấp_VIP.py", "status": "Demo"},
    {"name": "Tạo QR", "icon": "🔍", "path": "pages/4_💎_Nâng_Cấp_VIP.py", "status": "Demo"},
    {"name": "Nhân sự", "icon": "👥", "path": "pages/4_💎_Nâng_Cấp_VIP.py", "status": "Demo"},
    {"name": "Email Marketing", "icon": "📧", "path": "pages/4_💎_Nâng_Cấp_VIP.py", "status": "Demo"},
    {"name": "Thiết kế ảnh", "icon": "🎨", "path": "pages/4_💎_Nâng_Cấp_VIP.py", "status": "Demo"},
    {"name": "Phân tích SEO", "icon": "📈", "path": "pages/4_💎_Nâng_Cấp_VIP.py", "status": "Demo"},
    {"name": "Auto Social", "icon": "📱", "path": "pages/4_💎_Nâng_Cấp_VIP.py", "status": "Demo"},
    {"name": "Báo cáo", "icon": "📓", "path": "pages/4_💎_Nâng_Cấp_VIP.py", "status": "Demo"},
]

# 5. Render Grid 4 cột x 4 hàng
for i in range(0, 16, 4):
    cols = st.columns(4)
    for j in range(4):
        index = i + j
        if index < len(tools):
            tool = tools[index]
            with cols[j]:
                is_demo_class = "demo" if tool["status"] == "Demo" else ""
                st.markdown(f"""
                    <div class="tool-card {is_demo_class}">
                        <div class="icon">{tool['icon']}</div>
                        <div class="tool-name">{tool['name']}</div>
                        <div class="status-tag">{ "Sắp ra mắt" if tool['status'] == 'Demo' else "Sẵn sàng" }</div>
                    </div>
                """, unsafe_allow_html=True)
                
                if tool["status"] == "Active":
                    if st.button(f"Sử dụng {tool['name']}", key=f"btn_{index}", use_container_width=True):
                        st.switch_page(tool["path"])
                else:
                    if st.button("Mở khóa bản PRO", key=f"btn_{index}", use_container_width=True):
                        st.switch_page("pages/4_💎_Nâng_Cấp_VIP.py")

# 6. Footer
st.divider()
st.caption("© 2026 Smart Tools Hub | Hỗ trợ: Zalo 0869611000")

