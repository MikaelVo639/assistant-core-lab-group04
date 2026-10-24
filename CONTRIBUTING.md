# Quy trình cộng tác nhóm 04

## Bài cá nhân

1. Clone repo nhóm sau khi nhóm trưởng đưa lên GitHub.
2. Từ `main` mới nhất, tạo nhánh `refactor/assistant-core-<ten-khong-dau>`.
3. Làm refactor theo tutorial; chạy test và commit sau mỗi bước.
4. Điền `docs/lab3/before_after.md` trên nhánh cá nhân.
5. Push nhánh, mở PR và nộp link PR của mình lên LMS cuối buổi; draft được chấp nhận theo đề.

## Bản tích hợp của nhóm

Sau khi đủ 6 PR, nhóm review và chọn một bản rõ ràng nhất làm nền.
Không merge cả 6 bản refactor hoàn chỉnh nối tiếp nhau vì chúng thường sửa trùng file.
Đưa các cải tiến cần thiết từ các bản còn lại vào bản nền và ghi nhận đóng góp bằng `Co-authored-by`.

Khi phát triển tiếp bản nền, mỗi thành viên dùng nhánh riêng cho module được giao và mở PR.
Giữ kiểu dữ liệu chung trong `models.py`, ngoại lệ chung trong `errors.py`.
Thống nhất interface trong `docs/architecture.md` trước khi sửa các module phụ thuộc nhau.

## Trước khi merge

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
```

Bản refactor cuối phải có ít nhất 10 test, bao gồm test cho package mới, hành vi cũ và fallback.
Không commit `.venv`, `.env`, khóa API thật hoặc log chứa nội dung người dùng.
Không sửa bản gốc trong `lab03/monolith/` để làm lint/test qua.
Ghi việc dùng AI vào `docs/ai-use-log.md`; không khai khống việc tự review hoặc chỉnh sửa code AI.

## Thiết lập GitHub do nhóm trưởng thực hiện sau khi có remote

- Thêm 5 thành viên còn lại.
- Bảo vệ `main`: yêu cầu PR và ít nhất 1 review nếu tài khoản/gói GitHub hỗ trợ.
- Thêm CI chạy pytest và Ruff; sau đó mới bật yêu cầu các status check tương ứng.
- Chỉ tạo `v0.3-core` khi bản tích hợp đạt checklist bài lab; không tag bản khung hiện tại.
- Hoàn thành bootcamp nhóm rồi mới tạo `py-w3-done`.
