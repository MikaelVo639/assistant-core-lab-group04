# assistant-core-lab-group04

Repo mới của nhóm 04 cho CSC10014 Lab 03: Engineering a Maintainable Python Service.

## Trạng thái hiện tại

- Đã nhập nguyên trạng code và worksheet của môn vào `lab03/`.
- Đã tạo khung package, dữ liệu làm việc, cấu hình thư viện và template môi trường.
- Có 9 test ghi lại hành vi của code gốc, chạy offline và không phụ thuộc lỗi AI ngẫu nhiên.
- Chưa triển khai các module refactor hoặc CLI của `assistant_core`.
- Chưa tạo repo GitHub, cấu hình remote, branch protection, CI hoặc tag hoàn thành.

Các test hiện tại chỉ bảo vệ bản gốc. Chúng chưa chứng minh package refactor đạt yêu cầu Lab 03.
Xem `docs/lab3/progress.md` để biết phần còn lại.

## Chạy trên Windows PowerShell

Chạy tại thư mục gốc repo. Máy đã được chuẩn bị có thể dùng trực tiếp Python trong `.venv`:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe lab03\monolith\assistant_monolith.py --test
```

Khi clone sang máy khác, dùng Python 3.10 trở lên để tạo môi trường riêng:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install -e .
```

Không cần activate môi trường hoặc đổi PowerShell execution policy.
`.env.example` là mẫu cho module cấu hình sắp triển khai; nếu cần, copy thành `.env`.
Script gốc chưa đọc các biến trong `.env`.

## Cấu trúc

```text
lab03/                  # Bản gốc của môn, giữ nguyên để đối chiếu
data/                   # CSV/JSON cho package mới
src/assistant_core/     # Hiện mới có __init__.py
tests/                  # Characterisation tests của monolith
docs/architecture.md    # Thiết kế đích, chưa phải mô tả code hoàn thiện
docs/lab3/              # Worksheet, tiến độ và đề xuất phân công
docs/ai-use-log.md      # Ghi nhận việc dùng AI khi khởi tạo
UPSTREAM.md             # Nguồn và commit gốc
CONTRIBUTING.md         # Quy trình nhánh và PR
```

Ruff bỏ qua `lab03/monolith/` vì đây là ví dụ cố ý có lỗi cần giữ nguyên.
Ruff vẫn kiểm tra `src/` và `tests/`; không dùng việc lint bản khung sạch để kết luận lab đã xong.

## Làm việc theo nhóm

Mỗi người tạo nhánh cá nhân `refactor/assistant-core-<ten>`, hoàn thành refactor và mở PR.
Không push trực tiếp vào `main` sau khi nhóm bắt đầu làm việc.
Đề xuất chia trách nhiệm bản tích hợp cho 6 người nằm ở `docs/lab3/team-plan.md`.
Mỗi người vẫn phải có bài cá nhân, worksheet và bài AI extension riêng.

## Nguồn

[Lab 03 - public_materials](https://github.com/CSC10014-at-fit-hcmus/public_materials/tree/main/lab03).
Chi tiết phiên bản và xác minh file xem `UPSTREAM.md`.
