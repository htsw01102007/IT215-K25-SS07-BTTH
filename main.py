from fastapi import FastAPI, status, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

# --- 1. Dữ liệu và Schema ---
promo_codes_db = {
    "SUMMER25": {"code": "SUMMER25", "discount_rate": 0.15, "max_budget": 50000000, "is_active": True},
    "WELCOME50": {"code": "WELCOME50", "discount_rate": 0.50, "max_budget": 10000000, "is_active": False}
}

class PromoPublic(BaseModel):
    code: str
    discount_rate: float

# --- 2. Global Exception Handler (Cấu trúc Envelope) ---
@app.exception_handler(HTTPException)
async def global_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "statusCode": exc.status_code,
            "data": None,
            "error": exc.detail,
            "message": "Có lỗi xảy ra trong quá trình xử lý.",
            "timestamp": datetime.now().isoformat(),
            "path": request.url.path
        }
    )

# --- 3. Endpoint Tra cứu ---
@app.get("/promos/{code}", response_model=PromoPublic)
def get_promo(code: str):
    # Kiểm tra tồn tại
    promo = promo_codes_db.get(code)
    if not promo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Mã giảm giá không tồn tại"
        )
    
    # Kiểm tra trạng thái hoạt động
    if not promo["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Mã giảm giá đã hết hạn sử dụng"
        )
    
    # Nếu hợp lệ: Pydantic response_model sẽ tự động lọc chỉ trả về code và discount_rate
    return promo
