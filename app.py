import streamlit as st
from datetime import datetime, date
import pandas as pd

# =========================================================
# CẤU HÌNH TRANG
# =========================================================
st.set_page_config(
    page_title="Hotel Manager",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# CSS
# =========================================================
st.markdown("""
<style>
    .main {
        background-color: #f5f7fa;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    .hotel-title {
        font-size: 32px;
        font-weight: 700;
        color: #17365d;
        margin-bottom: 0;
    }

    .hotel-subtitle {
        color: #6b7280;
        margin-bottom: 25px;
    }

    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06);
        border: 1px solid #e5e7eb;
    }

    .room-card {
        background: white;
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
        margin-bottom: 10px;
    }

    .status-empty {
        color: #15803d;
        font-weight: 700;
    }

    .status-occupied {
        color: #dc2626;
        font-weight: 700;
    }

    .status-cleaning {
        color: #d97706;
        font-weight: 700;
    }

    .status-maintenance {
        color: #7c3aed;
        font-weight: 700;
    }

    div[data-testid="stMetric"] {
        background-color: white;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
    }
</style>
""", unsafe_allow_html=True)


# =========================================================
# DỮ LIỆU BAN ĐẦU
# =========================================================
def create_initial_rooms():
    rooms = []

    room_types = {
        "101": ("Phòng đơn", 1, 350000),
        "102": ("Phòng đơn", 1, 350000),
        "103": ("Phòng đôi", 2, 500000),
        "104": ("Phòng đôi", 2, 500000),
        "105": ("Phòng đôi", 2, 500000),
        "201": ("Phòng đơn", 1, 400000),
        "202": ("Phòng đơn", 1, 400000),
        "203": ("Phòng đôi", 2, 550000),
        "204": ("Phòng đôi", 2, 550000),
        "205": ("Phòng đôi", 2, 550000),
        "301": ("Deluxe", 2, 750000),
        "302": ("Deluxe", 2, 750000),
        "303": ("Deluxe", 2, 750000),
        "304": ("Suite", 4, 1200000),
        "305": ("Suite", 4, 1200000),
    }

    for number, info in room_types.items():
        rooms.append({
            "room": number,
            "type": info[0],
            "capacity": info[1],
            "price": info[2],
            "status": "Trống",
            "guest": "",
            "phone": "",
            "checkin": None,
            "checkout": None,
            "note": ""
        })

    return pd.DataFrame(rooms)


if "rooms" not in st.session_state:
    st.session_state.rooms = create_initial_rooms()

if "bookings" not in st.session_state:
    st.session_state.bookings = []

if "selected_page" not in st.session_state:
    st.session_state.selected_page = "Tổng quan"


# =========================================================
# HÀM TIỆN ÍCH
# =========================================================
def format_money(value):
    return f"{int(value):,}".replace(",", ".") + " đ"


def get_room(room_number):
    index = st.session_state.rooms[
        st.session_state.rooms["room"] == room_number
    ].index

    if len(index) == 0:
        return None

    return index[0]


def change_room_status(room_number, status):
    idx = get_room(room_number)

    if idx is not None:
        st.session_state.rooms.at[idx, "status"] = status


def clear_room(room_number):
    idx = get_room(room_number)

    if idx is not None:
        st.session_state.rooms.at[idx, "status"] = "Trống"
        st.session_state.rooms.at[idx, "guest"] = ""
        st.session_state.rooms.at[idx, "phone"] = ""
        st.session_state.rooms.at[idx, "checkin"] = None
        st.session_state.rooms.at[idx, "checkout"] = None
        st.session_state.rooms.at[idx, "note"] = ""


def checkin_room(room_number, guest, phone, checkout, note):
    idx = get_room(room_number)

    if idx is None:
        return False

    st.session_state.rooms.at[idx, "status"] = "Đang ở"
    st.session_state.rooms.at[idx, "guest"] = guest
    st.session_state.rooms.at[idx, "phone"] = phone
    st.session_state.rooms.at[idx, "checkin"] = date.today()
    st.session_state.rooms.at[idx, "checkout"] = checkout
    st.session_state.rooms.at[idx, "note"] = note

    return True


def checkout_room(room_number):
    idx = get_room(room_number)

    if idx is None:
        return

    room = st.session_state.rooms.loc[idx]

    checkin_date = room["checkin"]
    checkout_date = date.today()

    nights = 1

    if checkin_date:
        nights = max(
            1,
            (checkout_date - checkin_date).days
        )

    total = room["price"] * nights

    booking = {
        "room": room["room"],
        "guest": room["guest"],
        "phone": room["phone"],
        "checkin": room["checkin"],
        "checkout": checkout_date,
        "nights": nights,
        "total": total
    }

    st.session_state.bookings.append(booking)

    change_room_status(room_number, "Dọn phòng")

    st.session_state.rooms.at[idx, "guest"] = ""
    st.session_state.rooms.at[idx, "phone"] = ""
    st.session_state.rooms.at[idx, "checkin"] = None
    st.session_state.rooms.at[idx, "checkout"] = None

    return total


# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:

    st.markdown("## 🏨 HOTEL MANAGER")
    st.caption("Hệ thống quản lý khách sạn")

    st.divider()

    pages = [
        "📊 Tổng quan",
        "🛏️ Quản lý phòng",
        "🧾 Nhận phòng",
        "🚪 Trả phòng",
        "👥 Khách đang ở",
        "📋 Lịch sử lưu trú",
        "💰 Doanh thu"
    ]

    for page in pages:
        if st.button(
            page,
            use_container_width=True,
            key=f"menu_{page}"
        ):
            st.session_state.selected_page = page.replace(
                "📊 ", ""
            ).replace(
                "🛏️ ", ""
            ).replace(
                "🧾 ", ""
            ).replace(
                "🚪 ", ""
            ).replace(
                "👥 ", ""
            ).replace(
                "📋 ", ""
            ).replace(
                "💰 ", ""
            )

    st.divider()

    st.info(
        "💡 Dữ liệu hiện được lưu trong phiên chạy Streamlit. "
        "Nếu cần dữ liệu không mất khi app khởi động lại, "
        "có thể kết nối SQLite hoặc MySQL."
    )


page = st.session_state.selected_page


# =========================================================
# TRANG TỔNG QUAN
# =========================================================
if page == "Tổng quan":

    st.markdown(
        '<div class="hotel-title">🏨 Quản lý khách sạn</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="hotel-subtitle">'
        'Tổng quan hoạt động khách sạn'
        '</div>',
        unsafe_allow_html=True
    )

    rooms = st.session_state.rooms

    total_rooms = len(rooms)
    empty_rooms = len(rooms[rooms["status"] == "Trống"])
    occupied_rooms = len(rooms[rooms["status"] == "Đang ở"])
    cleaning_rooms = len(rooms[rooms["status"] == "Dọn phòng"])
    maintenance_rooms = len(
        rooms[rooms["status"] == "Bảo trì"]
    )

    total_revenue = sum(
        booking["total"]
        for booking in st.session_state.bookings
    )

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric("🏨 Tổng phòng", total_rooms)
    c2.metric("🟢 Phòng trống", empty_rooms)
    c3.metric("🔴 Đang ở", occupied_rooms)
    c4.metric("🟠 Dọn phòng", cleaning_rooms)
    c5.metric("💰 Doanh thu", format_money(total_revenue))

    st.markdown("### 📌 Tình trạng phòng")

    status_data = pd.DataFrame({
        "Trạng thái": [
            "Trống",
            "Đang ở",
            "Dọn phòng",
            "Bảo trì"
        ],
        "Số phòng": [
            empty_rooms,
            occupied_rooms,
            cleaning_rooms,
            maintenance_rooms
        ]
    })

    col_chart, col_info = st.columns([2, 1])

    with col_chart:
        st.bar_chart(
            status_data.set_index("Trạng thái")
        )

    with col_info:
        st.markdown("#### Thống kê")

        if total_rooms > 0:
            occupancy = (
                occupied_rooms / total_rooms
            ) * 100
        else:
            occupancy = 0

        st.metric(
            "Công suất phòng",
            f"{occupancy:.1f}%"
        )

        st.write(
            f"Phòng trống: **{empty_rooms}**"
        )
        st.write(
            f"Phòng đang ở: **{occupied_rooms}**"
        )
        st.write(
            f"Phòng đang dọn: **{cleaning_rooms}**"
        )
        st.write(
            f"Phòng bảo trì: **{maintenance_rooms}**"
        )

    st.markdown("### 👥 Khách đang lưu trú")

    occupied = rooms[
        rooms["status"] == "Đang ở"
    ].copy()

    if len(occupied) == 0:
        st.success("Hiện chưa có khách đang lưu trú.")
    else:
        display = occupied[
            [
                "room",
                "type",
                "guest",
                "phone",
                "checkin",
                "checkout"
            ]
        ].copy()

        display.columns = [
            "Phòng",
            "Loại phòng",
            "Khách",
            "Số điện thoại",
            "Ngày nhận",
            "Ngày trả"
        ]

        st.dataframe(
            display,
            use_container_width=True,
            hide_index=True
        )


# =========================================================
# QUẢN LÝ PHÒNG
# =========================================================
elif page == "Quản lý phòng":

    st.title("🛏️ Quản lý phòng")

    rooms = st.session_state.rooms.copy()

    col1, col2 = st.columns(2)

    with col1:
        filter_status = st.selectbox(
            "Lọc theo trạng thái",
            [
                "Tất cả",
                "Trống",
                "Đang ở",
                "Dọn phòng",
                "Bảo trì"
            ]
        )

    with col2:
        filter_type = st.selectbox(
            "Lọc theo loại phòng",
            ["Tất cả"] +
            sorted(rooms["type"].unique().tolist())
        )

    if filter_status != "Tất cả":
        rooms = rooms[
            rooms["status"] == filter_status
        ]

    if filter_type != "Tất cả":
        rooms = rooms[
            rooms["type"] == filter_type
        ]

    st.write(
        f"Hiển thị **{len(rooms)} phòng**"
    )

    for _, room in rooms.iterrows():

        with st.container(border=True):

            c1, c2, c3, c4, c5 = st.columns(
                [1, 2, 2, 2, 2]
            )

            c1.markdown(
                f"### 🛏️ {room['room']}"
            )

            c2.write(
                f"**{room['type']}**\n\n"
                f"Sức chứa: {room['capacity']} người"
            )

            c3.write(
                f"Giá: **{format_money(room['price'])}/đêm**"
            )

            status = room["status"]

            if status == "Trống":
                c4.markdown(
                    '<span class="status-empty">'
                    '🟢 Trống'
                    '</span>',
                    unsafe_allow_html=True
                )

            elif status == "Đang ở":
                c4.markdown(
                    '<span class="status-occupied">'
                    '🔴 Đang ở'
                    '</span>',
                    unsafe_allow_html=True
                )

            elif status == "Dọn phòng":
                c4.markdown(
                    '<span class="status-cleaning">'
                    '🟠 Dọn phòng'
                    '</span>',
                    unsafe_allow_html=True
                )

            else:
                c4.markdown(
                    '<span class="status-maintenance">'
                    '🟣 Bảo trì'
                    '</span>',
                    unsafe_allow_html=True
                )

            with c5:
                if status == "Dọn phòng":

                    if st.button(
                        "✅ Đã dọn",
                        key=f"clean_{room['room']}"
                    ):
                        change_room_status(
                            room["room"],
                            "Trống"
                        )
                        st.rerun()

                elif status == "Trống":

                    if st.button(
                        "🔧 Bảo trì",
                        key=f"maintenance_{room['room']}"
                    ):
                        change_room_status(
                            room["room"],
                            "Bảo trì"
                        )
                        st.rerun()

                elif status == "Bảo trì":

                    if st.button(
                        "🟢 Mở phòng",
                        key=f"open_{room['room']}"
                    ):
                        change_room_status(
                            room["room"],
                            "Trống"
                        )
                        st.rerun()

            if room["status"] == "Đang ở":
                st.caption(
                    f"Khách: {room['guest']} | "
                    f"SĐT: {room['phone']}"
                )


# =========================================================
# NHẬN PHÒNG
# =========================================================
elif page == "Nhận phòng":

    st.title("🧾 Nhận phòng")

    rooms = st.session_state.rooms

    available_rooms = rooms[
        rooms["status"] == "Trống"
    ]

    if len(available_rooms) == 0:

        st.warning(
            "Hiện không có phòng trống để nhận khách."
        )

    else:

        with st.form("checkin_form"):

            room_number = st.selectbox(
                "Chọn phòng",
                available_rooms["room"].tolist()
            )

            selected_room = available_rooms[
                available_rooms["room"] == room_number
            ].iloc[0]

            st.info(
                f"{selected_room['type']} | "
                f"Sức chứa: {selected_room['capacity']} người | "
                f"{format_money(selected_room['price'])}/đêm"
            )

            guest = st.text_input(
                "Họ và tên khách *"
            )

            phone = st.text_input(
                "Số điện thoại"
            )

            checkout = st.date_input(
                "Ngày dự kiến trả phòng",
                value=date.today()
            )

            note = st.text_area(
                "Ghi chú"
            )

            submit = st.form_submit_button(
                "✅ Xác nhận nhận phòng",
                use_container_width=True
            )

            if submit:

                if not guest.strip():
                    st.error(
                        "Vui lòng nhập tên khách."
                    )

                elif checkout < date.today():
                    st.error(
                        "Ngày trả phòng không hợp lệ."
                    )

                else:

                    checkin_room(
                        room_number,
                        guest.strip(),
                        phone.strip(),
                        checkout,
                        note.strip()
                    )

                    st.success(
                        f"Đã nhận phòng {room_number} "
                        f"cho khách {guest}."
                    )

                    st.rerun()


# =========================================================
# TRẢ PHÒNG
# =========================================================
elif page == "Trả phòng":

    st.title("🚪 Trả phòng")

    occupied = st.session_state.rooms[
        st.session_state.rooms["status"] == "Đang ở"
    ]

    if len(occupied) == 0:

        st.info(
            "Hiện không có khách nào đang lưu trú."
        )

    else:

        room_number = st.selectbox(
            "Chọn phòng trả",
            occupied["room"].tolist()
        )

        room = occupied[
            occupied["room"] == room_number
        ].iloc[0]

        st.markdown("### Thông tin lưu trú")

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Phòng",
            room["room"]
        )

        c2.metric(
            "Khách",
            room["guest"]
        )

        c3.metric(
            "Giá/đêm",
            format_money(room["price"])
        )

        st.write(
            f"📅 Ngày nhận: **{room['checkin']}**"
        )

        st.write(
            f"📅 Ngày dự kiến trả: **{room['checkout']}**"
        )

        if room["checkin"]:

            nights = max(
                1,
                (date.today() - room["checkin"]).days
            )

        else:
            nights = 1

        total = room["price"] * nights

        st.markdown("### 💰 Thanh toán")

        c1, c2 = st.columns(2)

        c1.metric(
            "Số đêm",
            nights
        )

        c2.metric(
            "Tổng tiền phòng",
            format_money(total)
        )

        confirm = st.checkbox(
            "Tôi xác nhận khách đã trả phòng."
        )

        if st.button(
            "🚪 Xác nhận trả phòng",
            type="primary",
            disabled=not confirm,
            use_container_width=True
        ):

            checkout_total = checkout_room(
                room_number
            )

            st.success(
                f"Đã trả phòng {room_number}. "
                f"Tổng tiền: {format_money(checkout_total)}"
            )

            st.rerun()


# =========================================================
# KHÁCH ĐANG Ở
# =========================================================
elif page == "Khách đang ở":

    st.title("👥 Khách đang lưu trú")

    occupied = st.session_state.rooms[
        st.session_state.rooms["status"] == "Đang ở"
    ].copy()

    if len(occupied) == 0:

        st.info(
            "Hiện chưa có khách đang lưu trú."
        )

    else:

        for _, room in occupied.iterrows():

            with st.container(border=True):

                st.subheader(
                    f"🛏️ Phòng {room['room']} — "
                    f"{room['guest']}"
                )

                c1, c2, c3 = st.columns(3)

                c1.write(
                    f"📞 **Số điện thoại:** "
                    f"{room['phone'] or 'Chưa có'}"
                )

                c2.write(
                    f"📅 **Nhận phòng:** "
                    f"{room['checkin']}"
                )

                c3.write(
                    f"📅 **Trả phòng:** "
                    f"{room['checkout']}"
                )

                if room["note"]:
                    st.write(
                        f"📝 Ghi chú: {room['note']}"
                    )


# =========================================================
# LỊCH SỬ
# =========================================================
elif page == "Lịch sử lưu trú":

    st.title("📋 Lịch sử lưu trú")

    bookings = st.session_state.bookings

    if len(bookings) == 0:

        st.info(
            "Chưa có dữ liệu trả phòng."
        )

    else:

        history = pd.DataFrame(bookings)

        history = history[
            [
                "room",
                "guest",
                "phone",
                "checkin",
                "checkout",
                "nights",
                "total"
            ]
        ]

        history.columns = [
            "Phòng",
            "Khách",
            "Số điện thoại",
            "Ngày nhận",
            "Ngày trả",
            "Số đêm",
            "Tổng tiền"
        ]

        history["Tổng tiền"] = history[
            "Tổng tiền"
        ].apply(format_money)

        st.dataframe(
            history,
            use_container_width=True,
            hide_index=True
        )


# =========================================================
# DOANH THU
# =========================================================
elif page == "Doanh thu":

    st.title("💰 Doanh thu")

    bookings = st.session_state.bookings

    if len(bookings) == 0:

        st.info(
            "Chưa có dữ liệu doanh thu."
        )

    else:

        total_revenue = sum(
            x["total"] for x in bookings
        )

        total_bookings = len(bookings)

        total_nights = sum(
            x["nights"] for x in bookings
        )

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "💰 Tổng doanh thu",
            format_money(total_revenue)
        )

        c2.metric(
            "🧾 Số lượt lưu trú",
            total_bookings
        )

        c3.metric(
            "🌙 Tổng số đêm",
            total_nights
        )

        st.markdown("### 📊 Doanh thu theo phòng")

        revenue_data = {}

        for booking in bookings:

            room = booking["room"]

            if room not in revenue_data:
                revenue_data[room] = 0

            revenue_data[room] += booking["total"]

        revenue_df = pd.DataFrame(
            list(revenue_data.items()),
            columns=["Phòng", "Doanh thu"]
        )

        revenue_df = revenue_df.sort_values(
            "Doanh thu",
            ascending=False
        )

        st.bar_chart(
            revenue_df.set_index("Phòng")
        )

        st.markdown("### 📋 Chi tiết doanh thu")

        display = revenue_df.copy()

        display["Doanh thu"] = display[
            "Doanh thu"
        ].apply(format_money)

        st.dataframe(
            display,
            use_container_width=True,
            hide_index=True
        )


# =========================================================
# FOOTER
# =========================================================
st.divider()

st.caption(
    "🏨 Hotel Manager | Ứng dụng quản lý phòng khách sạn "
    f"| {datetime.now().strftime('%d/%m/%Y %H:%M')}"
)
