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


### Exercise 3.1: Railway deployment
- URL: https://lab-12-production-bdfa.up.railway.app/
- Screenshot: day12-2A202600121-L-u-Quang-L-c\03-cloud.JPG 

###  Exercise 4.1: API Key authentication

**Nhiệm vụ:** Đọc `app.py` và tìm:
- API key được check ở đâu: Dependency function verify_api_key
- Điều gì xảy ra nếu sai key: Raise HTTPException 401
- Làm sao rotate key: Thay đổi biến môi trường AGENT_API_KEY

Test results
PS D:\luc\Luc_Lenovo\Study\AI_thuc_chien_3_10> curl.exe -X POST -H "Content-Type: application/json" "http://localhost:8000/ask?question=Hello"
{"detail":"Missing API key. Include header: X-API-Key: <your-key>"}

PS D:\luc\Luc_Lenovo\Study\AI_thuc_chien_3_10> curl.exe -X POST -H "X-API-Key: my-secret-key" -H "Content-Type: application/json" "http://localhost:8000/ask?question=Hello"
{"question":"Hello","answer":"Agent đang hoạt động tốt! (mock response) Hỏi thêm câu hỏi đi nhé."}

###  Exercise 4.2: JWT authentication (Advanced)
**Nhiệm vụ:** 
1. Đọc `auth.py` — hiểu JWT flow
2. Lấy token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdHVkZW50Iiwicm9sZSI6InVzZXIiLCJpYXQiOjE3NzY0MTk1NjQsImV4cCI6MTc3NjQyMzE2NH0.PjvvLCxrSEW0aB3-L6YU-w7jK-Ee6jnd8qePOxUAhfc

PS D:\luc\Luc_Lenovo\Study\AI_thuc_chien_3_10> curl.exe -X POST "http://localhost:8000/ask" `
>>   -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdHVkZW50Iiwicm9sZSI6InVzZXIiLCJpYXQiOjE3NzY0MTk1NjQsImV4cCI6MTc3NjQyMzE2NH0.PjvvLCxrSEW0aB3-L6YU-w7jK-Ee6jnd8qePOxUAhfc" `
>>   -H "Content-Type: application/json" `
>>   -d '{\"question\": \"Explain JWT\"}'
{"question":"Explain JWT","answer":"Đây là câu trả lời từ AI agent (mock). Trong production, đây sẽ là response từ OpenAI/Anthropic.","usage":{"requests_remaining":9,"budget_remaining_usd":2.1e-05}}

###  Exercise 4.3: Rate limiting

**Nhiệm vụ:** Đọc `rate_limiter.py` và trả lời:
- Algorithm nào được dùng: Sliding Window Counter
- Limit là bao nhiêu requests/minute: 10
- Làm sao bypass limit cho admin: rule-base: limiter = rate_limiter_admin if role == "admin" else rate_limiter_user


--- Request 11 completed ---
{"detail":[{"type":"json_invalid","loc":["body",1],"msg":"JSON decode error","input":{},"ctx":{"error":"Expecting property name enclosed in double quotes"}}]}curl: (3) URL using bad/illegal format or missing URL
curl: (6) Could not resolve host: number
curl: (3) URL using bad/illegal format or missing URL
--- Request 12 completed ---
{"detail":[{"type":"json_invalid","loc":["body",1],"msg":"JSON decode error","input":{},"ctx":{"error":"Expecting property name enclosed in double quotes"}}]}curl: (3) URL using bad/illegal format or missing URL
curl: (6) Could not resolve host: number
curl: (3) URL using bad/illegal format or missing URL
--- Request 13 completed ---
{"detail":[{"type":"json_invalid","loc":["body",1],"msg":"JSON decode error","input":{},"ctx":{"error":"Expecting property name enclosed in double quotes"}}]}curl: (3) URL using bad/illegal format or missing URL
curl: (6) Could not resolve host: number
curl: (3) URL using bad/illegal format or missing URL
--- Request 14 completed ---
{"detail":[{"type":"json_invalid","loc":["body",1],"msg":"JSON decode error","input":{},"ctx":{"error":"Expecting property name enclosed in double quotes"}}]}curl: (3) URL using bad/illegal format or missing URL
curl: (6) Could not resolve host: number
curl: (3) URL using bad/illegal format or missing URL
--- Request 15 completed ---
{"detail":[{"type":"json_invalid","loc":["body",1],"msg":"JSON decode error","input":{},"ctx":{"error":"Expecting property name enclosed in double quotes"}}]}curl: (3) URL using bad/illegal format or missing URL
curl: (6) Could not resolve host: number

### Exercise 4.4: Cost guard implementation
[Lưu budget của user vào Redis để xử lý nhanh nhất, trước khi sử dụng thì check xem user còn bao nhiêu budget, tính toán phần chuẩn bị sử dụng có vượt quá budget không, nếu không thì cho sử dụng, nếu vượt thì trả về lỗi. Sau khi sử dụng thì ghi nhận usage vào Redis.]

### 5.1:
PS D:\luc\Luc_Lenovo\Study\AI_thuc_chien_3_10> curl.exe http://localhost:8000/health
{"status":"ok","uptime_seconds":80.7,"version":"1.0.0","environment":"development","timestamp":"2026-04-17T10:32:45.887230+00:00","checks":{"memory":{"status":"ok","used_percent":62.7}}}
{"ready":true,"in_flight_requests":1}
### 5.2:
INFO:     Shutting down
INFO:     Waiting for application shutdown.
2026-04-17 17:37:18,459 INFO 🔄 Graceful shutdown initiated...
2026-04-17 17:37:18,459 INFO ✅ Shutdown complete
INFO:     Application shutdown complete.
INFO:     Finished server process [18208]
---
## Part 6: Final Project (60 phút)
https://lab12-2a202600121-production-3133.up.railway.app/