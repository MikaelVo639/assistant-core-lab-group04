# Đề xuất phân công cho nhóm 6 người

Đây là đề xuất trách nhiệm cho bản tích hợp, chưa gán tên hoặc tạo issue trên GitHub.
Trách nhiệm module không thay thế yêu cầu mỗi người tự refactor và mở PR cá nhân.

| Người | Phạm vi khi hoàn thiện bản tích hợp | Kết quả cần bàn giao |
| --- | --- | --- |
| Nhóm trưởng | `service.py`, `__main__.py`, review và tích hợp | Service/CLI hoạt động, kiến trúc khớp code, bản chung và tag |
| Thành viên 2 | `config.py`, `.env.example`, `.gitignore` | Đọc/kiểm tra cấu hình; test config thiếu/sai; không lộ khóa |
| Thành viên 3 | `models.py`, `errors.py` | Kiểu và ngoại lệ chung; test giới hạn input và validation |
| Thành viên 4 | `knowledge.py`, dữ liệu | CSV/JSON, tìm kiếm và nguồn; test file thiếu/sai |
| Thành viên 5 | `tools.py`, `router.py` | Phân tích tín chỉ, học phí, intent; test biên và hành vi cũ |
| Thành viên 6 | `responder.py`, `logging_setup.py` | Template/stub, JSON logs; test fallback và không lộ dữ liệu |

## Thứ tự phối hợp

1. Thống nhất `models`, `errors` và interface trước để các module không đặt tên khác nhau.
2. Mỗi người làm bài cá nhân đầy đủ trên nhánh riêng; nhóm trưởng thu 6 PR để review.
3. Chọn bản nền; các trách nhiệm trên dùng cho issue cải tiến tiếp theo trên bản nền.
4. Hoàn thiện test service với fallback, CLI, docs, CI rồi mới tạo tag chung.

Người làm module chịu trách nhiệm test module đó; nhóm trưởng kiểm tra tích hợp.
Phân công thêm một thành viên review mỗi PR trước khi merge.
