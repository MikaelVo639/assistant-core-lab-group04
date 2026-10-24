# Kiến trúc đích của assistant_core

Trạng thái: thiết kế theo tutorial Lab 03, chưa triển khai ngoài khung package.

## 1. Trách nhiệm từng module

| Module | Trách nhiệm |
| --- | --- |
| `config.py` | Đọc và kiểm tra cấu hình từ môi trường / `.env` |
| `errors.py` | `AssistantError`, `ConfigError`, `DataError`, `InvalidRequest`, `ProviderError` |
| `models.py` | Các kiểu công khai `Message`, `Response`, `Intent`, `Source` |
| `router.py` | Chọn intent theo quy tắc |
| `knowledge.py` | Nạp CSV/JSON, tra phòng ban và tìm quy định |
| `tools.py` | Phân tích số tín chỉ và tính học phí một cách xác định |
| `responder.py` | Protocol `Responder`, template và stub AI |
| `service.py` | Kết nối các thành phần; điểm vào chung cho caller |
| `logging_setup.py` | JSON logs tới stderr, không lộ khóa hoặc toàn bộ câu hỏi |
| `__main__.py` | CLI; câu trả lời ra stdout |

## 2. Service interface

```python
AssistantService.handle(msg: Message) -> Response
```

- `Message`: `text` dài 1-2000 ký tự; `session_id` mặc định `local`.
- `Response`: `answer`, `intent`, `sources: list[Source]`, `degraded: bool`.
- `Source`: `id`, `title`.
- `Intent`: `greeting`, `fee`, `office`, `rule`, `unknown`.
- Input sai được Pydantic từ chối ở boundary.
- Cấu hình hoặc file dữ liệu sai làm startup thất bại bằng lỗi có tên.
- `ProviderError` dùng template fallback; giữ nguồn và đặt `degraded=True`.

## 3. Ba quyết định thiết kế ban đầu

1. Học phí nằm trong hàm thuần ở `tools.py`: kết quả chính xác, dễ test, không do LLM tính.
2. Provider ở sau `Responder` và được truyền vào service: thay provider hoặc giả lập lỗi mà không sửa service.
3. Cấu hình đến từ môi trường, mô tả bằng `.env.example`: không cần sửa code hoặc commit khóa thật.

Khi triển khai, nhóm cập nhật tài liệu để phản ánh code thực tế và ghi lại các quyết định thay đổi.
