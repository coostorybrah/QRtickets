# THÔNG BÁO CHUNG

Để đảm bảo mọi người cùng làm việc trong cùng môi trường, sau khi tạo venv chạy lệnh:
python -m pip install -r requirements.txt

## A. GIỚI HẠN CÔNG VIỆC

- Giống như đã phân từ trước.
- Do thời gian có hạn nên chỉ tập trung vào làm các chức năng cho khách hàng (đọc phần B-2.1).

## B. CẤU TRÚC DATABASE

### 0. SETUP

Xem SETUP_GUIDE(MUST_READ).md

### 1. LƯỢC ĐỒ QUAN HỆ

Xem QRticket_ERD(final).png.

### 2. GIẢI THÍCH

- Database gốc gồm:
- - 32 User (20 Customer, 2 Admin và 10 Organizer),
- - 30 sự kiện (Event, 3 pending, 24 approved, 3 rejected),
- - 82 loại vé (TicketType, số lượng và phân loại dựa theo Event),
- - 6 thể loại sự kiện (Category).
- - Mỗi Organizer tổ chức 3 sự kiện, mỗi sự kiện chỉ có 1 organizer.

#### 2.1 USERS

- Toàn bộ user có khả năng đăng nhập, đăng ký và logout:

- - User gồm có 3 role: Customer, Admin và Organizer.
- - Customer có khả năng đặt vé sự kiện và thanh toán;
- - Admin có chức năng chấp nhận (approve) hoặc từ chối (reject) sự kiện (KHÔNG LÀM);
- - Organizer có khả năng tạo và thay đổi chi tiết sự kiện (KHÔNG LÀM).

- Đăng nhập cho các tài khoản đã có sẵn trong DB:

- - username: [role] + [number] (vd: customer1)
- - Có thể đăng nhập bằng email: [username] + "@gmail.com"
- - password: "password123"

- Đăng ký:

- - Tùy ý

#### 2.2 EVENTS

- Status: Bao gồm "pending", "approved" và "rejected", chỉ có các sự kiện "approved" được hiển thị trên web.
- Gồm 2 property: "price__max" và "price__min".
