#  Delivery Checklist — Day 12 Lab Submission

> **Student Name:** Lưu Quang Lực 
> **Student ID:** 2A202600121 
> **Date:** 17/4/2026

---

##  Submission Requirements

Submit a **GitHub repository** containing:

### 1. Mission Answers (40 points)

Create a file `MISSION_ANSWERS.md` with your answers to all exercises:

```markdown
# Day 12 Lab - Mission Answers

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found
1. Lộ API_KEY, địa chỉ DB
2. Không có file config riêng mà config vào file app
3. Không có try...except
4. Không có ratelimit
5. Không có health check
6. Port cố định
7. Không có logging
8. Không có graceful shutdown
...

### Exercise 1.3: Comparison table
| Feature | Develop | Production | Why Important? |
|---------|---------|------------|----------------|
| Config  | Hardcoded trong code | Environment Variables (.env) | Bảo mật secrets (API Key) và dễ thay đổi cấu hình mà không cần sửa code. |
| Logging | print() thông thường | Structured JSON Logging | Giúp các hệ thống quản lý log (như Datadog, ELK) dễ thu thập và phân tích lỗi. |
| Health Check | Không có | Endpoint /health, /ready | Để Cloud Platform (Railway/Docker) biết khi nào Agent bị treo để tự động khởi động lại. |
| Server Bind | localhost (127.0.0.1) | 0.0.0.0 | Để ứng dụng có thể "nói chuyện" với thế giới bên ngoài khi nằm trong Docker container. |
| Shutdown | Tắt đột ngột (Ctrl+C) | Graceful Shutdown (hứng SIGTERM) | Đảm bảo Agent hoàn thành các request đang xử lý dở trước khi thực sự tắt hẳn, tránh mất dữ liệu. |

###  Exercise 2.1: Dockerfile cơ bản

```bash
cd ../../02-docker/develop
```

**Nhiệm vụ:** Đọc `Dockerfile` và trả lời:

1. Base image là phiên bản Python tinh giản giúp giảm kích thước Image đáng kể so với bản full
2. Working directory là nơi chứa toàn bộ mã nguồn và dependencies của ứng dụng được đặt và chạy trong thư mục này bên trong container
3. Tại sao COPY requirements.txt trước: Việc cài đặt thư viện (pip install) thường tốn nhiều thời gian nhất. Bằng cách copy file requirements.txt và chạy pip install trước khi copy toàn bộ source code, Docker sẽ lưu lại tầng này (cache). Lần sau, nếu bạn chỉ sửa logic code mà không thêm thư viện mới, Docker sẽ bỏ qua bước cài đặt và lấy luôn kết quả từ cache, giúp quá trình Build image nhanh hơn gấp nhiều lần.
4. ENTRYPOINT: Định nghĩa lệnh chính sẽ luôn chạy khi khởi tạo container. Nó biến container của bạn giống như một "file thực thi". Rất khó để bị ghi đè khi chạy lệnh docker run, CMD: Cung cấp các tham số mặc định cho ENTRYPOINT hoặc lệnh chạy mặc định. CMD cực kỳ linh hoạt và rất dễ bị ghi đè.


###  Exercise 2.3: Multi-stage build

**Nhiệm vụ:** Đọc `Dockerfile` và tìm:
- Stage 1 làm gì: Đây là môi trường "Xây dựng". Nó cài đặt đầy đủ các công cụ cần thiết để biên dịch (compile) các thư viện Python, ví dụ như gcc, libpq-dev
- Stage 2 làm gì: Đây là môi trường "Sản phẩm". Nó chỉ chứa runtime cần thiết (Python + thư viện đã cài). Nó copy kết quả từ Stage 1 sang.
- Tại sao image nhỏ hơn: Vì Stage 2 không chứa các công cụ build (như gcc) và các file tạm, chỉ chứa runtime cần thiết. Nó sử dụng bản python:3.11-slim nhẹ hơn bản python:3.11 rất nhiều.
