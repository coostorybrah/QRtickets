# THÔNG BÁO CHUNG

Để đảm bảo mọi người cùng làm việc trong cùng môi trường, tạo venv, mở venv và chạy lệnh:

python -m pip install -r requirements.txt

## A. GIỚI HẠN CÔNG VIỆC

- Giống như đã phân từ trước.
- Do thời gian có hạn nên chỉ tập trung vào làm các chức năng cho khách hàng (đọc phần B-2.1), các chức năng sau sẽ được thêm tùy vào độ thiết yếu của chức năng.

## B. CẤU TRÚC DATABASE

### 0. SETUP

Xem SETUP_GUIDE(MUST_READ).md.

### 1. LƯỢC ĐỒ QUAN HỆ

Xem QRticket_ERD(final).png.

### 2. GIẢI THÍCH

- Database gốc gồm:
- - 32 User (20 Customer, 2 Admin phụ + 1 admin chính và 10 Organizer),
- - 30 sự kiện (Event, 3 pending, 24 approved, 3 rejected),
- - 82 loại vé (TicketType, số lượng và phân loại dựa theo Event),
- - 6 thể loại sự kiện (Category).
- - Mỗi Organizer tổ chức 3 sự kiện, mỗi sự kiện chỉ có 1 organizer.

#### 2.1 USERS

- Toàn bộ user có khả năng đăng nhập, đăng ký, xem thông tin cá nhân và logout:

- - User gồm có 3 role: Customer, Admin và Organizer.
- - Customer có khả năng đặt vé sự kiện, thanh toán và sử dụng vé;
- - Admin phụ có chức năng chấp nhận (approve) hoặc từ chối (reject) sự kiện; (KHÔNG LÀM)
- - Admin chính có quyền chỉnh sửa toàn bộ dữ liệu;
- - Organizer có khả năng scan vé, xem, tạo và thay đổi chi tiết sự kiện. (KHÔNG LÀM xem, tạo và thay đổi chi tiết sự kiện)

#### 2.2 EVENTS

- Có liên kết với thể loại (categories), được thể hiện qua thực thể yếu event_categories và địa điểm (venue);
- Status: Bao gồm "pending", "approved" và "rejected", chỉ có các sự kiện "approved" được hiển thị trên web;
- Gồm 2 property: "price__max" và "price__min". (Cho filter).

#### 2.3 CATEGORIES VÀ EVENT_CATEGORIES

- Mỗi event có thể có nhiều thể loại nhưng không được trùng lặp thể loại, quan hệ này được thể hiện bằng unique constrain của event_categories: UNIQUE(event_id, category_id).

- CHÚ Ý: event_categories được tạo tự động bởi django (muốn kiểm tra thì vào dòng 83-87 events/models.py).

#### 2.4 VENUES

- Organizer không được bán số lượng vé vượt quá venue capacity. (KHÔNG LÀM)

#### 2.5 TICKET_TYPES

- Mỗi sự kiện có các loại vé khác nhau.

#### 2.6 ORDERS

- Bao gồm thông tin bắt buộc: người mua (buyer_[info]) (người mua khác với người dùng), khi đặt vé người mua sẽ nhận email kèm QR cho từng vé.

#### 2.7 ORDER_ITEMS

- Bao gồm thông tin loại vé được mua và số lượng vé thuộc loại đó.

#### 2.8 TICKETS

- MỘT vé bao gồm thông tin loại vé và mã QR tương ứng.

- CHÚ Ý: Vé khác order_items, không thể kết hợp do chức năng khác nhau.

## C. CHỨC NĂNG

### 1. ĐĂNG NHẬP

- Đăng nhập cho các tài khoản đã có sẵn trong DB:

- - username: [role] + [number] (vd: customer1),
- - Có thể đăng nhập bằng email: [username] + "@gmail.com",
- - password: "paygorn4life".

- CHÚ Ý:

- - SUPERUSER (AKA TÀI KHOẢN ADMIN CHÍNH):

- - - username: paygorn123
- - - password: ilikepaygorn
- - - Phải truy cập trang admin qua local domain (127.0.0.1:8000)

- - Khi chưa đăng nhập, api kiểm tra thông tin người dùng báo lỗi là điều bình thường (Vì không có người dùng).

### 2. ĐĂNG KÝ

- Tùy ý, không thể đăng ký tạo tài khoản admin.

### 3. ĐĂNG XUẤT

- Khi đăng xuất, JWT được dọn dẹp và trang được tải lại.

### 4. ĐẶT VÉ VÀ THANH TOÁN

- Trang web có work flow chính như sau:

- - Người dùng đăng nhập -> chọn sự kiện -> click nút mua vé -> sang trang order -> chọn số lượng cho từng loại vé -> thanh toán -> nhận thông báo + thông tin vé.

- - CHÚ Ý: Không hỗ trợ chức năng giỏ hàng do người mua chỉ được phép mua vé cho một sự kiện mỗi khi tạo order.

- ĐẶT VÉ:

- - Khi đến trang order, người dùng phải nhập thông tin cá nhân (Tên, email và số điện thoại) và có ít nhất 1 vé trong "giỏ hàng".

- THANH TOÁN:

- - Gồm thanh toán qua paypal (sandbox) và card (KHÔNG LÀM card).

- - Tài khoản thử nghiệm paypal: Tự tạo tài khoản sandbox. Điền thông tin vào qrticket/settings.py (cuối file). Khi thử nghiệm mua hàng thì dùng test accounts.

### 5. THÔNG BÁO NGƯỜI MUA

- Gửi email cho người mua bao gồm tên người mua và file pdf có ảnh QR cho từng vé.

- Email backend: Vào qrticket/settings.py, xuống cuối file và điền thông tin.

### 6. QUÉT VÉ

- Sau khi đăng nhập, BTC truy cập scanner qua nút "Quét vé". (nằm ở header, chỉ BTC mới có);

- Vé chỉ quét được một lần.

- Sau khi quét, backend cập nhật trạng thái vé trong database, frontend sẽ hiển thị trạng thái mới của vé.

- CHÚ Ý:

- - Để xem trạng thái vé, user vào trang "Vé của tôi" (nếu lúc quét vé xong mà người dùng đang ở page, refresh page để thấy trạng thái vé được cập nhật).

- - BTC chỉ có thể quét vé cho sự kiện do bản thân tổ chức.

### 7. TÌM KIẾM

- Tìm kiếm sự kiện bằng từ khóa (header), sau đó truy vấn sâu hơn bằng filter.

- CHÚ Ý:

- - Nút reset trong filter chỉ reset duy nhất filter.

- - Nếu muốn reset toàn bộ kết quả tìm kiếm thì tìm kiếm thông tin rỗng qua search bar (header).
