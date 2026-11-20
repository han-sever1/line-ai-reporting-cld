# ฟังก์ชันตอบกลับ LINE
import os
from datetime import datetime
import requests
from dotenv import load_dotenv

load_dotenv()

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")


def reply_message(reply_token, text, access_token: str = None):
    """
    ส่งข้อความตอบกลับไปยัง LINE
    ใช้ replyToken ที่ LINE ส่งมากับ Webhook
    """
    url = "https://api.line.me/v2/bot/message/reply"
    token = (access_token and access_token.strip()) or LINE_CHANNEL_ACCESS_TOKEN

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "replyToken": reply_token,
        "messages": [
            {
                "type": "text",
                "text": text
            }
        ]
    }

    response = requests.post(url, headers=headers, json=payload)

    return response.status_code, response.text


def reply_flex_message(reply_token: str, alt_text: str, flex_contents: dict, access_token: str = None, quick_reply_items: list = None):
    """
    ส่งข้อความแบบ Flex Message ตอบกลับผ่าน replyToken
    รองรับการแนบ Quick Reply items ด้านล่างเพื่อความสะดวก
    """
    url = "https://api.line.me/v2/bot/message/reply"
    token = (access_token and access_token.strip()) or LINE_CHANNEL_ACCESS_TOKEN

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    message_payload = {
        "type": "flex",
        "altText": alt_text,
        "contents": flex_contents
    }

    if quick_reply_items:
        message_payload["quickReply"] = {
            "items": quick_reply_items
        }

    payload = {
        "replyToken": reply_token,
        "messages": [message_payload]
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200 and access_token and access_token.strip() != LINE_CHANNEL_ACCESS_TOKEN:
        headers["Authorization"] = f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
        response = requests.post(url, headers=headers, json=payload)
    return response.status_code, response.text


# ============================================================
# 🤖 LINE Quick Reply Service
# ฟังก์ชันส่งข้อความตอบกลับพร้อมปุ่ม Quick Reply ให้ผู้ใช้เลือกง่ายๆ
# ============================================================

def reply_quick_reply(reply_token, text, quick_reply_items, access_token: str = None):
    """
    ส่งข้อความตอบกลับไปยัง LINE พร้อมปุ่ม Quick Reply ด้านล่าง
    quick_reply_items เป็น list ของ action เช่น:
    [
        {"type": "action", "action": {"type": "message", "label": "ข้าม", "text": "ข้าม"}},
        {"type": "action", "action": {"type": "location", "label": "แชร์พิกัด"}}
    ]
    """
    url = "https://api.line.me/v2/bot/message/reply"
    token = (access_token and access_token.strip()) or LINE_CHANNEL_ACCESS_TOKEN

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "replyToken": reply_token,
        "messages": [
            {
                "type": "text",
                "text": text,
                "quickReply": {
                    "items": quick_reply_items
                }
            }
        ]
    }

    response = requests.post(url, headers=headers, json=payload)
    return response.status_code, response.text

# ============================================================
# จบ LINE Quick Reply Service
# ============================================================
# เพิ่มฟังก์ชันดาวน์โหลดรูปจาก LINE
def download_line_image(message_id: str, save_path: str):
    """
    ดาวน์โหลดรูปภาพจาก LINE ด้วย message_id

    LINE ไม่ได้ส่งไฟล์รูปมาให้โดยตรง
    แต่จะส่งแค่ message_id มาให้

    เราต้องใช้ message_id ไปขอดาวน์โหลดรูปจาก LINE API
    แล้วบันทึกไว้ในเครื่อง
    """

    url = f"https://api-data.line.me/v2/bot/message/{message_id}/content"

    headers = {
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }

    response = requests.get(url, headers=headers, timeout=20)

    if response.status_code == 200:
        with open(save_path, "wb") as file:
            file.write(response.content)

        return True

    print("Download image failed:", response.status_code, response.text)
    return False

##
def push_message(user_id: str, text: str):
    """
    ส่งข้อความหา user โดยตรงผ่าน LINE

    ใช้ตอนเจ้าหน้าที่เปลี่ยนสถานะใน Dashboard
    แล้วระบบต้องแจ้งกลับไปหาประชาชนอัตโนมัติ

    ต่างจาก reply_message:
    - reply_message ใช้ตอบกลับทันทีตอน user ส่งข้อความมา
    - push_message ใช้ส่งหา user ทีหลังได้
    """

    url = "https://api.line.me/v2/bot/message/push"

    headers = {
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "to": user_id,
        "messages": [
            {
                "type": "text",
                "text": text
            }
        ]
    }

    response = requests.post(url, headers=headers, json=payload)

    print("LINE push status:", response.status_code)
    print("LINE push response:", response.text)

    return response.status_code, response.text



# ============================================================
# 🤖 AI Verification Flex Card (Use Case 10: ยืนยัน/แก้ไขผลวิเคราะห์)
# ============================================================

def build_ai_verification_flex_card(data: dict) -> dict:
    """
    สร้างการ์ด Flex Message สวยงาม ให้ประชาชนตรวจสอบและยืนยันข้อมูล
    หลัง AI วิเคราะห์เสร็จสิ้น (Use Case 10)
    ประกอบด้วย:
    - หมวดหมู่ปัญหาที่ AI จำแนก
    - หน่วยงานที่รับผิดชอบ
    - ระดับความเร่งด่วน พร้อม Badge สี
    - รายละเอียดที่แจ้ง
    - พิกัด GPS และสถานะรูปภาพ
    - ปุ่ม '✅ ยืนยันการแจ้งเหตุ', '✏️ แก้ไขประเภทปัญหา', '❌ ยกเลิก'
    """
    category = data.get("category") or data.get("problem_type") or "อื่นๆ"
    department = data.get("department") or data.get("ai_department") or "สำนักปลัด"
    priority = data.get("priority") or "ปกติ"
    priority_score = data.get("priority_score", 0)
    description = data.get("description") or "-"
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    has_image = data.get("has_image", False)

    # กำหนดสี Badge ตามระดับความเร่งด่วน
    if priority == "เร่งด่วน":
        badge_bg = "#FEE2E2"
        badge_color = "#DC2626"
    elif priority == "ปานกลาง":
        badge_bg = "#FEF3C7"
        badge_color = "#D97706"
    else:
        badge_bg = "#DBEAFE"
        badge_color = "#1D4ED8"

    try:
        lat_f = float(latitude) if latitude is not None else 0.0
        lng_f = float(longitude) if longitude is not None else 0.0
        loc_text = f"{lat_f:.5f}, {lng_f:.5f}" if (lat_f != 0 and lng_f != 0) else "-"
    except Exception:
        loc_text = f"{latitude}, {longitude}" if (latitude and longitude) else "-"

    image_status_text = "มีรูปภาพประกอบ 📷" if has_image else "ไม่มีรูปภาพ (ข้าม)"

    body_contents = [
        # แถวหมวดหมู่ปัญหา และ Badge ความสำคัญ
        {
            "type": "box",
            "layout": "horizontal",
            "alignItems": "center",
            "contents": [
                {
                    "type": "box",
                    "layout": "vertical",
                    "flex": 4,
                    "contents": [
                        {
                            "type": "text",
                            "text": "หมวดหมู่ปัญหาที่ตรวจพบ",
                            "color": "#64748B",
                            "size": "xs"
                        },
                        {
                            "type": "text",
                            "text": f"📌 {category}",
                            "weight": "bold",
                            "size": "md",
                            "color": "#0F172A",
                            "wrap": True
                        }
                    ]
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "backgroundColor": badge_bg,
                    "cornerRadius": "6px",
                    "paddingStart": "8px",
                    "paddingEnd": "8px",
                    "paddingTop": "4px",
                    "paddingBottom": "4px",
                    "contents": [
                        {
                            "type": "text",
                            "text": f"ระดับ: {priority}",
                            "color": badge_color,
                            "size": "xs",
                            "weight": "bold"
                        }
                    ]
                }
            ]
        },
        # หน่วยงานผู้รับผิดชอบ
        {
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {
                    "type": "text",
                    "text": "🏢 หน่วยงานรับผิดชอบ:",
                    "color": "#64748B",
                    "size": "xs",
                    "flex": 2
                },
                {
                    "type": "text",
                    "text": department,
                    "color": "#1E40AF",
                    "size": "xs",
                    "weight": "bold",
                    "flex": 3
                }
            ]
        },
        {"type": "separator"},
        # รายละเอียดปัญหา
        {
            "type": "box",
            "layout": "vertical",
            "spacing": "xs",
            "contents": [
                {
                    "type": "text",
                    "text": "📝 รายละเอียดที่แจ้ง:",
                    "color": "#64748B",
                    "size": "xs",
                    "weight": "bold"
                },
                {
                    "type": "text",
                    "text": str(description),
                    "color": "#334155",
                    "size": "sm",
                    "wrap": True
                }
            ]
        },
        {"type": "separator"},
        # พิกัดและรูปถ่าย
        {
            "type": "box",
            "layout": "vertical",
            "spacing": "xs",
            "contents": [
                {
                    "type": "text",
                    "text": f"📍 พิกัดตำแหน่ง: {loc_text}",
                    "color": "#64748B",
                    "size": "xxs"
                },
                {
                    "type": "text",
                    "text": f"📷 ภาพถ่าย: {image_status_text}",
                    "color": "#64748B",
                    "size": "xxs"
                }
            ]
        }
    ]

    bubble = {
        "type": "bubble",
        "size": "mega",
        "header": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": "#1E3A8A",
            "paddingAll": "16px",
            "contents": [
                {
                    "type": "text",
                    "text": "🤖 ผลการวิเคราะห์เรื่องร้องเรียนโดย AI",
                    "color": "#93C5FD",
                    "weight": "bold",
                    "size": "xs"
                },
                {
                    "type": "text",
                    "text": "กรุณาตรวจสอบข้อมูลก่อนยืนยัน",
                    "color": "#FFFFFF",
                    "weight": "bold",
                    "size": "md",
                    "margin": "xs"
                }
            ]
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "paddingAll": "16px",
            "spacing": "md",
            "contents": body_contents
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "paddingAll": "14px",
            "contents": [
                {
                    "type": "button",
                    "style": "primary",
                    "color": "#059669",
                    "height": "sm",
                    "action": {
                        "type": "message",
                        "label": "✅ ยืนยันการแจ้งเหตุ",
                        "text": "ยืนยันการแจ้งเหตุ"
                    }
                },
                {
                    "type": "button",
                    "style": "primary",
                    "color": "#D97706",
                    "height": "sm",
                    "action": {
                        "type": "message",
                        "label": "✏️ แก้ไขประเภทปัญหา",
                        "text": "แก้ไขประเภทปัญหา"
                    }
                },
                {
                    "type": "button",
                    "style": "link",
                    "color": "#DC2626",
                    "height": "sm",
                    "action": {
                        "type": "message",
                        "label": "❌ ยกเลิกการแจ้งเรื่อง",
                        "text": "ยกเลิก"
                    }
                }
            ]
        }
    }

    return bubble


# ============================================================
# 🤖 LINE Department Notification Service (แจ้งเตือนไลน์หน่วยงาน)
# ============================================================

def build_department_flex_card(ticket_data: dict) -> dict:
    """
    สร้างการ์ด Flex Message สวยงามสำหรับแจ้งเตือนหน่วยงาน
    - แสดงเลขอ้างอิง, หน่วยงาน, หมวดหมู่, รายละเอียด
    - พิกัด GPS พร้อมปุ่มกดนำทาง Google Maps
    - ปุ่ม '✅ ยืนยันรับเรื่อง' สลับเป็น '❌ ยกเลิกรับเรื่อง' เมื่อกดรับแล้ว (ไม่มี displayText)
    - ปุ่มสถานะ '⏳ รอแก้ไข', '⚙️ กำลังทำ', '🎉 ดำเนินการเสร็จสิ้น' (ไม่มี displayText)
    """
    ticket_id = ticket_data.get("ticket_id", "TK-0000")
    department = ticket_data.get("department") or ticket_data.get("ai_department") or "สำนักปลัด"
    category = ticket_data.get("category") or ticket_data.get("nlp_category") or ticket_data.get("model_b_class") or "ทั่วไป"
    priority = ticket_data.get("priority", "ปกติ")
    priority_score = ticket_data.get("priority_score", 0)
    description = ticket_data.get("description", "-")
    latitude = ticket_data.get("latitude")
    longitude = ticket_data.get("longitude")
    image_path = ticket_data.get("image_path")
    created_at = ticket_data.get("created_at") or datetime.now().strftime("%d/%m/%Y %H:%M น.")
    status = ticket_data.get("status", "รอดำเนินการ")
    accepted_by = ticket_data.get("accepted_by")
    accepted_at = ticket_data.get("accepted_at")
    status_reason = ticket_data.get("status_reason")

    # กำหนดสีและธีมตามสถานะ หรือระดับความเร่งด่วน
    if status == "ยกเลิก":
        header_bg = "#DC2626"  # แดง
        header_title = "❌ ยกเลิกเรื่องร้องเรียนแล้ว"
        badge_bg = "#FEE2E2"
        badge_color = "#DC2626"
        badge_text = "ยกเลิกแล้ว"
    elif status == "ดำเนินการเสร็จสิ้น":
        header_bg = "#059669"  # เขียว
        header_title = "🎉 แก้ไขปัญหาเสร็จสิ้นแล้ว"
        badge_bg = "#D1FAE5"
        badge_color = "#065F46"
        badge_text = "เสร็จสิ้น"
    elif status == "กำลังดำเนินการ":
        header_bg = "#2563EB"  # ฟ้าเข้ม
        header_title = "⚙️ กำลังดำเนินการแก้ไข"
        badge_bg = "#DBEAFE"
        badge_color = "#1D4ED8"
        badge_text = "กำลังทำ"
    elif status == "รอแก้ไข":
        header_bg = "#D97706"  # ส้ม
        header_title = "⏳ อยู่ระหว่างรอแก้ไข"
        badge_bg = "#FEF3C7"
        badge_color = "#B45309"
        badge_text = "รอแก้ไข"
    elif accepted_by:
        header_bg = "#0D9488"  # เขียวน้ำทะเล
        header_title = "📥 หน่วยงานรับเรื่องแล้ว"
        badge_bg = "#CCFBF1"
        badge_color = "#0F766E"
        badge_text = f"ระดับ: {priority}"
    else:
        header_title = "🚨 มีเรื่องร้องเรียนใหม่เข้าสู่ระบบ"
        if priority == "เร่งด่วน":
            header_bg = "#DC2626"  # แดง
            badge_bg = "#FEE2E2"
            badge_color = "#DC2626"
        elif priority == "ปานกลาง":
            header_bg = "#D97706"  # ส้ม
            badge_bg = "#FEF3C7"
            badge_color = "#D97706"
        else:
            header_bg = "#2563EB"  # ฟ้า-น้ำเงิน
            badge_bg = "#DBEAFE"
            badge_color = "#1D4ED8"
        badge_text = f"ระดับ: {priority}"

    body_contents = [
        {
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {
                    "type": "text",
                    "text": f"🎫 {ticket_id}",
                    "weight": "bold",
                    "size": "lg",
                    "color": "#1E293B",
                    "flex": 1
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "backgroundColor": badge_bg,
                    "cornerRadius": "6px",
                    "paddingStart": "8px",
                    "paddingEnd": "8px",
                    "paddingTop": "3px",
                    "paddingBottom": "3px",
                    "contents": [
                        {
                            "type": "text",
                            "text": badge_text,
                            "color": badge_color,
                            "size": "xs",
                            "weight": "bold"
                        }
                    ]
                }
            ]
        },
        {
            "type": "box",
            "layout": "baseline",
            "spacing": "sm",
            "contents": [
                {
                    "type": "text",
                    "text": "หมวดหมู่:",
                    "color": "#64748B",
                    "size": "xs",
                    "flex": 2
                },
                {
                    "type": "text",
                    "text": f"{category} (เร่งด่วน: {priority_score})",
                    "color": "#0F172A",
                    "size": "xs",
                    "weight": "bold",
                    "flex": 5
                }
            ]
        },
        {
            "type": "separator"
        },
        {
            "type": "box",
            "layout": "vertical",
            "spacing": "xs",
            "contents": [
                {
                    "type": "text",
                    "text": "📝 รายละเอียดปัญหา:",
                    "color": "#64748B",
                    "size": "xs",
                    "weight": "bold"
                },
                {
                    "type": "text",
                    "text": str(description),
                    "color": "#334155",
                    "size": "sm",
                    "wrap": True
                }
            ]
        },
        {
            "type": "separator"
        },
        {
            "type": "box",
            "layout": "vertical",
            "spacing": "xs",
            "contents": [
                {
                    "type": "text",
                    "text": f"📍 พิกัด: {latitude}, {longitude}" if latitude and longitude else "📍 พิกัด: ไม่ได้ระบุ",
                    "color": "#64748B",
                    "size": "xxs"
                },
                {
                    "type": "text",
                    "text": f"🕐 เวลาแจ้ง: {created_at}",
                    "color": "#94A3B8",
                    "size": "xxs"
                }
            ]
        }
    ]

    # กล่องแสดงข้อมูลการรับเรื่อง / สถานะ และเหตุผล
    if status == "ยกเลิก":
        cancel_box_items = [
            {
                "type": "text",
                "text": f"❌ หน่วยงานยกเลิกการรับเรื่องนี้แล้ว" + (f" ({accepted_by})" if accepted_by else ""),
                "color": "#DC2626",
                "size": "xs",
                "weight": "bold"
            }
        ]
        if status_reason:
            cancel_box_items.append({
                "type": "text",
                "text": f"📌 สาเหตุ: {status_reason}",
                "color": "#B91C1C",
                "size": "xs",
                "weight": "bold",
                "margin": "xs",
                "wrap": True
            })
        cancel_box_items.append({
            "type": "text",
            "text": f"🕒 เวลา: {accepted_at or '-'}" if accepted_at else "สถานะงาน: ยกเลิกเรื่องร้องเรียน",
            "color": "#991B1B",
            "size": "xxs",
            "margin": "xs"
        })
        body_contents.append({
            "type": "box",
            "layout": "vertical",
            "backgroundColor": "#FEF2F2",
            "cornerRadius": "8px",
            "paddingAll": "10px",
            "margin": "sm",
            "contents": cancel_box_items
        })
    elif status == "รอแก้ไข":
        reason_desc = f"📌 สาเหตุ: {status_reason}" if status_reason else "⏳ อยู่ระหว่างจัดเตรียมอุปกรณ์/งบประมาณ"
        body_contents.append({
            "type": "box",
            "layout": "vertical",
            "backgroundColor": "#FFFBEB",
            "cornerRadius": "8px",
            "paddingAll": "10px",
            "margin": "sm",
            "contents": [
                {
                    "type": "text",
                    "text": f"⏳ สถานะ: รอแก้ไข" + (f" ({accepted_by})" if accepted_by else ""),
                    "color": "#B45309",
                    "size": "xs",
                    "weight": "bold"
                },
                {
                    "type": "text",
                    "text": reason_desc,
                    "color": "#92400E",
                    "size": "xs",
                    "weight": "bold",
                    "margin": "xs",
                    "wrap": True
                }
            ]
        })
    elif status == "กำลังดำเนินการ":
        reason_desc = f"🚗 ความคืบหน้า: {status_reason}" if status_reason else "⚙️ กำลังลงพื้นที่ดำเนินการแก้ไข"
        body_contents.append({
            "type": "box",
            "layout": "vertical",
            "backgroundColor": "#EFF6FF",
            "cornerRadius": "8px",
            "paddingAll": "10px",
            "margin": "sm",
            "contents": [
                {
                    "type": "text",
                    "text": f"⚙️ สถานะ: กำลังดำเนินการ" + (f" ({accepted_by})" if accepted_by else ""),
                    "color": "#1D4ED8",
                    "size": "xs",
                    "weight": "bold"
                },
                {
                    "type": "text",
                    "text": reason_desc,
                    "color": "#1E40AF",
                    "size": "xs",
                    "weight": "bold",
                    "margin": "xs",
                    "wrap": True
                }
            ]
        })
    elif status == "ดำเนินการเสร็จสิ้น":
        done_contents = [
            {
                "type": "text",
                "text": f"🎉 ปัญหาได้รับการแก้ไขเสร็จสิ้นแล้ว" + (f" ({accepted_by})" if accepted_by else ""),
                "color": "#065F46",
                "size": "xs",
                "weight": "bold"
            }
        ]
        if status_reason:
            done_contents.append({
                "type": "text",
                "text": f"📌 ผลการแก้ไข: {status_reason}",
                "color": "#047857",
                "size": "xs",
                "weight": "bold",
                "margin": "xs",
                "wrap": True
            })
        body_contents.append({
            "type": "box",
            "layout": "vertical",
            "backgroundColor": "#ECFDF5",
            "cornerRadius": "8px",
            "paddingAll": "10px",
            "margin": "sm",
            "contents": done_contents
        })
    elif accepted_by:
        body_contents.append({
            "type": "box",
            "layout": "vertical",
            "backgroundColor": "#ECFDF5",
            "cornerRadius": "8px",
            "paddingAll": "10px",
            "margin": "sm",
            "contents": [
                {
                    "type": "text",
                    "text": f"🏢 หน่วยงานรับเรื่องแล้ว ({accepted_by})",
                    "color": "#065F46",
                    "size": "xs",
                    "weight": "bold"
                },
                {
                    "type": "text",
                    "text": f"🕒 เวลา: {accepted_at or '-'}",
                    "color": "#047857",
                    "size": "xxs",
                    "margin": "xs"
                }
            ]
        })
    else:
        body_contents.append({
            "type": "box",
            "layout": "vertical",
            "backgroundColor": "#FFFBEB",
            "cornerRadius": "8px",
            "paddingAll": "8px",
            "margin": "sm",
            "contents": [
                {
                    "type": "text",
                    "text": "⏳ รอหน่วยงานกดยืนยันรับเรื่อง",
                    "color": "#B45309",
                    "size": "xs",
                    "weight": "bold"
                }
            ]
        })

    bubble = {
        "type": "bubble",
        "size": "mega",
        "header": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": header_bg,
            "paddingAll": "16px",
            "contents": [
                {
                    "type": "text",
                    "text": header_title,
                    "color": "#FFFFFF",
                    "weight": "bold",
                    "size": "sm"
                },
                {
                    "type": "text",
                    "text": f"🏢 {department}",
                    "color": "#FFFFFF",
                    "weight": "bold",
                    "size": "xl",
                    "margin": "sm"
                }
            ]
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "paddingAll": "16px",
            "spacing": "md",
            "contents": body_contents
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "paddingAll": "16px",
            "contents": []
        }
    }

    # ถ้ามีพิกัดถูกต้อง ให้เพิ่มปุ่มนำทาง Google Maps
    try:
        lat_val = float(latitude) if latitude is not None else 0
        lng_val = float(longitude) if longitude is not None else 0
    except (ValueError, TypeError):
        lat_val, lng_val = 0, 0

    if lat_val != 0 and lng_val != 0:
        google_maps_url = f"https://www.google.com/maps/search/?api=1&query={lat_val},{lng_val}"
        bubble["footer"]["contents"].append({
            "type": "button",
            "style": "primary",
            "color": "#2563EB",
            "height": "sm",
            "action": {
                "type": "uri",
                "label": "🗺️ นำทาง Google Maps",
                "uri": google_maps_url
            }
        })

    # 2. ปุ่มยืนยันรับเรื่อง: เริ่มแรก = '⏳ รอยืนยันรับเรื่อง' เมื่อกดรับแล้ว = '✅ ยืนยันรับเรื่องแล้ว' (เต็มแถว ไม่โดนตัดคำ)
    if status == "ยกเลิก":
        accept_label = "✅ ยืนยันรับเรื่อง"
        accept_style = "secondary"
        accept_color = None
    elif accepted_by:
        accept_label = "✅ ยืนยันรับเรื่องแล้ว"
        accept_style = "primary"
        accept_color = "#0D9488"
    else:
        accept_label = "⏳ รอยืนยันรับเรื่อง"
        accept_style = "primary"
        accept_color = "#059669"

    btn_accept = {
        "type": "button",
        "style": accept_style,
        "height": "sm",
        "action": {
            "type": "postback",
            "label": accept_label,
            "data": f"action=accept&ticket_id={ticket_id}"
        }
    }
    if accept_color:
        btn_accept["color"] = accept_color

    bubble["footer"]["contents"].append(btn_accept)

    # เส้นคั่นสำหรับปุ่มอัปเดตสถานะ
    bubble["footer"]["contents"].append({
        "type": "separator",
        "margin": "xs"
    })

    # 3. ปุ่มแถวสถานะ: รอแก้ไข + กำลังทำ (2 ปุ่มเคียงข้างกันในแนวนอน)
    btn_wait = {
        "type": "button",
        "style": "primary" if status == "รอแก้ไข" else "secondary",
        "height": "sm",
        "action": {
            "type": "postback",
            "label": "⏳ รอแก้ไข",
            "data": f"action=status&status=รอแก้ไข&ticket_id={ticket_id}"
        }
    }
    if status == "รอแก้ไข":
        btn_wait["color"] = "#D97706"

    btn_doing = {
        "type": "button",
        "style": "primary" if status == "กำลังดำเนินการ" else "secondary",
        "height": "sm",
        "action": {
            "type": "postback",
            "label": "⚙️ กำลังทำ",
            "data": f"action=status&status=กำลังดำเนินการ&ticket_id={ticket_id}"
        }
    }
    if status == "กำลังดำเนินการ":
        btn_doing["color"] = "#2563EB"

    bubble["footer"]["contents"].append({
        "type": "box",
        "layout": "horizontal",
        "spacing": "sm",
        "contents": [btn_wait, btn_doing]
    })

    # 4. ปุ่มดำเนินการเสร็จสิ้น (เต็มแถว)
    btn_done = {
        "type": "button",
        "style": "primary" if status == "ดำเนินการเสร็จสิ้น" else "secondary",
        "height": "sm",
        "action": {
            "type": "postback",
            "label": "🎉 ดำเนินการเสร็จสิ้น",
            "data": f"action=status&status=ดำเนินการเสร็จสิ้น&ticket_id={ticket_id}"
        }
    }
    if status == "ดำเนินการเสร็จสิ้น":
        btn_done["color"] = "#059669"

    bubble["footer"]["contents"].append(btn_done)

    # เส้นคั่นสำหรับปุ่มยกเลิก
    bubble["footer"]["contents"].append({
        "type": "separator",
        "margin": "xs"
    })

    # 5. ปุ่มยกเลิกรับเรื่อง (เต็มแถว สีแดงชัดเจน ไม่โดนตัดคำ)
    btn_cancel = {
        "type": "button",
        "style": "primary",
        "color": "#DC2626",
        "height": "sm",
        "action": {
            "type": "postback",
            "label": "❌ ยกเลิกเรื่องร้องเรียนแล้ว" if status == "ยกเลิก" else "❌ ยกเลิกรับเรื่อง",
            "data": f"action=cancel_accept&ticket_id={ticket_id}"
        }
    }
    bubble["footer"]["contents"].append(btn_cancel)

    # Hero Image ถ้ามีและเป็น https URL ที่สมบูรณ์
    if image_path and str(image_path).startswith("https://"):
        bubble["hero"] = {
            "type": "image",
            "url": str(image_path),
            "size": "full",
            "aspectRatio": "20:13",
            "aspectMode": "cover"
        }

    return bubble


def get_user_profile(user_id: str, access_token: str = None) -> dict:
    """
    ดึงข้อมูลโปรไฟล์ LINE ของผู้ใช้งานหรือเจ้าหน้าที่ (เช่น ชื่อ displayName)
    """
    token = (access_token and access_token.strip()) or LINE_CHANNEL_ACCESS_TOKEN
    url = f"https://api.line.me/v2/bot/profile/{user_id}"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        print("Error fetching profile from LINE:", e)
    return {}


def push_flex_message(to: str, alt_text: str, flex_contents: dict, access_token: str = None):
    """
    ส่งข้อความแบบ Flex Message ไปยัง LINE User หรือ Group
    หากไม่ระบุ access_token จะใช้ LINE_CHANNEL_ACCESS_TOKEN หลัก
    """
    token = (access_token and access_token.strip()) or LINE_CHANNEL_ACCESS_TOKEN
    url = "https://api.line.me/v2/bot/message/push"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "to": to,
        "messages": [
            {
                "type": "flex",
                "altText": alt_text,
                "contents": flex_contents
            }
        ]
    }

    response = requests.post(url, headers=headers, json=payload)
    return response.status_code, response.text


def get_department_config(department: str):
    """
    ดึง Token และ Destination (User ID / Group ID) ของหน่วยงานจาก .env
    หากไม่ได้กำหนด Token เฉพาะ จะใช้ Token หลักของ อบต.
    หากไม่ได้กำหนด ปลายทาง จะใช้ LINE_DEPT_DEFAULT
    """
    # โหลดค่าล่าสุดจาก .env
    load_dotenv(override=True)

    dept_configs = {
        "กองช่าง": {
            "token": os.getenv("LINE_TOKEN_KONG_CHANG"),
            "dest": os.getenv("LINE_DEST_KONG_CHANG") or os.getenv("LINE_DEPT_KONG_CHANG"),
        },
        "กองสาธารณสุข": {
            "token": os.getenv("LINE_TOKEN_PUBLIC_HEALTH"),
            "dest": os.getenv("LINE_DEST_PUBLIC_HEALTH") or os.getenv("LINE_DEPT_PUBLIC_HEALTH"),
        },
        "งานป้องกันและบรรเทาสาธารณภัย": {
            "token": os.getenv("LINE_TOKEN_DISASTER"),
            "dest": os.getenv("LINE_DEST_DISASTER") or os.getenv("LINE_DEPT_DISASTER"),
        },
        "งานไฟฟ้า": {
            "token": os.getenv("LINE_TOKEN_ELECTRIC"),
            "dest": os.getenv("LINE_DEST_ELECTRIC"),
        },
        "สำนักปลัด": {
            "token": os.getenv("LINE_TOKEN_PALAD"),
            "dest": os.getenv("LINE_DEST_PALAD") or os.getenv("LINE_DEPT_PALAD"),
        },
    }

    cfg = dept_configs.get(department, {})
    token = (cfg.get("token") or "").strip()
    dest = (cfg.get("dest") or "").strip() or os.getenv("LINE_DEPT_DEFAULT")

    return token, dest


def notify_department(ticket_data: dict):
    """
    ส่งแจ้งเตือน Flex Card ไปยัง LINE ของหน่วยงานที่รับผิดชอบโดยอัตโนมัติ
    ⚠️ สำคัญ: ต้องส่งผ่านบอทประจำหน่วยงานเท่านั้น ห้ามส่งผ่านบอทหลักประชาชนเด็ดขาด
    เพื่อป้องกันไม่ให้การ์ดที่มีปุ่มรับเรื่อง/สถานะไปโผล่ในห้องแชทของประชาชน
    """
    department = ticket_data.get("department") or ticket_data.get("ai_department") or "สำนักปลัด"
    ticket_id = ticket_data.get("ticket_id", "")
    token, destination_id = get_department_config(department)

    # ป้องกันไม่ให้ส่งผ่านบอทหลักประชาชน (LINE_CHANNEL_ACCESS_TOKEN) เด็ดขาด
    main_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "").strip()
    if not token or token == main_token:
        print(f"⚠️ หน่วยงาน '{department}' ยังไม่มี LINE Token ประจำหน่วยงาน (ระบบระงับการส่งผ่านบอทหลักประชาชน เพื่อป้องกันประชาชนกดเล่น)")
        return False, "Department token not configured"

    if not destination_id:
        print(f"⚠️ ไม่มี LINE Destination สำหรับหน่วยงาน: {department}")
        return False, "No LINE destination configured"

    flex_card = build_department_flex_card(ticket_data)
    alt_text = f"🚨 แจ้งเตือนงานใหม่: {ticket_id} ({department})"

    print(f"📢 กำลังส่งแจ้งเตือน Flex Card หาหน่วยงาน {department} ผ่านบอทเฉพาะของหน่วยงาน (ID: {destination_id})...")
    status_code, response_text = push_flex_message(
        to=destination_id,
        alt_text=alt_text,
        flex_contents=flex_card,
        access_token=token
    )

    if status_code == 200:
        print(f"✅ ส่งแจ้งเตือนหน่วยงาน {department} สำเร็จ ({ticket_id})")
        return True, response_text
    else:
        print(f"❌ ส่งแจ้งเตือนหน่วยงาน {department} ไม่สำเร็จ: {status_code} - {response_text}")
        return False, response_text

# ============================================================
# จบ LINE Department Notification Service
# ============================================================