import streamlit as st

# 1. Cấu hình trang rộng và tiêu đề
st.set_page_config(layout="wide", page_title="Smart Tools Hub - Dashboard")

# 2. CSS nâng cao: Tạo hiệu ứng Gradient, Bo góc và Hover (giống AdminPro)
st.markdown("""
    <style>
    /* Nền tổng thể */
    .stApp { background-color: #f1f5f9; }
    
    /* Thiết kế thẻ Card */
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
    
    /* Làm mờ các mục chưa có (Demo) */
    .demo { opacity: 0.6; background-color: #fafafa; border-style: dashed; }
    </style>
    """, unsafe_allow_html=True)

# 3. Header
st.title("🚀 Smart Tools Admin Dashboard")
st.write("Hệ sinh thái công cụ tự động hóa đa năng. Vui lòng chọn một công cụ bên dưới:")
st.divider()

# 4. Danh sách 16 Tools (3 mục thật + 13 mục demo)
tools = [
    {"name": "Dữ liệu Excel", "icon": "📊", "path": "pages/1_📊_Excel_Tools.py", "status": "Active"},
    {"name": "Content AI", "icon": "🤖", "path": "pages/2_🤖_AI_Marketing.py", "status": "Active"},
    {"name": "Quản lý kho", "icon": "📦", "path": "pages/3_📦_Warehouse.py", "status": "Active"},
    {"name": "Gửi SMS", "icon": "💬", "path": "", "status": "Demo"},
    {"name": "Quét Website", "icon": "🌐", "path": "", "status": "Demo"},
    {"name": "Chuyển PDF", "icon": "📄", "path": "", "status": "Demo"},
    {"name": "Tài chính", "icon": "💰", "path": "", "status": "Demo"},
    {"name": "Lịch hẹn", "icon": "📅", "path": "", "status": "Demo"},
    {"name": "Rút gọn link", "icon": "🔗", "path": "", "status": "Demo"},
    {"name": "Tạo QR", "icon": "🔍", "path": "", "status": "Demo"},
    {"name": "Nhân sự", "icon": "👥", "path": "", "status": "Demo"},
    {"name": "Email Marketing", "icon": "📧", "path": "", "status": "Demo"},
    {"name": "Thiết kế ảnh", "icon": "🎨", "path": "", "status": "Demo"},
    {"name": "Phân tích SEO", "icon": "📈", "path": "", "status": "Demo"},
    {"name": "Auto Social", "icon": "📱", "path": "", "status": "Demo"},
    {"name": "Báo cáo", "icon": "📓", "path": "", "status": "Demo"},
]

# 5. Render Grid 4 cột x 4 hàng
for i in range(0, 16, 4):
    cols = st.columns(4)
    for j in range(4):
        index = i + j
        tool = tools[index]
        with cols[j]:
            # Hiển thị Card bằng HTML
            is_demo_class = "demo" if tool["status"] == "Demo" else ""
            st.markdown(f"""
                <div class="tool-card {is_demo_class}">
                    <div class="icon">{tool['icon']}</div>
                    <div class="tool-name">{tool['name']}</div>
                    <div class="status-tag">{ "Sắp ra mắt" if tool['status'] == 'Demo' else "Sẵn sàng" }</div>
                </div>
            """, unsafe_allow_html=True)
            
            # Nút bấm tương ứng bên dưới Card
            if tool["status"] == "Active":
                if st.button(f"Sử dụng {tool['name']}", key=f"btn_{index}", use_container_width=True):
                    st.switch_page(tool["path"])
            else:
                st.button("Xem Demo", key=f"btn_{index}", disabled=True, use_container_width=True)

# 6. Footer
st.divider()
st.caption("© 2026 Smart Tools Hub | Hỗ trợ: Zalo 0869611000")