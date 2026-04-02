# VỀ CÔNG CUỘC TEST VÀ BUG FIXES

## Vấn đề

- Khi chương trình có bug và được sửa, phiên bản sửa được up lên github và làm reset lại file settings.py;

- Sau khi pull phiên bản này, người pull phải nhập lại toàn bộ thông tin email host, paypal và ngrok url;

- Điều này rất khó chịu và làm chậm tiến độ kiểm thử.

## Giải pháp

- Sử dụng .env:

- - Bước 1: Kích hoạt venv, chạy lại lệnh: python -m pip install -r requirements.txt; (vì nội dung requirements.txt đã được cập nhật)

- - Bước 2: Tạo file .env ở root (tệp ngoài cùng, chứa file requirements.txt, manage.py, etc);

- - Bước 3: Nhập thông tin email host, paypal client và ngrok giống như khi nhập vào file settings và lưu lại (xem ví dụ VD_env.png).

- CHÚ Ý: File .gitignore và settings.py đã được viết lại để phối hợp với file .env nên không cần đụng tay vào 2 file này.
