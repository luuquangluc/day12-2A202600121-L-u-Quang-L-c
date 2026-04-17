import asyncio
import random

# Mock database of coffee shops
CAFE_DATA = {
    "hà nội": [
        {"name": "Cộng Cà Phê", "address": "116 Cầu Gỗ", "specialty": "Cà phê cốt dừa"},
        {"name": "Đinh Café", "address": "13 Đinh Tiên Hoàng", "specialty": "Cà phê trứng"},
        {"name": "Tranquil Books & Coffee", "address": "5 Nguyễn Quang Bích", "specialty": "Không gian yên tĩnh, Hand-brew"},
        {"name": "Xofa Café & Bistro", "address": "14 Tống Duy Tân", "specialty": "Mở cửa 24/7, không gian ấm cúng"}
    ],
    "hồ chí minh": [
        {"name": "The Workshop Coffee", "address": "27 Ngô Đức Kế", "specialty": "Specialty Coffee, không gian công nghiệp"},
        {"name": "L'Usine", "address": "151 Đồng Khởi", "specialty": "Phong cách Pháp, Brunch"},
        {"name": "Ẩu Ơ", "address": "31 Trần Quý Khoách", "specialty": "Vibe Đà Lạt giữa lòng Sài Gòn"},
        {"name": "Little HaNoi Egg Coffee", "address": "119/5 Yersin", "specialty": "Cà phê trứng kiểu Hà Nội"}
    ],
    "đà nẵng": [
        {"name": "43 Factory Coffee Roaster", "address": "Lô 422 Ngô Thì Sỹ", "specialty": "Specialty Coffee, kiến trúc kính"},
        {"name": "Wonderlust", "address": "96 Trần Phú", "specialty": "Không gian trắng tối giản, tích hợp shop"},
        {"name": "Boulevard Gelato & Coffee", "address": "77 Trần Quốc Toản", "specialty": "Kem Ý & Cà phê"}
    ]
}

async def get_cafe_info(city: str) -> str:
    # Simulate some network delay
    await asyncio.sleep(0.5)
    
    city_key = city.lower().strip()
    
    # Try to find a match in the keys
    matching_city = None
    for key in CAFE_DATA.keys():
        if key in city_key or city_key in key:
            matching_city = key
            break
            
    if not matching_city:
        return f"Hiện tại tôi chưa có dữ liệu quán cafe tại {city}. Bạn có thể thử tìm ở Hà Nội, Hồ Chí Minh hoặc Đà Nẵng nhé!"
        
    cafes = CAFE_DATA[matching_city]
    # Pick a random recommendation or return all? Let's return a nice formatted string of all.
    result = f"Gợi ý các quán cafe nổi bật tại {city}:\n"
    for idx, cafe in enumerate(cafes, 1):
        result += f"{idx}. {cafe['name']} - {cafe['address']} (Đặc sắc: {cafe['specialty']})\n"
        
    return result.strip()
