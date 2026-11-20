# ============================================================
# 🤖 LINE Rich Menu Setup (100% Match Custom Design - Full Size 2500x1686)
# สคริปต์ปรับขนาดภาพริชเมนูต้นฉบับของผู้ใช้ให้เป็นขนาดมาตรฐานแบบเต็มจอ (2500x1686)
# ปุ่มมีความสูงและขนาดใหญ่ ชัดเจน อ่านง่าย กดสะดวก ตามเส้นแบ่งความสูงใหม่
#
# ส่วนที่ 1 (ซ้ายเต็ม): 📢 แจ้งเรื่องร้องเรียน (ส่งรูปภาพ/พิมพ์แจ้งปัญหา)
# ส่วนที่ 2 (ขวาบน): 🤖 แชทบอท AI (สอบถามข้อมูลทั่วไป / เทศบาล)
# ส่วนที่ 3 (ขวาล่าง): 🌐 เว็บไซต์ / อื่นๆ (ข้อมูลบริการและกิจกรรมต่าง ๆ)
# ============================================================

import os
import requests
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

# ขนาดมาตรฐานตามข้อกำหนดของ LINE Rich Menu (Full Size ขนาดใหญ่เต็มจอ)
WIDTH = 2500
HEIGHT = 1686

# ตำแหน่งไฟล์รูปต้นฉบับใหม่ที่ผู้ใช้อัปโหลด (ขนาดสัดส่วนปุ่มสูงใหญ่ 1024x686)
SOURCE_IMAGE_PATH = r"C:\Users\IKKLASCOM\.gemini\antigravity\brain\f27609f9-1226-49a6-b8a9-f856246f4fc2\.user_uploaded\media_1792660550623_5ce8e1c4.jpg"
OUTPUT_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "rich_menu_custom.jpg")

# URL เว็บไซต์สำหรับปุ่มเว็บไซต์/อื่นๆ (ดึงจาก .env)
WEBSITE_URL = os.getenv("OBT_WEBSITE_URL", "http://www.munok.go.th")


def prepare_rich_menu_image():
    """
    ปรับขนาดภาพจากต้นฉบับของผู้ใช้ให้เป็น 2500x1686 พิกเซล พอดี 100%
    และบันทึกเป็น JPEG คุณภาพสูง (quality=92) เพื่อให้อยู่ในเกณฑ์ < 1MB ของ LINE API
    """
    if not os.path.exists(SOURCE_IMAGE_PATH):
        raise FileNotFoundError(f"ไม่พบไฟล์ภาพต้นฉบับที่: {SOURCE_IMAGE_PATH}")

    img = Image.open(SOURCE_IMAGE_PATH).convert("RGB")
    resized_img = img.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
    resized_img.save(OUTPUT_IMAGE_PATH, format="JPEG", quality=92, optimize=True)
    file_size_kb = os.path.getsize(OUTPUT_IMAGE_PATH) / 1024
    print(f"✅ บันทึกและปรับขนาดภาพ Rich Menu สำเร็จ: {OUTPUT_IMAGE_PATH} ({file_size_kb:.1f} KB)")
    return OUTPUT_IMAGE_PATH


def setup_line_rich_menu():
    """
    ส่งข้อมูล Rich Menu ขึ้น LINE API และตั้งเป็นเมนูหลักสำหรับทุกคน
    """
    if not LINE_CHANNEL_ACCESS_TOKEN:
        print("❌ ไม่พบ LINE_CHANNEL_ACCESS_TOKEN ใน .env")
        return

    headers = {
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    # 1. ลบริชเมนูเก่าทั้งหมดก่อน เพื่อให้ใช้เมนูใหม่ล่าสุดเท่านั้น
    print("🔄 กำลังตรวจสอบและลบริชเมนูเก่า...")
    res = requests.get("https://api.line.me/v2/bot/richmenu/list", headers=headers)
    if res.status_code == 200:
        for menu in res.json().get("richmenus", []):
            rm_id = menu["richMenuId"]
            del_res = requests.delete(f"https://api.line.me/v2/bot/richmenu/{rm_id}", headers=headers)
            print(f"🗑️ ลบเมนูเก่า: {rm_id} (สถานะ: {del_res.status_code})")

    # 2. กำหนดพิกัดทั้ง 3 ส่วนตามสัดส่วนภาพต้นฉบับ 2500x1686
    # เส้นแบ่งแนวตั้งอยู่ที่ x = 1292 (ซ้าย 1292px, ขวา 1208px)
    # เส้นแบ่งแนวนอนฝั่งขวาอยู่ที่ y = 845 (บน 845px, ล่าง 841px)
    payload = {
        "size": {"width": WIDTH, "height": HEIGHT},
        "selected": True,
        "name": "CustomMainMenuTall1686",
        "chatBarText": "เมนูหลัก",
        "areas": [
            # โซน 1: ซ้ายเต็ม - แจ้งเรื่องร้องเรียน (สูง 1686px)
            {
                "bounds": {"x": 0, "y": 0, "width": 1292, "height": HEIGHT},
                "action": {
                    "type": "message",
                    "label": "แจ้งเรื่องร้องเรียน",
                    "text": "แจ้งเรื่องร้องเรียน"
                }
            },
            # โซน 2: ขวาบน - แชทบอท AI (สูง 845px)
            {
                "bounds": {"x": 1292, "y": 0, "width": 1208, "height": 845},
                "action": {
                    "type": "message",
                    "label": "แชทบอท AI",
                    "text": "สอบถามข้อมูล"
                }
            },
            # โซน 3: ขวาล่าง - เว็บไซต์ / อื่นๆ (สูง 841px)
            {
                "bounds": {"x": 1292, "y": 845, "width": 1208, "height": 841},
                "action": {
                    "type": "message",
                    "label": "เว็บไซต์ / อื่นๆ",
                    "text": "เว็บไซต์ อบต."
                }
            }
        ]
    }

    print("📤 กำลังส่งโครงสร้าง Rich Menu แบบสูงใหญ่ (2500x1686) ไปยัง LINE API...")
    create_res = requests.post("https://api.line.me/v2/bot/richmenu", headers=headers, json=payload)
    if create_res.status_code != 200:
        print("❌ สร้าง Rich Menu ไม่สำเร็จ:", create_res.status_code, create_res.text)
        return

    rich_menu_id = create_res.json()["richMenuId"]
    print("✅ สร้าง Rich Menu โครงสร้างสำเร็จ ID:", rich_menu_id)

    # 3. อัปโหลดรูปภาพไปยัง Rich Menu
    img_path = prepare_rich_menu_image()
    upload_headers = {
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
        "Content-Type": "image/jpeg"
    }

    print("🖼️ กำลังอัปโหลดรูปภาพ 2500x1686 ไปยัง LINE API...")
    with open(img_path, "rb") as f:
        upload_res = requests.post(
            f"https://api-data.line.me/v2/bot/richmenu/{rich_menu_id}/content",
            headers=upload_headers,
            data=f.read()
        )

    if upload_res.status_code != 200:
        print("❌ อัปโหลดภาพไม่สำเร็จ:", upload_res.status_code, upload_res.text)
        return

    print("✅ อัปโหลดภาพสำเร็จ")

    # 4. ตั้งเป็น Default Rich Menu ให้ทุกคนเห็นทันที
    print("🚀 กำลังตั้งเป็น Default Rich Menu ให้กับผู้ใช้ทุกคน...")
    set_default_res = requests.post(
        f"https://api.line.me/v2/bot/user/all/richmenu/{rich_menu_id}",
        headers=headers
    )

    if set_default_res.status_code == 200:
        print("🎉 สำเร็จ 100%! ตั้งเป็น Default Rich Menu แบบสูงใหญ่เรียบร้อยแล้ว")
        print(f"🔑 Rich Menu ID ปัจจุบัน: {rich_menu_id}")
        print("📱 กรุณาเปิดแอป LINE บนมือถือ เพื่อดูริชเมนูโฉมใหม่แบบสูงใหญ่ได้ทันทีครับ!")
    else:
        print("❌ ตั้งค่า Default ไม่สำเร็จ:", set_default_res.status_code, set_default_res.text)


if __name__ == "__main__":
    setup_line_rich_menu()
