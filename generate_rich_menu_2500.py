import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 2500, 1686
base = Image.new("RGB", (W, H), "#040910")
draw = ImageDraw.Draw(base)

# ฟอนต์ไทยขนาดใหญ่พิเศษ ชัดเจน คมกริบ
font_bold_huge = ImageFont.truetype(r"C:\Windows\Fonts\leelawdb.ttf", 108)
font_bold_large = ImageFont.truetype(r"C:\Windows\Fonts\leelawdb.ttf", 88)
font_bold_btn = ImageFont.truetype(r"C:\Windows\Fonts\leelawdb.ttf", 64)
font_bold_btn_sm = ImageFont.truetype(r"C:\Windows\Fonts\leelawdb.ttf", 54)
font_sub = ImageFont.truetype(r"C:\Windows\Fonts\leelawad.ttf", 56)
font_sub_sm = ImageFont.truetype(r"C:\Windows\Fonts\leelawad.ttf", 46)

src_path = r"C:\Users\IKKLASCOM\.gemini\antigravity\brain\f27609f9-1226-49a6-b8a9-f856246f4fc2\.user_uploaded\media_1790189491736.png"
src = Image.open(src_path).convert("RGBA")

def create_soft_icon(cropped_img, target_size):
    """ขยายไอคอนและใส่ feather mask ขอบฟุ้ง เพื่อกลืนเข้ากับพื้นหลังเนียน 100%"""
    resized = cropped_img.resize(target_size, Image.Resampling.LANCZOS)
    w, h = target_size
    mask = Image.new("L", (w, h), 0)
    m_draw = ImageDraw.Draw(mask)
    m_draw.rounded_rectangle((10, 10, w - 10, h - 10), radius=int(min(w, h) * 0.25), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(14))
    
    # รวม alpha
    r, g, b, a = resized.split()
    combined_a = Image.fromarray(np.minimum(np.array(a), np.array(mask)))
    return Image.merge("RGBA", (r, g, b, combined_a))

# ============================================================
# 1. กล่องซ้าย (📢 แจ้งเรื่องร้องเรียน)
# bounds: (28, 28, 1184, 1658)
# ============================================================
b1 = (28, 28, 1184, 1658)
draw.rounded_rectangle(b1, radius=48, fill="#042a1d", outline="#f59e0b", width=8)
b1_inner = (44, 44, 1168, 1642)
draw.rounded_rectangle(b1_inner, radius=40, outline="#fbbf24", width=3)

# ไอคอนลำโพง
raw_mega = src.crop((175, 35, 335, 205))
icon_mega_clean = create_soft_icon(raw_mega, (520, 520))
base.paste(icon_mega_clean, (int(b1[0] + (1156 - 520)/2), 190), icon_mega_clean)

# ข้อความกล่องซ้าย
draw.text((b1[0] + 578, 870), "แจ้งเรื่องร้องเรียน", font=font_bold_huge, fill="#ffffff", anchor="mm")
draw.text((b1[0] + 578, 985), "ส่งรูปภาพ / พิมพ์แจ้งปัญหา", font=font_sub, fill="#86efac", anchor="mm")

# ปุ่มคลิกที่นี่
btn1_rect = (b1[0] + 300, 1130, b1[0] + 856, 1260)
draw.rounded_rectangle(btn1_rect, radius=65, fill="#ffffff")
draw.text((b1[0] + 578, 1195), "คลิกที่นี่", font=font_bold_btn, fill="#047857", anchor="mm")


# ============================================================
# 2. กล่องขวาบน (🤖 แชทบอท AI)
# bounds: (1216, 28, 2472, 828)
# ============================================================
b2 = (1216, 28, 2472, 828)
draw.rounded_rectangle(b2, radius=48, fill="#082343", outline="#38bdf8", width=8)
b2_inner = (1232, 44, 2456, 812)
draw.rounded_rectangle(b2_inner, radius=40, outline="#60a5fa", width=3)

# ไอคอนหุ่นยนต์
raw_bot = src.crop((535, 20, 680, 165))
icon_bot_clean = create_soft_icon(raw_bot, (400, 400))
base.paste(icon_bot_clean, (1270, int(b2[1] + (800 - 400)/2)), icon_bot_clean)

# ข้อความกล่องขวาบน
draw.text((1720, 240), "แชทบอท AI", font=font_bold_large, fill="#ffffff")
draw.text((1720, 360), "สอบถามข้อมูลทั่วไป / อบต.", font=font_sub_sm, fill="#93c5fd")

btn2_rect = (1720, 480, 2260, 600)
draw.rounded_rectangle(btn2_rect, radius=60, fill="#ffffff")
draw.text((1990, 540), "สอบถามที่นี่", font=font_bold_btn_sm, fill="#0369a1", anchor="mm")


# ============================================================
# 3. กล่องขวาล่าง (🌐 เว็บไซต์ อบต.)
# bounds: (1216, 858, 2472, 1658)
# ============================================================
b3 = (1216, 858, 2472, 1658)
draw.rounded_rectangle(b3, radius=48, fill="#230d3e", outline="#c084fc", width=8)
b3_inner = (1232, 874, 2456, 1642)
draw.rounded_rectangle(b3_inner, radius=40, outline="#d8b4fe", width=3)

# ไอคอนเมือง
raw_city = src.crop((545, 200, 680, 350))
icon_city_clean = create_soft_icon(raw_city, (400, 400))
base.paste(icon_city_clean, (1270, int(b3[1] + (800 - 400)/2)), icon_city_clean)

# ข้อความกล่องขวาล่าง
draw.text((1720, 1070), "เว็บไซต์ อบต.", font=font_bold_large, fill="#ffffff")
draw.text((1720, 1190), "ข้อมูลบริการและกิจกรรมต่าง ๆ", font=font_sub_sm, fill="#e9d5ff")

btn3_rect = (1720, 1310, 2260, 1430)
draw.rounded_rectangle(btn3_rect, radius=60, fill="#ffffff")
draw.text((1990, 1370), "เข้าชมที่นี่", font=font_bold_btn_sm, fill="#6b21a8", anchor="mm")

# บันทึกไฟล์ภาพเป็น JPEG คุณภาพสูง
out_path = os.path.join(os.path.dirname(__file__), "rich_menu_2500x1686.jpg")
base.save(out_path, format="JPEG", quality=95)
print(f"Generated successfully: {out_path} ({os.path.getsize(out_path) / 1024:.1f} KB)")
