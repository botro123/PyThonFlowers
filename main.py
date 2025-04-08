from fastapi import FastAPI
# 1. Import CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware
from config.db import engine, Base
from routers import users
from routers.flowers import router as flowers_router

app = FastAPI()

# --- Cấu hình CORS ---
# 2. Định nghĩa danh sách các origins được phép truy cập API của bạn.
#    Bạn nên liệt kê cụ thể các địa chỉ frontend của mình thay vì dùng "*" trong môi trường production.
origins = [
    "http://localhost", # Nếu frontend chạy trên localhost
    "http://localhost:8080", # Ví dụ cổng frontend phổ biến
    "http://localhost:5173", # Ví dụ cổng frontend React/Vue/Angular
    "https://your-frontend-domain.com", # Domain của frontend khi deploy
    # Thêm các origin khác nếu cần
    # "*" # Cho phép TẤT CẢ các origins (chỉ nên dùng khi phát triển, không an toàn cho production)
]

# 3. Thêm CORSMiddleware vào ứng dụng FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # Cho phép các origins được định nghĩa ở trên
    allow_credentials=True, # Cho phép gửi cookie và thông tin xác thực (authentication headers)
    allow_methods=["*"], # Cho phép tất cả các phương thức HTTP (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"], # Cho phép tất cả các header trong yêu cầu
)
# --- Kết thúc cấu hình CORS ---

# Khởi tạo cơ sở dữ liệu
Base.metadata.create_all(bind=engine)

# Đăng ký router
app.include_router(users.user)
app.include_router(flowers_router)

# (Optional) Bạn có thể thêm một route gốc để kiểm tra nhanh
# @app.get("/")
# async def read_root():
#     return {"message": "API is running with CORS enabled!"}