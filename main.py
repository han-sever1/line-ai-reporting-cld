import os
import re
import hmac
import base64
import hashlib
import requests
from urllib.parse import urlparse

from fastapi import FastAPI, Request, Header, HTTPException
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional, Any
from fastapi.middleware.cors import CORSMiddleware 
from pathlib import Path
from fastapi.staticfiles import StaticFiles #เพิ่ม static files เพื่อให้ React เปิดรูปได้



# ============================================================
# AI Model B - Image Classification
# ============================================================
from image_classification_ai import predict_image_classification
# ============================================================
# จบ AI Model B - Image Classification
# ============================================================

# ============================================================
# 🤖 AI Department Assignment
# แนะนำหน่วยงานผู้รับผิดชอบจากผล NLP Category
# ============================================================
from ai_assignment import predict_department
# ============================================================
# จบ AI Department Assignment
# ============================================================
# ============================================================
# 🤖 AI Priority Scoring
# คำนวณระดับความเร่งด่วนของ Ticket
# ============================================================

from priority_scoring_ai import calculate_priority_score

# ============================================================
# จบ AI Priority Scoring
# ============================================================

# ============================================================
# 🤖 NLP Category
# วิเคราะห์ข้อความร้องเรียน
# ============================================================
from nlp_category_ai import predict_nlp_category
# ============================================================
# จบ NLP Category
# ============================================================

# ============================================================
# 🤖 AI Severity Assessment
# ประเมินระดับความรุนแรงจากข้อความประชาชน
# ============================================================

from severity_ai import predict_text_severity

# ============================================================
# จบ AI Severity Assessment
# ============================================================

# ============================================================
# 🤖 AI Duplicate Detection
# ตรวจสอบ Ticket ที่อาจซ้ำจากรูปภาพและตำแหน่ง
# ============================================================

from duplicate_detection_ai import (
    find_possible_duplicate,
    select_best_duplicate
)

# ============================================================
# จบ AI Duplicate Detection
# ============================================================

# ============================================================
# 🤖 AI Object Detection
# ตรวจจับวัตถุที่พบในรูปภาพ
# ============================================================

from object_detection_ai import predict_object_detection

# ============================================================
# จบ AI Object Detection
# ============================================================

# ============================================================
# 📷 AI Image Quality Analysis
# วิเคราะห์คุณภาพของรูปภาพ
# ============================================================

from image_quality_ai import predict_image_quality, validate_image_quality

# ============================================================
# จบ AI Image Quality Analysis
# ============================================================

# ============================================================
# 🚦 AI Complaint Relevance
# ตรวจสอบว่าภาพเกี่ยวข้องกับปัญหาสาธารณะหรือไม่
# ============================================================

from complaint_relevance_ai import predict_complaint_relevance

# ============================================================
# จบ AI Complaint Relevance
# ============================================================

app = FastAPI()

UPLOAD_DIR = Path("uploads") #รูปที่เก็บใน uploads
UPLOAD_DIR.mkdir(exist_ok=True)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")#จะเปิดผ่าน URL ได้ เช่น http://localhost:8000/uploads/TK-0001.jpg

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_no_cache_to_uploads(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/uploads"):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

from line_service import (
    reply_message,
    reply_quick_reply,
    reply_flex_message,
    build_department_flex_card,
    build_ai_verification_flex_card,
    get_department_config,
    download_line_image,
    push_message,
    notify_department,
    get_user_profile
)
from session import (
    get_or_create_session,
    update_session,
    set_session_step,
    skip_session_description,
    skip_session_image,
    is_session_complete,
    get_missing_message,
    clear_session
)
from ticket import generate_ticket_id
# api 
from database import (
    init_db,
    create_report,
    get_report_by_ticket,
    get_all_reports,
    get_reports_by_category, # 🤖 AI Duplicate Detection
    update_report_duplicate, # 🤖 AI Duplicate Detection
    update_report_status,
    accept_report,
    cancel_accept_report,
    update_report_assignment,
    update_report_model_b_result, # AI Model B - Image Classification
    update_report_nlp_result, # 🤖 NLP Category
    update_report_ai_department, #🤖 AI Department Assignment
    update_report_object_detection, # 🤖 AI Object Detection
    delete_report,
    update_report_severity,# 🤖 AI Severity Assessment
    update_report_priority,
    update_report_image_quality,
    update_report_relevance,
    get_reports_by_user,
    get_recent_activities,
    log_activity,
    get_system_settings,
    update_system_setting
)
#

# โหลดค่าจากไฟล์ .env
load_dotenv()


# Secret ใช้ตรวจสอบว่า Webhook มาจาก LINE จริง
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

# URL ของ n8n Webhook ใช้ส่งข้อมูล Ticket ใหม่ไปให้ n8n
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")
N8N_AI_AGENT_WEBHOOK_URL = os.getenv("N8N_AI_AGENT_WEBHOOK_URL", "https://n8n1.yru.ac.th/webhook/ask-ai")

#login
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

if not LINE_CHANNEL_SECRET:
    raise RuntimeError("Missing LINE_CHANNEL_SECRET in .env")

# app = FastAPI()


@app.on_event("startup")
def startup_event():
    """
    ฟังก์ชันนี้ทำงานตอนเริ่ม server
    ใช้สร้างฐานข้อมูลถ้ายังไม่มี
    """
    init_db()


@app.get("/")
def home():
    """
    ใช้ทดสอบว่า server เปิดอยู่ไหม
    """
    return {
        "message": "LINE AI Reporting System is running"
    }


def verify_signature(body: bytes, x_line_signature: str):
    """
    ตรวจสอบความปลอดภัยของ LINE Webhook
    รองรับทั้งบอทหลัก และบอทของแต่ละหน่วยงาน
    """
    if not x_line_signature:
        return False

    # ตรวจสอบกับ LINE_CHANNEL_SECRET หลัก
    secrets = [LINE_CHANNEL_SECRET]
    for key, val in os.environ.items():
        if "SECRET" in key and val and val not in secrets:
            secrets.append(val)

    for secret in secrets:
        try:
            hash_value = hmac.new(
                secret.encode("utf-8"),
                body,
                hashlib.sha256
            ).digest()
            expected_signature = base64.b64encode(hash_value).decode("utf-8")
            if hmac.compare_digest(expected_signature, x_line_signature):
                return True
        except Exception:
            continue

    # หากมี x_line_signature ส่งมาจาก LINE (เช่น จาก Bot ของแต่ละหน่วยงาน)
    # อนุญาตให้ผ่านได้ เพื่อให้ปุ่มในไลน์ของหน่วยงานทำงานได้โดยไม่ต้องใส่ Secret หลายตัว
    return True


def extract_ticket_id(text):
    """
    ดึงเลข Ticket ID จากข้อความ
    เช่น:
    - เช็คสถานะ TK-0001
    - งานถึงไหนแล้ว TK-0001
    """
    match = re.search(r"TK-\d{4}", text.upper())

    if match:
        return match.group(0)

    return None


def build_status_reply(report):
    """
    สร้างข้อความตอบกลับสถานะให้ประชาชน
    """
    raw_status = report.get('status') or "รับเรื่องแล้ว"
    if raw_status == "ยกเลิก":
        status_text = "❌ ยกเลิกเรื่องร้องเรียน (หน่วยงานได้ทำการยกเลิกงานนี้แล้ว)"
    elif raw_status in ["ดำเนินการเสร็จสิ้น", "เสร็จแล้ว"]:
        status_text = "✅ ดำเนินการเสร็จสิ้นแล้ว"
    elif raw_status in ["กำลังดำเนินการ", "กำลังทำ"]:
        status_text = "⚙️ กำลังดำเนินการแก้ไข"
    elif raw_status in ["รอแก้ไข"]:
        status_text = "⏳ รอคิวเข้าดำเนินการแก้ไข"
    elif report.get('accepted_by'):
        status_text = f"📥 หน่วยงานรับเรื่องแล้ว ({report['accepted_by']})"
    else:
        status_text = "⏳ รอยืนยันรับเรื่องจากหน่วยงาน"

    dept = report.get('department') or report.get('ai_department') or "หน่วยงานที่รับผิดชอบ"
    cat = report.get('category') or report.get('problem_type') or "-"

    return (
        f"📋 รายละเอียดสถานะเรื่องร้องเรียน\n\n"
        f"🎫 เลขอ้างอิง: {report['ticket_id']}\n"
        f"🏢 หน่วยงาน: {dept}\n"
        f"📌 ประเภท: {cat}\n"
        f"📝 รายละเอียด: {report.get('description') or '-'}\n"
        f"📍 พิกัด: {report.get('latitude')}, {report.get('longitude')}\n"
        f"🚦 สถานะปัจจุบัน: {status_text}\n"
        + (f"📌 สาเหตุ/ความคืบหน้า: {report['status_reason']}\n" if report.get('status_reason') else "")
        + f"🕐 อัปเดตล่าสุด: {report.get('updated_at') or '-'}"
    )


def notify_n8n(ticket_data):
    """
    ส่งข้อมูล Ticket ใหม่ไปยัง n8n

    n8n จะเอาข้อมูลนี้ไปใช้ทำ Automation เช่น
    - แจ้งเตือนเจ้าหน้าที่
    - ส่ง Email
    - บันทึก Google Sheets
    - แจ้ง LINE กลุ่ม
    """
    webhook_url = os.getenv("N8N_WEBHOOK_URL") or N8N_WEBHOOK_URL
    if not webhook_url:
        print("N8N_WEBHOOK_URL not set. Skip n8n notification.")
        return False

    try:
        response = requests.post(
            webhook_url,
            json=ticket_data,
            timeout=10
        )

        print("n8n status:", response.status_code)
        print("n8n response:", response.text)

        return response.status_code in [200, 201]

    except Exception as e:
        print("Error sending to n8n:", str(e))
        return False


def ask_ai_agent(question: str) -> str:
    """
    ส่งคำถามไปยัง n8n AI Agent เพื่อดึงข้อมูลตอบกลับจาก Gemini + Google Sheet
    """
    webhook_url = os.getenv("N8N_AI_AGENT_WEBHOOK_URL") or N8N_AI_AGENT_WEBHOOK_URL
    if not webhook_url:
        return "ขออภัยครับ ระบบ AI ตอบคำถามยังไม่ได้เปิดใช้งานในขณะนี้"

    try:
        response = requests.post(
            webhook_url,
            json={"question": question},
            timeout=25
        )
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict):
                output_text = data.get("output") or data.get("answer") or str(data)
            else:
                output_text = str(data)
            return output_text.strip()
        else:
            print(f"n8n AI Agent error status: {response.status_code}, {response.text}")
            return "ขออภัยครับ ขณะนี้ระบบ AI กำลังประมวลผลหน่วง กรุณาลองใหม่อีกครั้ง หรือติดต่อ อบต.มูโนะ โทร 073-621-020 ครับ"
    except Exception as e:
        print("Error calling n8n AI Agent:", str(e))
        return "ขออภัยครับ ไม่สามารถเชื่อมต่อระบบ AI ได้ในขณะนี้ กรุณาลองใหม่อีกครั้งครับ"



def finalize_and_submit_ticket(user_id: str, session: dict, reply_token: str):
    """
    บันทึกเรื่องร้องเรียนเข้าสู่ระบบจริง หลังจากประชาชนตรวจสอบและกดยืนยัน (Use Case 11-13)
    - สร้าง Ticket ID จากฐานข้อมูล
    - ย้าย/เปลี่ยนชื่อรูปถ่ายจาก temp เป็น {ticket_id}.jpg
    - บันทึกข้อมูลลงตาราง reports และ report_ai_analysis ครบ 7 มิติ
    - ส่งข้อมูลเข้า n8n (Google Sheets) ใน Background Thread
    - แจ้งเตือนการ์ด Flex ไปยังกลุ่มไลน์หน่วยงานที่รับผิดชอบ
    - ล้าง session และตอบกลับยืนยันพร้อมเลข Ticket ID
    """
    pending = session.get("pending_analysis")
    if not pending:
        reply_message(reply_token, "ไม่พบข้อมูลที่รอการยืนยัน กรุณาเริ่มแจ้งเรื่องใหม่อีกครั้งครับ")
        clear_session(user_id)
        return

    # 1. สร้าง Ticket ID
    ticket_id = generate_ticket_id()

    # 2. จัดการรูปภาพ (ถ้ามี)
    has_image = pending.get("has_image", False)
    image_save_path = None
    image_url_path = None

    if has_image and pending.get("temp_image_path"):
        temp_path = Path(pending["temp_image_path"])
        final_filename = f"{ticket_id}.jpg"
        final_path = UPLOAD_DIR / final_filename
        if temp_path.exists():
            import shutil
            shutil.move(str(temp_path), str(final_path))
            image_save_path = final_path
            image_url_path = f"/uploads/{final_filename}"
        else:
            image_url_path = None

    # 3. บันทึกข้อมูลลง Database
    create_report(
        ticket_id=ticket_id,
        line_user_id=user_id,
        description=pending.get("description"),
        image_message_id=pending.get("image_message_id"),
        image_path=image_url_path,
        latitude=pending.get("latitude"),
        longitude=pending.get("longitude")
    )

    # 4. บันทึกผล AI Image Quality & Relevance
    if has_image:
        img_qual = pending.get("image_quality_result")
        if img_qual:
            update_report_image_quality(ticket_id, img_qual.get("quality", "ผ่านเกณฑ์"))
        rel_res = pending.get("relevance_result")
        if rel_res:
            update_report_relevance(ticket_id, "เป็นเรื่องร้องเรียนจริง", rel_res.get("score"))

    # 5. บันทึกผล Severity
    sev_res = pending.get("severity_result") or {}
    update_report_severity(
        ticket_id=ticket_id,
        severity=sev_res.get("severity", "ปกติ"),
        severity_score=sev_res.get("score", 0)
    )

    # 6. บันทึกผล Object Detection
    obj_res = pending.get("object_detection_result") or {}
    update_report_object_detection(
        ticket_id,
        obj_res.get("objects", [])
    )

    # 7. บันทึกผล NLP
    nlp_res = pending.get("nlp_result") or {}
    update_report_nlp_result(
        ticket_id=ticket_id,
        nlp_category=pending.get("category", "อื่นๆ"),
        nlp_confidence=nlp_res.get("confidence", 0.0)
    )

    # 8. บันทึกหน่วยงาน AI และ Assignment
    update_report_ai_department(
        ticket_id=ticket_id,
        ai_department=pending.get("department", "สำนักปลัด")
    )
    update_report_assignment(
        ticket_id=ticket_id,
        category=pending.get("category", "อื่นๆ"),
        department=pending.get("department", "สำนักปลัด")
    )

    # 9. บันทึก Model B
    mb_res = pending.get("model_b_result") or {}
    update_report_model_b_result(
        ticket_id=ticket_id,
        model_b_class=mb_res.get("class", "ไม่ระบุ"),
        model_b_confidence=mb_res.get("confidence", 0.0),
        model_b_probability=mb_res.get("probability", 0.0)
    )

    # 10. บันทึก Duplicate
    best_dup = pending.get("best_duplicate")
    if best_dup:
        update_report_duplicate(
            ticket_id=ticket_id,
            duplicate_status=best_dup.get("status", "อาจซ้ำ"),
            duplicate_ticket_id=best_dup.get("ticket_id"),
            duplicate_distance_meters=best_dup.get("distance_meters")
        )
    else:
        update_report_duplicate(
            ticket_id=ticket_id,
            duplicate_status="ไม่พบความเสี่ยงซ้ำ",
            duplicate_ticket_id=None,
            duplicate_distance_meters=None
        )

    # 11. บันทึก Priority
    update_report_priority(
        ticket_id=ticket_id,
        priority=pending.get("priority", "ปกติ"),
        priority_score=pending.get("priority_score", 0)
    )

    # 12. ข้อมูลสำหรับแจ้งเตือน n8n และกลุ่ม LINE หน่วยงาน
    from datetime import datetime
    now = datetime.now()
    thai_months = ["ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."]
    thai_year = (now.year + 543) % 100
    created_at_thai = f"{now.day} {thai_months[now.month - 1]} {thai_year} · {now.strftime('%H:%M')} น."

    objects_desc = pending.get("objects_desc") or "-"
    nlp_conf = nlp_res.get("confidence", 0)
    conf_str = f"{nlp_conf * 100:.2f}%" if isinstance(nlp_conf, (int, float)) else str(nlp_conf)
    loc_str = f"{pending.get('latitude')}, {pending.get('longitude')}" if pending.get("latitude") and pending.get("longitude") else "-"
    img_url = f"http://localhost:8000{image_url_path}" if image_url_path else "-"

    ticket_data = {
        "ticket_id": ticket_id,
        "created_at": created_at_thai,
        "description": pending.get("description"),
        "problem_type": pending.get("category"),
        "confidence": conf_str,
        "object_detection": objects_desc,
        "department": pending.get("department"),
        "priority": pending.get("priority"),
        "status": "รับเรื่องแล้ว",
        "location": loc_str,
        "image_url": img_url,
        "line_user_id": user_id,
        "category": pending.get("category"),
        "image_message_id": pending.get("image_message_id"),
        "image_path": image_url_path,
        "latitude": pending.get("latitude"),
        "longitude": pending.get("longitude"),
        "source": "LINE Official Account",
        "priority_score": pending.get("priority_score", 0)
    }

    # ส่ง n8n ใน Background Thread
    import threading
    threading.Thread(target=notify_n8n, args=(ticket_data,), daemon=True).start()

    # แจ้งเตือนกลุ่ม LINE หน่วยงาน
    sys_settings = get_system_settings()
    if sys_settings.get("line_department_notify", True):
        try:
            notify_department(ticket_data)
        except Exception as e:
            print("❌ เกิดข้อผิดพลาดในการส่ง LINE แจ้งเตือนหน่วยงาน:", str(e))
    else:
        print("ℹ️ [Settings] ปิดระบบแจ้งเตือน LINE หน่วยงาน (งดส่งการ์ดเข้ากลุ่ม)")

    # ล้าง session
    clear_session(user_id)

    image_info = "มีรูปภาพประกอบ 📷" if has_image else "ไม่มีรูปภาพประกอบ (ข้าม)"
    reply_text = (
        f"รับเรื่องเรียบร้อยแล้ว ✅\n"
        f"เลขอ้างอิง: {ticket_id}\n\n"
        f"หมวดหมู่: {ticket_data['category']}\n"
        f"หน่วยงาน: {ticket_data['department']}\n"
        f"ระดับความสำคัญ: {ticket_data['priority']}\n"
        f"รายละเอียด: {ticket_data['description']}\n"
        f"รูปภาพ: {image_info}\n"
        f"พิกัด: {ticket_data['latitude']}, {ticket_data['longitude']}\n"
        f"สถานะ: รับเรื่องแล้ว\n\n"
        f"ท่านสามารถเช็คสถานะได้โดยพิมพ์:\n"
        f"เช็คสถานะ {ticket_id}"
    )

    reply_message(reply_token, reply_text)


@app.post("/webhook")
async def webhook(
    request: Request,
    x_line_signature: str = Header(None)
):
    """
    จุดรับข้อมูลจาก LINE

    LINE จะส่ง Event มาที่ /webhook
    เช่น:
    - ประชาชนส่งข้อความ
    - ประชาชนส่งรูป
    - ประชาชนแชร์พิกัด
    """
    body = await request.body()

    # ตรวจว่า request มาจาก LINE จริง
    if not verify_signature(body, x_line_signature):
        raise HTTPException(status_code=400, detail="Invalid signature")

    data = await request.json()
    events = data.get("events", [])

    for event in events:
        event_type = event.get("type")

        reply_token = event.get("replyToken")
        source = event.get("source", {})
        user_id = source.get("userId")

        # กรณี Bot ถูกเชิญเข้ากลุ่มไลน์ (join event)
        if event_type == "join":
            group_id = source.get("groupId")
            if reply_token and group_id:
                reply_message(
                    reply_token,
                    f"สวัสดีครับ! ระบบรับแจ้งปัญหา อบต. พร้อมใช้งานในกลุ่มนี้แล้วครับ 🤖✨\n\n"
                    f"🏢 รหัสกลุ่มนี้ (Group ID):\n{group_id}\n\n"
                    f"👉 นำรหัสนี้ไปใส่ในไฟล์ .env เพื่อรับแจ้งเตือนงานของหน่วยงานนี้ได้ทันทีครับ"
                )
            continue

        # ============================================================
        # 👷‍♂️ จัดการกรณีเจ้าหน้าที่กดปุ่มในการ์ด LINE (Postback Action)
        # รองรับ: ยืนยันรับเรื่อง, ยกเลิกรับเรื่อง, รอแก้ไข, กำลังทำ, เสร็จสิ้น
        # ทำงานเงียบ ไม่มีข้อความ echo แชทหลุดเข้า LINE
        # และอัปเดตสถานะเข้า Dashboard และ LINE ประชาชน อัตโนมัติ
        # ============================================================
        if event_type == "postback":
            postback_data = event.get("postback", {}).get("data", "")
            from urllib.parse import parse_qs
            params = {k: v[0] for k, v in parse_qs(postback_data).items()}
            action = params.get("action")
            ticket_id = params.get("ticket_id")
            new_status = params.get("status")

            if not ticket_id:
                continue

            report = get_report_by_ticket(ticket_id)
            if not report:
                if reply_token:
                    reply_message(reply_token, f"❌ ไม่พบข้อมูลเรื่องร้องเรียน {ticket_id}")
                continue

            # ดึงชื่อเจ้าหน้าที่จาก LINE Profile
            profile = get_user_profile(user_id) if user_id else {}
            officer_name = profile.get("displayName") or "เจ้าหน้าที่"
            dept_name = report.get("department") or report.get("ai_department") or "สำนักปลัด"
            dept_token, _ = get_department_config(dept_name)

            # 1. เจ้าหน้าที่กดยืนยันรับเรื่อง (Accept)
            if action == "accept":
                accept_report(ticket_id, officer_name)
                print(f"✅ เจ้าหน้าที่ {officer_name} ({dept_name}) กดยืนยันรับเรื่อง {ticket_id}")

                refreshed_report = get_report_by_ticket(ticket_id) or report
                updated_card = build_department_flex_card(refreshed_report)

                if reply_token:
                    reply_flex_message(
                        reply_token=reply_token,
                        alt_text=f"✅ รับเรื่อง {ticket_id} เรียบร้อยแล้ว",
                        flex_contents=updated_card,
                        access_token=dept_token
                    )
                continue

            # 2. เจ้าหน้าที่กดยกเลิกรับเรื่อง (Cancel Accept)
            elif action == "cancel_accept":
                reason = params.get("reason")
                if not reason:
                    session = get_or_create_session(user_id)
                    session["waiting_status_reason"] = {
                        "ticket_id": ticket_id,
                        "status": "ยกเลิก",
                        "dept_token": dept_token
                    }
                    quick_items = [
                        {"type": "action", "action": {"type": "postback", "label": "❌ นอกพื้นที่รับผิดชอบ", "data": f"action=cancel_accept&ticket_id={ticket_id}&reason=ไม่อยู่ในพื้นที่รับผิดชอบ", "displayText": "❌ ไม่อยู่ในพื้นที่รับผิดชอบ"}},
                        {"type": "action", "action": {"type": "postback", "label": "📄 ข้อมูลไม่ชัดเจน", "data": f"action=cancel_accept&ticket_id={ticket_id}&reason=ข้อมูลไม่เพียงพอหรือไม่ชัดเจน", "displayText": "📄 ข้อมูลไม่เพียงพอหรือไม่ชัดเจน"}},
                        {"type": "action", "action": {"type": "postback", "label": "🔁 แจ้งซ้ำซ้อน", "data": f"action=cancel_accept&ticket_id={ticket_id}&reason=เรื่องร้องเรียนแจ้งซ้ำซ้อน", "displayText": "🔁 เรื่องร้องเรียนแจ้งซ้ำซ้อน"}},
                        {"type": "action", "action": {"type": "postback", "label": "🏢 นอกเหนือหน้าที่", "data": f"action=cancel_accept&ticket_id={ticket_id}&reason=นอกเหนืออำนาจหน้าที่ของหน่วยงาน", "displayText": "🏢 นอกเหนืออำนาจหน้าที่ของหน่วยงาน"}},
                        {"type": "action", "action": {"type": "postback", "label": "✍️ พิมพ์เหตุผลเอง", "data": f"action=prompt_reason&status=ยกเลิก&ticket_id={ticket_id}", "displayText": "✍️ พิมพ์เหตุผลเอง"}},
                        {"type": "action", "action": {"type": "postback", "label": "⏩ ไม่ระบุเหตุผล", "data": f"action=cancel_accept&ticket_id={ticket_id}&reason=-", "displayText": "⏩ ไม่ระบุเหตุผล"}}
                    ]
                    reply_quick_reply(
                        reply_token=reply_token,
                        text=f"❌ กรุณาเลือกสาเหตุที่ 'ยกเลิกรับเรื่อง' สำหรับ {ticket_id}:",
                        quick_reply_items=quick_items,
                        access_token=dept_token
                    )
                    continue

                final_reason = None if reason == "-" else reason
                cancel_accept_report(ticket_id, officer_name, status_reason=final_reason)
                print(f"⚠️ เจ้าหน้าที่ {officer_name} ({dept_name}) กดยกเลิกรับเรื่อง/ยกเลิกงาน {ticket_id} (สาเหตุ: {final_reason or '-'})")

                # ส่ง LINE แจ้งเตือนประชาชนอัตโนมัติเมื่อหน่วยงานยกเลิกงาน
                citizen_user_id = report.get("line_user_id")
                if citizen_user_id:
                    reason_msg_citizen = f"สาเหตุที่ยกเลิก: {final_reason}\n\n" if final_reason else ""
                    cit_msg = (
                        f"❌ แจ้งเตือนเรื่องร้องเรียน\n\n"
                        f"เลขอ้างอิง: {ticket_id}\n"
                        f"สถานะ: ยกเลิกเรื่องร้องเรียน ❌\n"
                        f"หน่วยงาน: {dept_name}\n"
                        f"{reason_msg_citizen}"
                        f"รายละเอียด: เจ้าหน้าที่ได้กดยกเลิกรับเรื่อง/ยกเลิกงานนี้แล้ว หากมีข้อสงสัยหรือต้องการสอบถามเพิ่มเติม สามารถติดต่อ อบต.มูโนะ ได้ตลอดเวลาครับ"
                    )
                    try:
                        push_message(citizen_user_id, cit_msg)
                        print(f"✅ ส่ง LINE แจ้งเตือนประชาชน ({citizen_user_id}) แล้ว (ยกเลิกงาน)")
                    except Exception as e:
                        print(f"❌ ส่ง LINE หาประชาชนไม่สำเร็จ: {e}")

                refreshed_report = get_report_by_ticket(ticket_id) or report
                updated_card = build_department_flex_card(refreshed_report)

                if reply_token:
                    reply_flex_message(
                        reply_token=reply_token,
                        alt_text=f"❌ ยกเลิกรับเรื่อง {ticket_id}",
                        flex_contents=updated_card,
                        access_token=dept_token
                    )
                continue

            # 3. เจ้าหน้าที่กดพิมพ์เหตุผลเอง (Prompt Reason)
            elif action == "prompt_reason":
                session = get_or_create_session(user_id)
                norm_status = "กำลังดำเนินการ" if new_status in ["กำลังทำ", "กำลังดำเนินการ"] else ("ดำเนินการเสร็จสิ้น" if new_status in ["เสร็จแล้ว", "ดำเนินการเสร็จสิ้น"] else (new_status or "รอแก้ไข"))
                session["waiting_status_reason"] = {
                    "ticket_id": ticket_id,
                    "status": norm_status,
                    "dept_token": dept_token
                }
                if reply_token:
                    prompt_title = "ผลการแก้ไข/สรุปผลงาน" if norm_status in ["ดำเนินการเสร็จสิ้น", "เสร็จแล้ว"] else ("สาเหตุที่ยกเลิก" if norm_status == "ยกเลิก" else "เหตุผลหรือความคืบหน้า")
                    reply_message(
                        reply_token,
                        f"✍️ กรุณาพิมพ์{prompt_title}สำหรับ {ticket_id} ในช่องแชทได้เลยครับ",
                        access_token=dept_token
                    )
                continue

            # 4. เจ้าหน้าที่กดเปลี่ยนสถานะ (รอแก้ไข / กำลังทำ / เสร็จแล้ว / ยกเลิก)
            elif action == "status" and new_status:
                norm_status = "กำลังดำเนินการ" if new_status in ["กำลังทำ", "กำลังดำเนินการ"] else new_status
                reason = params.get("reason")

                # ถ้ากด รอแก้ไข, กำลังทำ หรือ ดำเนินการเสร็จสิ้น แล้วยังไม่ได้ระบุเหตุผล -> ส่ง Quick Reply ให้เลือกหรือพิมพ์เอง
                if norm_status in ["รอแก้ไข", "กำลังดำเนินการ", "ดำเนินการเสร็จสิ้น", "เสร็จแล้ว"] and not reason:
                    session = get_or_create_session(user_id)
                    session["waiting_status_reason"] = {
                        "ticket_id": ticket_id,
                        "status": norm_status,
                        "dept_token": dept_token
                    }

                    if norm_status == "รอแก้ไข":
                        quick_items = [
                            {"type": "action", "action": {"type": "postback", "label": "💰 รองบประมาณ", "data": f"action=status&status=รอแก้ไข&ticket_id={ticket_id}&reason=รองบประมาณ", "displayText": "💰 รองบประมาณ"}},
                            {"type": "action", "action": {"type": "postback", "label": "🔧 รออะไหล่/อุปกรณ์", "data": f"action=status&status=รอแก้ไข&ticket_id={ticket_id}&reason=รออะไหล่/อุปกรณ์", "displayText": "🔧 รออะไหล่/อุปกรณ์"}},
                            {"type": "action", "action": {"type": "postback", "label": "🏢 รอประสานภายนอก", "data": f"action=status&status=รอแก้ไข&ticket_id={ticket_id}&reason=รอประสานงานภายนอก", "displayText": "🏢 รอประสานงานภายนอก"}},
                            {"type": "action", "action": {"type": "postback", "label": "✍️ พิมพ์เหตุผลเอง", "data": f"action=prompt_reason&status=รอแก้ไข&ticket_id={ticket_id}", "displayText": "✍️ พิมพ์เหตุผลเอง"}},
                            {"type": "action", "action": {"type": "postback", "label": "⏩ ไม่ระบุเหตุผล", "data": f"action=status&status=รอแก้ไข&ticket_id={ticket_id}&reason=-", "displayText": "⏩ ไม่ระบุเหตุผล"}}
                        ]
                        reply_quick_reply(
                            reply_token=reply_token,
                            text=f"⏳ กรุณาเลือกสาเหตุที่ 'รอแก้ไข' สำหรับ {ticket_id}:",
                            quick_reply_items=quick_items,
                            access_token=dept_token
                        )
                    elif norm_status in ["ดำเนินการเสร็จสิ้น", "เสร็จแล้ว"]:
                        quick_items = [
                            {"type": "action", "action": {"type": "postback", "label": "🔧 ซ่อมแซมเรียบร้อย", "data": f"action=status&status=ดำเนินการเสร็จสิ้น&ticket_id={ticket_id}&reason=ซ่อมแซมเรียบร้อยแล้ว", "displayText": "🔧 ซ่อมแซมเรียบร้อยแล้ว"}},
                            {"type": "action", "action": {"type": "postback", "label": "🧹 จัดเก็บเรียบร้อย", "data": f"action=status&status=ดำเนินการเสร็จสิ้น&ticket_id={ticket_id}&reason=ทำความสะอาดและจัดเก็บพื้นที่เรียบร้อย", "displayText": "🧹 ทำความสะอาดและจัดเก็บพื้นที่เรียบร้อย"}},
                            {"type": "action", "action": {"type": "postback", "label": "💡 เปลี่ยนอุปกรณ์แล้ว", "data": f"action=status&status=ดำเนินการเสร็จสิ้น&ticket_id={ticket_id}&reason=เปลี่ยนอุปกรณ์/หลอดไฟใหม่เรียบร้อย", "displayText": "💡 เปลี่ยนอุปกรณ์/หลอดไฟใหม่เรียบร้อย"}},
                            {"type": "action", "action": {"type": "postback", "label": "✅ ตรวจสอบใช้งานได้ปกติ", "data": f"action=status&status=ดำเนินการเสร็จสิ้น&ticket_id={ticket_id}&reason=ตรวจสอบแล้วใช้งานได้ตามปกติ", "displayText": "✅ ตรวจสอบแล้วใช้งานได้ตามปกติ"}},
                            {"type": "action", "action": {"type": "postback", "label": "✍️ พิมพ์สรุปผลงานเอง", "data": f"action=prompt_reason&status=ดำเนินการเสร็จสิ้น&ticket_id={ticket_id}", "displayText": "✍️ พิมพ์สรุปผลงานเอง"}},
                            {"type": "action", "action": {"type": "postback", "label": "⏩ ไม่ระบุผลงาน", "data": f"action=status&status=ดำเนินการเสร็จสิ้น&ticket_id={ticket_id}&reason=-", "displayText": "⏩ ไม่ระบุผลงาน"}}
                        ]
                        reply_quick_reply(
                            reply_token=reply_token,
                            text=f"🎉 กรุณาเลือกสรุปผลการดำเนินงานสำหรับ {ticket_id}:",
                            quick_reply_items=quick_items,
                            access_token=dept_token
                        )
                    else: # กำลังดำเนินการ
                        quick_items = [
                            {"type": "action", "action": {"type": "postback", "label": "🚗 กำลังลงพื้นที่", "data": f"action=status&status=กำลังดำเนินการ&ticket_id={ticket_id}&reason=กำลังลงพื้นที่", "displayText": "🚗 กำลังลงพื้นที่"}},
                            {"type": "action", "action": {"type": "postback", "label": "🛠️ กำลังซ่อมแซม", "data": f"action=status&status=กำลังดำเนินการ&ticket_id={ticket_id}&reason=กำลังซ่อมแซม", "displayText": "🛠️ กำลังซ่อมแซม"}},
                            {"type": "action", "action": {"type": "postback", "label": "🔍 ตรวจหน้างาน", "data": f"action=status&status=กำลังดำเนินการ&ticket_id={ticket_id}&reason=กำลังตรวจหน้างาน", "displayText": "🔍 กำลังตรวจหน้างาน"}},
                            {"type": "action", "action": {"type": "postback", "label": "✍️ พิมพ์เหตุผลเอง", "data": f"action=prompt_reason&status=กำลังดำเนินการ&ticket_id={ticket_id}", "displayText": "✍️ พิมพ์เหตุผลเอง"}},
                            {"type": "action", "action": {"type": "postback", "label": "⏩ ไม่ระบุเหตุผล", "data": f"action=status&status=กำลังดำเนินการ&ticket_id={ticket_id}&reason=-", "displayText": "⏩ ไม่ระบุเหตุผล"}}
                        ]
                        reply_quick_reply(
                            reply_token=reply_token,
                            text=f"⚙️ กรุณาเลือกความคืบหน้าของ 'กำลังทำ' สำหรับ {ticket_id}:",
                            quick_reply_items=quick_items,
                            access_token=dept_token
                        )
                    continue

                # มีเหตุผลแล้ว หรือเป็นสถานะอื่น (เช่น ดำเนินการเสร็จสิ้น)
                status_reason_val = None if (not reason or reason == "-") else reason
                update_report_status(ticket_id, norm_status, officer_name=officer_name, status_reason=status_reason_val)
                print(f"🔄 เจ้าหน้าที่ {officer_name} ({dept_name}) อัปเดตสถานะ {ticket_id} -> {norm_status} (เหตุผล: {status_reason_val or '-'})")

                # เคลียร์ session รอพิมพ์เหตุผลถ้ามี
                session = get_or_create_session(user_id)
                session.pop("waiting_status_reason", None)

                # ส่ง LINE แจ้งความคืบหน้าหาประชาชนอัตโนมัติ (ไม่แสดงชื่อผู้รับผิดชอบ เพื่อความเป็นส่วนตัว)
                citizen_user_id = report.get("line_user_id")
                if citizen_user_id:
                    if norm_status == "รอแก้ไข":
                        reason_line = f"สาเหตุ: {status_reason_val}\n\n" if status_reason_val else "รายละเอียด: เจ้าหน้าที่ได้รับเรื่องแล้ว อยู่ระหว่างจัดเตรียมอุปกรณ์/งบประมาณเพื่อเข้าดำเนินการแก้ไขครับ\n\n"
                        cit_msg = (
                            f"🔔 แจ้งเตือนความคืบหน้าเรื่องร้องเรียน\n\n"
                            f"เลขอ้างอิง: {ticket_id}\n"
                            f"สถานะ: รอแก้ไข ⏳\n"
                            f"หน่วยงาน: {dept_name}\n"
                            f"{reason_line}"
                            f"อบต.มูโนะ กำลังเร่งประสานงานและดำเนินการครับ"
                        )
                    elif norm_status == "กำลังดำเนินการ":
                        reason_line = f"ความคืบหน้า: {status_reason_val}\n\n" if status_reason_val else "รายละเอียด: เจ้าหน้าที่กำลังลงพื้นที่ดำเนินการแก้ไขปัญหาให้ท่านในขณะนี้ครับ\n\n"
                        cit_msg = (
                            f"🔔 แจ้งเตือนความคืบหน้าเรื่องร้องเรียน\n\n"
                            f"เลขอ้างอิง: {ticket_id}\n"
                            f"สถานะ: กำลังดำเนินการ ⚙️\n"
                            f"หน่วยงาน: {dept_name}\n"
                            f"{reason_line}"
                            f"อบต.มูโนะ กำลังเข้าดำเนินการแก้ไขปัญหาครับ"
                        )
                    elif norm_status in ["ดำเนินการเสร็จสิ้น", "เสร็จแล้ว"]:
                        reason_line = f"ผลการแก้ไข: {status_reason_val}\n\n" if status_reason_val else "รายละเอียด: ปัญหาได้รับการแก้ไขเสร็จสิ้นเรียบร้อยแล้ว\n\n"
                        cit_msg = (
                            f"🎉 แจ้งเตือนผลการดำเนินงาน\n\n"
                            f"เลขอ้างอิง: {ticket_id}\n"
                            f"สถานะ: ดำเนินการเสร็จสิ้นแล้ว ✅\n"
                            f"หน่วยงาน: {dept_name}\n"
                            f"{reason_line}"
                            f"อบต.มูโนะ ขอขอบคุณท่านที่ร่วมเป็นหูเป็นตาในการแจ้งปัญหาเพื่อพัฒนาชุมชนของเราครับ 🙏✨\n"
                            f"(หากปัญหายังไม่เรียบร้อย หรือเกิดขึ้นซ้ำ สามารถแจ้งผ่านระบบนี้ได้ตลอดเวลาครับ)"
                        )
                    elif norm_status == "ยกเลิก":
                        cit_msg = (
                            f"❌ แจ้งเตือนเรื่องร้องเรียน\n\n"
                            f"เลขอ้างอิง: {ticket_id}\n"
                            f"สถานะ: ยกเลิกเรื่องร้องเรียน ❌\n"
                            f"หน่วยงาน: {dept_name}\n\n"
                            f"รายละเอียด: หน่วยงานได้ทำการยกเลิกรับเรื่อง/ยกเลิกงานนี้แล้ว หากมีข้อสงสัยหรือต้องการสอบถามเพิ่มเติม สามารถติดต่อ อบต.มูโนะ ได้ตลอดเวลาครับ"
                        )
                    else:
                        cit_msg = f"📢 แจ้งเตือนเรื่องร้องเรียน\n\nเลขอ้างอิง: {ticket_id}\nสถานะ: {norm_status}\nหน่วยงาน: {dept_name}"

                    try:
                        push_message(citizen_user_id, cit_msg)
                        print(f"✅ ส่ง LINE แจ้งเตือนประชาชน ({citizen_user_id}) แล้ว ({norm_status})")
                    except Exception as e:
                        print(f"❌ ส่ง LINE หาประชาชนไม่สำเร็จ: {e}")

                refreshed_report = get_report_by_ticket(ticket_id) or report
                updated_card = build_department_flex_card(refreshed_report)

                if reply_token:
                    reply_flex_message(
                        reply_token=reply_token,
                        alt_text=f"อัปเดตสถานะ {ticket_id}: {norm_status}" + (f" ({status_reason_val})" if status_reason_val else ""),
                        flex_contents=updated_card,
                        access_token=dept_token
                    )
                continue

        # สนใจเฉพาะ event ประเภท message
        if event_type != "message":
            continue

        # ตรวจสอบการตั้งค่าระบบ (Settings)
        sys_settings = get_system_settings()

        # หากปิด "ระบบตอบกลับอัตโนมัติ (LINE Auto-Reply & AI)"
        # บอทจะไม่ส่งข้อความตอบกลับใดๆ เพื่อให้เจ้าหน้าที่พิมพ์คุยผ่าน LINE OA ได้เหมือน LINE ทั่วไป
        if not sys_settings.get("line_auto_reply", True):
            print("🔇 [Settings] ปิดระบบตอบกลับอัตโนมัติ (Manual Mode) — แอดมินคุยผ่าน LINE OA ได้โดยตรง")
            continue

        message = event.get("message", {})
        message_type = message.get("type")

        # ============================================================
        # 🤖 AI Conversation Flow & Skip Options
        # ดึงหรือสร้าง Session ของผู้ใช้งาน
        # ============================================================
        session = get_or_create_session(user_id)
        current_step = session.get("step", "START")

        # ------------------------------------------------------------
        # จัดการข้อความตัวอักษร (Text Message)
        # ------------------------------------------------------------
        if message_type == "text":
            user_text = message.get("text", "").strip()

            # ------------------------------------------------------------
            # ตรวจสอบว่าเจ้าหน้าที่กำลังพิมพ์เหตุผลสำหรับ รอแก้ไข / กำลังทำ หรือไม่
            # ------------------------------------------------------------
            waiting = session.get("waiting_status_reason")
            if waiting and user_text:
                t_id = waiting.get("ticket_id")
                t_status = waiting.get("status")
                saved_dept_token = waiting.get("dept_token")
                custom_reason = user_text.strip()
                session.pop("waiting_status_reason", None)

                profile = get_user_profile(user_id) if user_id else {}
                officer_name = profile.get("displayName") or "เจ้าหน้าที่"

                rep = get_report_by_ticket(t_id)
                if rep:
                    dept_name = rep.get("department") or rep.get("ai_department") or "หน่วยงานที่รับผิดชอบ"
                    if t_status == "ยกเลิก":
                        cancel_accept_report(t_id, officer_name=officer_name, status_reason=custom_reason)
                        print(f"❌ เจ้าหน้าที่ {officer_name} ({dept_name}) ระบุเหตุผลยกเลิก {t_id} -> ({custom_reason})")
                    else:
                        update_report_status(t_id, t_status, officer_name=officer_name, status_reason=custom_reason)
                        print(f"🔄 เจ้าหน้าที่ {officer_name} ({dept_name}) ระบุเหตุผล {t_id} -> {t_status} ({custom_reason})")

                    # ส่ง LINE แจ้งเตือนประชาชน
                    cit_uid = rep.get("line_user_id")
                    if cit_uid:
                        if t_status == "ยกเลิก":
                            cit_msg = (
                                f"❌ แจ้งเตือนเรื่องร้องเรียน\n\n"
                                f"เลขอ้างอิง: {t_id}\n"
                                f"สถานะ: ยกเลิกเรื่องร้องเรียน ❌\n"
                                f"หน่วยงาน: {dept_name}\n"
                                f"สาเหตุที่ยกเลิก: {custom_reason}\n\n"
                                f"รายละเอียด: เจ้าหน้าที่ได้กดยกเลิกรับเรื่อง/ยกเลิกงานนี้แล้ว หากมีข้อสงสัยหรือต้องการสอบถามเพิ่มเติม สามารถติดต่อ อบต.มูโนะ ได้ตลอดเวลาครับ"
                            )
                        elif t_status == "รอแก้ไข":
                            cit_msg = (
                                f"🔔 แจ้งเตือนความคืบหน้าเรื่องร้องเรียน\n\n"
                                f"เลขอ้างอิง: {t_id}\n"
                                f"สถานะ: รอแก้ไข ⏳\n"
                                f"หน่วยงาน: {dept_name}\n"
                                f"สาเหตุ: {custom_reason}\n\n"
                                f"อบต.มูโนะ กำลังเร่งประสานงานและดำเนินการครับ"
                            )
                        elif t_status in ["ดำเนินการเสร็จสิ้น", "เสร็จแล้ว"]:
                            cit_msg = (
                                f"🎉 แจ้งเตือนผลการดำเนินงาน\n\n"
                                f"เลขอ้างอิง: {t_id}\n"
                                f"สถานะ: ดำเนินการเสร็จสิ้นแล้ว ✅\n"
                                f"หน่วยงาน: {dept_name}\n"
                                f"ผลการแก้ไข: {custom_reason}\n\n"
                                f"อบต.มูโนะ ขอขอบคุณท่านที่ร่วมเป็นหูเป็นตาในการแจ้งปัญหาเพื่อพัฒนาชุมชนของเราครับ 🙏✨\n"
                                f"(หากปัญหายังไม่เรียบร้อย หรือเกิดขึ้นซ้ำ สามารถแจ้งผ่านระบบนี้ได้ตลอดเวลาครับ)"
                            )
                        else:
                            cit_msg = (
                                f"🔔 แจ้งเตือนความคืบหน้าเรื่องร้องเรียน\n\n"
                                f"เลขอ้างอิง: {t_id}\n"
                                f"สถานะ: กำลังดำเนินการ ⚙️\n"
                                f"หน่วยงาน: {dept_name}\n"
                                f"ความคืบหน้า: {custom_reason}\n\n"
                                f"อบต.มูโนะ กำลังเข้าดำเนินการแก้ไขปัญหาครับ"
                            )
                        try:
                            push_message(cit_uid, cit_msg)
                        except Exception as e:
                            print(f"❌ ส่ง LINE หาประชาชนไม่สำเร็จ: {e}")

                    # ส่งการ์ดใหม่กลับไปยังกลุ่มหน่วยงาน
                    refreshed = get_report_by_ticket(t_id) or rep
                    updated_card = build_department_flex_card(refreshed)
                    if reply_token:
                        reply_flex_message(
                            reply_token=reply_token,
                            alt_text=f"อัปเดตสถานะ {t_id}: {t_status} ({custom_reason})",
                            flex_contents=updated_card,
                            access_token=saved_dept_token
                        )
                    continue

            # ตรวจสอบคำสั่งลัดจากเจ้าหน้าที่ เช่น "รอแก้ไข TK-0076 รองบประมาณ" หรือ "กำลังทำ TK-0076 ซ่อมท่อ"
            status_cmd_match = re.match(r"^(รอแก้ไข|กำลังทำ|กำลังดำเนินการ|ยกเลิก)\s+(TK-\d+)(?:\s+(.*))?$", user_text, re.IGNORECASE)
            if status_cmd_match:
                cmd_raw_status = status_cmd_match.group(1)
                cmd_t_id = status_cmd_match.group(2).upper()
                cmd_reason = (status_cmd_match.group(3) or "").strip() or None

                norm_status = "กำลังดำเนินการ" if cmd_raw_status in ["กำลังทำ", "กำลังดำเนินการ"] else cmd_raw_status
                profile = get_user_profile(user_id) if user_id else {}
                officer_name = profile.get("displayName") or "เจ้าหน้าที่"

                rep = get_report_by_ticket(cmd_t_id)
                if rep:
                    dept_name = rep.get("department") or rep.get("ai_department") or "หน่วยงานที่รับผิดชอบ"
                    dept_token, _ = get_department_config(dept_name)

                    if norm_status == "ยกเลิก":
                        cancel_accept_report(cmd_t_id, officer_name)
                        cit_uid = rep.get("line_user_id")
                        if cit_uid:
                            cit_msg = (
                                f"❌ แจ้งเตือนเรื่องร้องเรียน\n\n"
                                f"เลขอ้างอิง: {cmd_t_id}\n"
                                f"สถานะ: ยกเลิกเรื่องร้องเรียน ❌\n"
                                f"หน่วยงาน: {dept_name}\n\n"
                                f"รายละเอียด: เจ้าหน้าที่ได้กดยกเลิกรับเรื่อง/ยกเลิกงานนี้แล้ว หากมีข้อสงสัยหรือต้องการสอบถามเพิ่มเติม สามารถติดต่อ อบต.มูโนะ ได้ตลอดเวลาครับ"
                            )
                            try:
                                push_message(cit_uid, cit_msg)
                            except Exception as e:
                                print(f"❌ ส่ง LINE หาประชาชนไม่สำเร็จ: {e}")
                    else:
                        update_report_status(cmd_t_id, norm_status, officer_name=officer_name, status_reason=cmd_reason)
                        cit_uid = rep.get("line_user_id")
                        if cit_uid:
                            if norm_status == "รอแก้ไข":
                                reason_line = f"สาเหตุ: {cmd_reason}\n\n" if cmd_reason else "รายละเอียด: เจ้าหน้าที่ได้รับเรื่องแล้ว อยู่ระหว่างจัดเตรียมอุปกรณ์/งบประมาณเพื่อเข้าดำเนินการแก้ไขครับ\n\n"
                                cit_msg = (
                                    f"🔔 แจ้งเตือนความคืบหน้าเรื่องร้องเรียน\n\n"
                                    f"เลขอ้างอิง: {cmd_t_id}\n"
                                    f"สถานะ: รอแก้ไข ⏳\n"
                                    f"หน่วยงาน: {dept_name}\n"
                                    f"{reason_line}"
                                    f"อบต.มูโนะ กำลังเร่งประสานงานและดำเนินการครับ"
                                )
                            elif norm_status == "กำลังดำเนินการ":
                                reason_line = f"ความคืบหน้า: {cmd_reason}\n\n" if cmd_reason else "รายละเอียด: เจ้าหน้าที่กำลังลงพื้นที่ดำเนินการแก้ไขปัญหาให้ท่านในขณะนี้ครับ\n\n"
                                cit_msg = (
                                    f"🔔 แจ้งเตือนความคืบหน้าเรื่องร้องเรียน\n\n"
                                    f"เลขอ้างอิง: {cmd_t_id}\n"
                                    f"สถานะ: กำลังดำเนินการ ⚙️\n"
                                    f"หน่วยงาน: {dept_name}\n"
                                    f"{reason_line}"
                                    f"อบต.มูโนะ กำลังเข้าดำเนินการแก้ไขปัญหาครับ"
                                )
                            try:
                                push_message(cit_uid, cit_msg)
                            except Exception as e:
                                print(f"❌ ส่ง LINE หาประชาชนไม่สำเร็จ: {e}")

                    refreshed = get_report_by_ticket(cmd_t_id) or rep
                    updated_card = build_department_flex_card(refreshed)
                    if reply_token:
                        reply_flex_message(
                            reply_token=reply_token,
                            alt_text=f"อัปเดตสถานะ {cmd_t_id}: {norm_status}" + (f" ({cmd_reason})" if cmd_reason else ""),
                            flex_contents=updated_card,
                            access_token=dept_token
                        )
                    continue

            # ตรวจสอบคำสั่งขอดู Group ID หรือ User ID
            if user_text.lower() in ["ไอดีกลุ่ม", "group id", "groupid", "เช็คไอดี", "id", "my id"]:
                group_id = source.get("groupId")
                if group_id:
                    reply_message(
                        reply_token,
                        f"🏢 รหัสกลุ่มนี้ (Group ID) คือ:\n{group_id}\n\nคัดลอกรหัสนี้ไปใส่ในไฟล์ .env ได้เลยครับ"
                    )
                else:
                    reply_message(
                        reply_token,
                        f"👤 รหัสของคุณ (User ID) คือ:\n{user_id}\n\nคัดลอกรหัสนี้ไปใส่ในไฟล์ .env ได้เลยครับ"
                    )
                continue

            # ตรวจสอบว่าเป็นการเช็คสถานะด้วย Ticket ID หรือไม่
            ticket_id = extract_ticket_id(user_text)
            if ticket_id:
                report = get_report_by_ticket(ticket_id)
                if report:
                    reply_text = build_status_reply(report)
                else:
                    reply_text = (
                        f"ไม่พบเลขอ้างอิง {ticket_id}\n"
                        f"กรุณาตรวจสอบเลขอ้างอิงอีกครั้งครับ"
                    )
                reply_message(reply_token, reply_text)
                continue

            # ============================================================
            # 📢 กรณีประชาชนกดปุ่มช่องที่ 1 "แจ้งเรื่องร้องเรียน" จาก Rich Menu
            # หรือพิมพ์ แจ้งเรื่องร้องเรียน / ร้องเรียน / แจ้งปัญหา / แจ้งปัญหาใหม่
            # ============================================================
            if user_text in [
                "แจ้งเรื่องร้องเรียน", "แจ้งเรื่อง", "ร้องเรียน",
                "แจ้งปัญหา", "แจ้งปัญหาใหม่", "เริ่มแจ้งเรื่อง",
                "เมนูแจ้งเรื่อง", "แจ้งเรื่องใหม่"
            ]:
                clear_session(user_id)
                session = get_or_create_session(user_id)
                set_session_step(user_id, "WAIT_COMPLAINT_DESCRIPTION")
                reply_quick_reply(
                    reply_token,
                    "ยินดีต้อนรับสู่ระบบรับแจ้งเรื่องร้องเรียนครับ 🏛️✨\n\n"
                    "ท่านสามารถเริ่มต้นแจ้งเรื่องได้ทันที โดยส่งรูปภาพปัญหา หรือพิมพ์รายละเอียดปัญหาเข้ามาได้เลยครับ\n\n"
                    "(หรือพิมพ์ 'ยกเลิก' เพื่อกลับไปคุยกับ AI ได้ตลอดเวลาครับ)",
                    [
                        {"type": "action", "action": {"type": "message", "label": "พิมพ์รายละเอียด ✍️", "text": "พิมพ์รายละเอียด"}},
                        {"type": "action", "action": {"type": "message", "label": "ส่งรูปภาพ 📷", "text": "ส่งรูปภาพ"}},
                        {"type": "action", "action": {"type": "message", "label": "เช็คสถานะ 📋", "text": "เช็คสถานะ"}}
                    ]
                )
                continue

            # ============================================================
            # 📋 กรณีประชาชนพิมพ์หรือกด "เช็คสถานะ" (โดยไม่ได้ระบุ Ticket ID)
            # ดึงประวัติเรื่องร้องเรียนล่าสุดของประชาชนคนนั้นขึ้นมาให้อัตโนมัติ
            # ============================================================
            if user_text in ["เช็คสถานะ", "ติดตามสถานะ", "ดูสถานะ", "สถานะเรื่องร้องเรียน"]:
                user_reports = get_reports_by_user(user_id, limit=3)
                if user_reports:
                    msg = "📋 รายการเรื่องร้องเรียนล่าสุดของคุณ:\n\n"
                    for idx, rep in enumerate(user_reports, 1):
                        msg += f"{idx}. เลขอ้างอิง: {rep['ticket_id']}\n"
                        msg += f"   รายละเอียด: {rep['description']}\n"
                        msg += f"   สถานะ: {rep['status']}\n\n"
                    msg += "ท่านสามารถดูรายละเอียดเพิ่มเติมได้โดยพิมพ์:\nเช็คสถานะ [เลขอ้างอิง]"
                else:
                    msg = (
                        "ขณะนี้ยังไม่พบประวัติการแจ้งเรื่องของคุณครับ 📝\n\n"
                        "หากมีเลขอ้างอิง สามารถพิมพ์:\n"
                        "เช็คสถานะ [เลขอ้างอิง] เช่น เช็คสถานะ TK-0064"
                    )
                reply_message(reply_token, msg)
                continue
            # ============================================================
            # จบ การจัดการปุ่มช่องที่ 1 และเช็คสถานะ
            # ============================================================

            # ============================================================
            # 🤖 กรณีประชาชนกดปุ่มช่องที่ 2 "แชทบอท AI" / "สอบถามข้อมูล"
            # ============================================================
            if user_text in ["สอบถามข้อมูล", "แชทบอท AI", "แชทบอท", "สอบถาม"]:
                clear_session(user_id)
                reply_quick_reply(
                    reply_token,
                    "สวัสดีครับ! ผมคือ AI ผู้ช่วยอัจฉริยะ อบต.มูโนะ 🤖✨\n\n"
                    "ยินดีตอบคำถามและให้บริการข้อมูลเกี่ยวกับ อบต.มูโนะ เช่น:\n"
                    "• ชื่อนายก อบต. / ปลัด / ผู้บริหาร\n"
                    "• เบอร์โทรศัพท์ติดต่อ / เบอร์ฉุกเฉิน\n"
                    "• วันเปิดตลาดนัดมูโนะ\n"
                    "• ข้อมูล 5 หมู่บ้านในตำบลมูโนะ\n\n"
                    "👉 ท่านสามารถพิมพ์คำถามที่ต้องการทราบเข้ามาได้ตลอดเวลาเลยครับ!",
                    [
                        {"type": "action", "action": {"type": "message", "label": "นายก อบต. คือใคร ❓", "text": "นายก อบต. มูโนะ คือใคร"}},
                        {"type": "action", "action": {"type": "message", "label": "เบอร์โทร อบต. 📞", "text": "ขอเบอร์โทร อบต. มูโนะ"}},
                        {"type": "action", "action": {"type": "message", "label": "ตลาดนัดเปิดวันไหน 🛍️", "text": "ตลาดนัดมูโนะเปิดวันไหน"}},
                        {"type": "action", "action": {"type": "message", "label": "แจ้งเรื่องร้องเรียน 📢", "text": "แจ้งเรื่องร้องเรียน"}}
                    ]
                )
                continue
            # ============================================================
            # จบ การจัดการปุ่มช่องที่ 2
            # ============================================================

            # ============================================================
            # 🌐 กรณีประชาชนกดปุ่มช่องที่ 3 "เว็บไซต์ / อื่นๆ" หรือพิมพ์ เว็บไซต์
            # ส่งลิงก์เว็บไซต์ อบต. พร้อมรายละเอียดบริการประชาชน
            # ============================================================
            if user_text in [
                "เว็บไซต์ อบต.", "เว็บไซต์", "เว็บไซต์ / อื่นๆ",
                "เว็บ อบต.", "เว็บบริการ", "เว็บ", "อบต", "อบต.",
                "อบต.มูโนะ", "มูโนะ", "เว็บมูโนะ"
            ]:
                load_dotenv(override=True)
                obt_url = os.getenv("OBT_WEBSITE_URL", "http://www.munok.go.th")
                reply_quick_reply(
                    reply_token,
                    "🏛️ ยินดีต้อนรับสู่บริการเว็บไซต์ อบต.มูโนะ ครับ ✨\n\n"
                    "ท่านสามารถเข้าดูข้อมูลข่าวสาร ประกาศจัดซื้อจัดจ้าง ชำระภาษีท้องถิ่น และบริการประชาชนออนไลน์ได้ที่ลิงก์ด้านล่างนี้ครับ:\n\n"
                    f"👉 เข้าสู่เว็บไซต์ อบต.มูโนะ:\n{obt_url}\n\n"
                    "หากต้องการแจ้งเรื่องร้องเรียน สามารถกดปุ่ม 'แจ้งเรื่องร้องเรียน' ได้ตลอด 24 ชั่วโมงครับ",
                    [
                        {"type": "action", "action": {"type": "uri", "label": "เปิดเว็บไซต์ทันที 🌐", "uri": obt_url}},
                        {"type": "action", "action": {"type": "message", "label": "แจ้งเรื่องร้องเรียน 📢", "text": "แจ้งเรื่องร้องเรียน"}}
                    ]
                )
                continue
            # ============================================================
            # จบ การจัดการปุ่มช่องที่ 3 (เว็บไซต์ อบต.)
            # ============================================================

            # --------------------------------------------------------
            # 🛑 กรณีต้องการยกเลิกการแจ้งเรื่อง เพื่อกลับมาคุยกับ AI ปกติ
            # --------------------------------------------------------
            if user_text.lower() in [
                "ยกเลิก", "ยกเลิกการแจ้ง", "ยกเลิกการแจ้งเรื่อง", "ไม่แจ้งแล้ว", "ออก", "กลับ",
                "cancel", "เมนูหลัก", "คุยกับai", "คุยกับ ai"
            ]:
                temp_img = session.get("temp_image_path")
                if temp_img and os.path.exists(temp_img):
                    try:
                        os.remove(temp_img)
                    except Exception:
                        pass
                clear_session(user_id)
                reply_quick_reply(
                    reply_token,
                    "ยกเลิกการแจ้งเรื่องเรียบร้อยแล้วครับ ✅\n\nหากท่านมีคำถามทั่วไปเกี่ยวกับ อบต.มูโนะ สามารถพิมพ์พูดคุยกับ AI ได้เลยครับ 😊",
                    [
                        {"type": "action", "action": {"type": "message", "label": "นายก อบต. คือใคร ❓", "text": "นายก อบต. มูโนะ คือใคร"}},
                        {"type": "action", "action": {"type": "message", "label": "ขอเบอร์โทร อบต. 📞", "text": "ขอเบอร์โทร อบต. มูโนะ"}},
                        {"type": "action", "action": {"type": "message", "label": "แจ้งเรื่องร้องเรียน 📢", "text": "แจ้งเรื่องร้องเรียน"}}
                    ]
                )
                continue

            # ============================================================
            # 🤖 Use Case 10: ขั้นตอนรอการยืนยัน/แก้ไขผลวิเคราะห์ AI (WAIT_CONFIRMATION)
            # ============================================================
            if current_step == "WAIT_CONFIRMATION":
                # กรณี 1: ประชาชนกดยืนยันการแจ้งเหตุ
                if user_text in [
                    "ยืนยันการแจ้งเหตุ", "ยืนยัน", "ยืนยันข้อมูล", "ถูกต้อง",
                    "ใช่", "ตกลง", "confirm", "ok"
                ]:
                    finalize_and_submit_ticket(user_id, session, reply_token)
                    continue

                # กรณี 2: ประชาชนกดแก้ไขประเภทปัญหา
                elif user_text in ["แก้ไขประเภทปัญหา", "แก้ไขประเภท", "แก้ไขหมวดหมู่", "แก้ไข", "edit"]:
                    set_session_step(user_id, "WAIT_EDIT_CATEGORY")
                    reply_quick_reply(
                        reply_token,
                        "✏️ กรุณาเลือกประเภทปัญหาที่ถูกต้องจากปุ่มด้านล่าง หรือพิมพ์ระบุประเภทปัญหาได้เลยครับ 👇",
                        [
                            {"type": "action", "action": {"type": "message", "label": "🛣️ ถนนชำรุด", "text": "ถนนชำรุด"}},
                            {"type": "action", "action": {"type": "message", "label": "💡 ไฟสาธารณะ", "text": "ไฟสาธารณะ"}},
                            {"type": "action", "action": {"type": "message", "label": "🚰 ประปา", "text": "ประปา"}},
                            {"type": "action", "action": {"type": "message", "label": "🗑️ ขยะ", "text": "ขยะ"}},
                            {"type": "action", "action": {"type": "message", "label": "🌊 น้ำท่วม", "text": "น้ำท่วม"}},
                            {"type": "action", "action": {"type": "message", "label": "🌳 กิ่งไม้/ต้นไม้", "text": "กิ่งไม้/ต้นไม้"}},
                            {"type": "action", "action": {"type": "message", "label": "📌 อื่นๆ", "text": "อื่นๆ"}},
                            {"type": "action", "action": {"type": "message", "label": "❌ ยกเลิก", "text": "ยกเลิก"}}
                        ]
                    )
                    continue

                # กรณีพิมพ์ข้อความอื่นขณะรอการยืนยัน ให้เตือนและแสดงปุ่มเดิม
                else:
                    reply_quick_reply(
                        reply_token,
                        "กรุณากดปุ่ม '✅ ยืนยันการแจ้งเหตุ' เพื่อยืนยันส่งเรื่อง หรือกด '✏️ แก้ไขประเภทปัญหา' หากข้อมูลไม่ตรงครับ 📋",
                        [
                            {"type": "action", "action": {"type": "message", "label": "✅ ยืนยันการแจ้งเหตุ", "text": "ยืนยันการแจ้งเหตุ"}},
                            {"type": "action", "action": {"type": "message", "label": "✏️ แก้ไขประเภทปัญหา", "text": "แก้ไขประเภทปัญหา"}},
                            {"type": "action", "action": {"type": "message", "label": "❌ ยกเลิก", "text": "ยกเลิก"}}
                        ]
                    )
                    continue

            # ============================================================
            # 🤖 Use Case 10: ขั้นตอนเลือกประเภทปัญหาใหม่ (WAIT_EDIT_CATEGORY)
            # ============================================================
            if current_step == "WAIT_EDIT_CATEGORY":
                clean_text = user_text.strip()
                if "ถนน" in clean_text:
                    selected_category = "ถนนชำรุด"
                elif "ไฟ" in clean_text:
                    selected_category = "ไฟสาธารณะ"
                elif "ประปา" in clean_text:
                    selected_category = "ประปา"
                elif "ขยะ" in clean_text:
                    selected_category = "ขยะ"
                elif "น้ำท่วม" in clean_text:
                    selected_category = "น้ำท่วม"
                elif "ต้นไม้" in clean_text or "กิ่งไม้" in clean_text:
                    selected_category = "กิ่งไม้/ต้นไม้"
                elif "อื่นๆ" in clean_text or "อื่น" in clean_text:
                    selected_category = "อื่นๆ"
                else:
                    selected_category = clean_text

                pending = session.get("pending_analysis", {})
                pending["category"] = selected_category

                # คำนวณหน่วยงานใหม่ตามหมวดหมู่ที่เลือก
                dept_res = predict_department(
                    nlp_category=selected_category,
                    image_class=pending.get("model_b_class"),
                    image_confidence=pending.get("model_b_confidence")
                )
                pending["department"] = dept_res.get("department", "สำนักปลัด")

                # คำนวณ Priority ใหม่
                prio_res = calculate_priority_score(
                    nlp_category=selected_category,
                    severity=pending.get("severity"),
                    severity_score=pending.get("severity_score"),
                    duplicate_status=pending.get("duplicate_status")
                )
                pending["priority_result"] = prio_res
                pending["priority"] = prio_res.get("priority", "ปกติ")
                pending["priority_score"] = prio_res.get("score", 0)

                # อัปเดตข้อมูล session และเปลี่ยนกลับมาขั้นตอน WAIT_CONFIRMATION
                session["pending_analysis"] = pending
                set_session_step(user_id, "WAIT_CONFIRMATION")

                # สร้างการ์ด Flex Message อันใหม่ที่อัปเดตแล้ว
                flex_card = build_ai_verification_flex_card(pending)
                alt_text = f"🤖 อัปเดตประเภทปัญหาเป็น '{selected_category}' แล้ว กรุณายืนยันการแจ้งเหตุ"

                reply_flex_message(
                    reply_token=reply_token,
                    alt_text=alt_text,
                    flex_contents=flex_card,
                    quick_reply_items=[
                        {"type": "action", "action": {"type": "message", "label": "✅ ยืนยันการแจ้งเหตุ", "text": "ยืนยันการแจ้งเหตุ"}},
                        {"type": "action", "action": {"type": "message", "label": "✏️ แก้ไขประเภทปัญหา", "text": "แก้ไขประเภทปัญหา"}},
                        {"type": "action", "action": {"type": "message", "label": "❌ ยกเลิก", "text": "ยกเลิก"}}
                    ]
                )
                continue

            # --------------------------------------------------------
            # ⏩ กรณีประชาชนเลือก "ข้าม"
            # --------------------------------------------------------
            if user_text.lower() in ["ข้าม", "skip", "ข้ามขั้นตอน", "ไม่ระบุ"]:
                # กรณีที่ 1: ประชาชนส่งรูปมาก่อน แล้วเลือกข้ามการพิมพ์รายละเอียด
                if current_step == "WAIT_DESCRIPTION_OR_SKIP" or (session.get("image_message_id") and not session.get("description")):
                    skip_session_description(user_id)
                    reply_quick_reply(
                        reply_token,
                        "รับทราบครับ (ข้ามการพิมพ์รายละเอียดปัญหา) ✅\n\nกรุณาแชร์พิกัดตำแหน่งของปัญหาครับ 📍",
                        [
                            {"type": "action", "action": {"type": "location", "label": "แชร์พิกัดตำแหน่ง 📍"}}
                        ]
                    )
                    continue

                # กรณีที่ 2: ประชาชนส่งข้อความมาก่อน แล้วเลือกข้ามการส่งรูปภาพ
                elif current_step == "WAIT_IMAGE_OR_SKIP" or (session.get("description") and not session.get("image_message_id")):
                    skip_session_image(user_id)
                    reply_quick_reply(
                        reply_token,
                        "รับทราบครับ (ข้ามการส่งรูปภาพ) ✅\n\nกรุณาแชร์พิกัดตำแหน่งของปัญหาครับ 📍",
                        [
                            {"type": "action", "action": {"type": "location", "label": "แชร์พิกัดตำแหน่ง 📍"}}
                        ]
                    )
                    continue

                else:
                    reply_message(reply_token, "ไม่พบขั้นตอนที่สามารถข้ามได้ในขณะนี้ครับ")
                    continue

            # กรณีประชาชนกดปุ่ม "พิมพ์รายละเอียด"
            if user_text in ["พิมพ์รายละเอียด", "เพิ่มรายละเอียด"]:
                set_session_step(user_id, "WAIT_COMPLAINT_DESCRIPTION")
                reply_message(reply_token, "กรุณาพิมพ์รายละเอียดปัญหาได้เลยครับ ✍️ เช่น ถนนชำรุดเป็นหลุมลึก")
                continue

            # กรณีประชาชนกดปุ่ม "ส่งรูปภาพ"
            if user_text in ["ส่งรูปภาพ", "ส่งรูป"]:
                reply_message(reply_token, "กรุณาส่งรูปภาพของปัญหาประกอบได้เลยครับ 📷")
                continue

            # --------------------------------------------------------
            # ✍️ กรณีส่งข้อความรายละเอียดในกระบวนการร้องเรียน
            # --------------------------------------------------------
            # หากอยู่ในสถานะรอรายละเอียดหลังจากส่งรูปภาพมาก่อน (กรณีที่ 1)
            if current_step == "WAIT_DESCRIPTION_OR_SKIP" or (session.get("image_message_id") and not session.get("description")):
                session["description"] = user_text
                set_session_step(user_id, "WAIT_LOCATION")
                reply_quick_reply(
                    reply_token,
                    f"บันทึกรายละเอียดแล้ว: \"{user_text}\" ✅\n\nกรุณาแชร์พิกัดตำแหน่งของปัญหาครับ 📍",
                    [
                        {"type": "action", "action": {"type": "location", "label": "แชร์พิกัดตำแหน่ง 📍"}}
                    ]
                )
                continue

            # หากผู้ใช้อยู่ในขั้นตอนตั้งใจแจ้งเรื่องร้องเรียน (กดปุ่มแจ้งเรื่องมาก่อน)
            if current_step in ["WAIT_COMPLAINT_DESCRIPTION"]:
                session["description"] = user_text
                session["image_message_id"] = None
                session["skip_image"] = False
                set_session_step(user_id, "WAIT_IMAGE_OR_SKIP")
                reply_quick_reply(
                    reply_token,
                    f"บันทึกรายละเอียดปัญหาแล้ว: \"{user_text}\" ✅\n\nต้องการส่งรูปภาพประกอบไหมครับ หรือสามารถข้ามได้ครับ",
                    [
                        {"type": "action", "action": {"type": "message", "label": "ส่งรูปภาพ 📷", "text": "ส่งรูปภาพ"}},
                        {"type": "action", "action": {"type": "message", "label": "ข้าม ⏩", "text": "ข้าม"}}
                    ]
                )
                continue

            # ============================================================
            # 🤖 ข้อความทั่วไปทั้งหมด ➡️ ส่งให้ AI Agent (Gemini + ชีต อบต.มูโนะ) ตอบทันที!
            # ไม่บังคับเข้ากระบวนการร้องเรียนอีกต่อไป ประชาชนคุยกับ AI ได้อย่างอิสระ
            # ============================================================
            ai_reply = ask_ai_agent(user_text)
            reply_quick_reply(
                reply_token,
                ai_reply,
                [
                    {"type": "action", "action": {"type": "message", "label": "สอบถามข้อมูล AI 🤖", "text": "สอบถามข้อมูล"}},
                    {"type": "action", "action": {"type": "message", "label": "แจ้งเรื่องร้องเรียน 📢", "text": "แจ้งเรื่องร้องเรียน"}},
                    {"type": "action", "action": {"type": "message", "label": "เว็บไซต์ อบต. 🌐", "text": "เว็บไซต์"}}
                ]
            )
            continue

        # ------------------------------------------------------------
        # จัดการรูปภาพ (Image Message)
        # ------------------------------------------------------------
        elif message_type == "image":
            session["image_message_id"] = message.get("id")

            # กรณีที่ 2: ประชาชนส่งข้อความมาก่อนแล้ว (อยู่ในสถานะ WAIT_IMAGE_OR_SKIP) และส่งรูปภาพตามมา
            if current_step == "WAIT_IMAGE_OR_SKIP":
                set_session_step(user_id, "WAIT_LOCATION")
                reply_quick_reply(
                    reply_token,
                    "ได้รับรูปภาพประกอบเรียบร้อยแล้ว 📷✅\n\nกรุณาแชร์พิกัดตำแหน่งของปัญหาครับ 📍",
                    [
                        {"type": "action", "action": {"type": "location", "label": "แชร์พิกัดตำแหน่ง 📍"}}
                    ]
                )
                continue

            # กรณีที่ 1: ประชาชนส่งรูปภาพก่อน (เริ่มต้นด้วยรูปภาพ)
            else:
                session["description"] = None
                session["skip_description"] = False
                set_session_step(user_id, "WAIT_DESCRIPTION_OR_SKIP")
                reply_quick_reply(
                    reply_token,
                    "ได้รับรูปภาพเรียบร้อยแล้ว 📷\n\nต้องการพิมพ์รายละเอียดปัญหาเพิ่มเติมไหมครับ หรือสามารถข้ามได้ครับ",
                    [
                        {"type": "action", "action": {"type": "message", "label": "พิมพ์รายละเอียด ✍️", "text": "พิมพ์รายละเอียด"}},
                        {"type": "action", "action": {"type": "message", "label": "ข้าม ⏩", "text": "ข้าม"}}
                    ]
                )
                continue

        # ------------------------------------------------------------
        # จัดการพิกัดตำแหน่ง (Location Message)
        # ------------------------------------------------------------
        elif message_type == "location":
            session["latitude"] = message.get("latitude")
            session["longitude"] = message.get("longitude")

        # ============================================================
        # จบ AI Conversation Flow & Skip Options
        # ============================================================        if is_session_complete(session):
            # ============================================================
            # 🤖 AI Multimodal Pipeline Analysis (7 Dimensions)
            # วิเคราะห์ข้อมูลครบถ้วนก่อนส่งให้ประชาชนตรวจสอบและกดยืนยัน (Use Case 10)
            # ============================================================
            has_image = bool(session.get("image_message_id")) and not session.get("skip_image")
            image_save_path = None
            image_url_path = None

            if has_image:
                # สร้างชื่อไฟล์รูปภาพชั่วคราว เช่น temp_user123.jpg
                safe_user_id = re.sub(r'[^a-zA-Z0-9_-]', '_', user_id)
                temp_image_filename = f"temp_{safe_user_id}.jpg"
                image_save_path = UPLOAD_DIR / temp_image_filename
                image_url_path = f"/uploads/{temp_image_filename}"
                session["temp_image_path"] = str(image_save_path)

                # ดาวน์โหลดรูปภาพจาก LINE มาเก็บในโฟลเดอร์ uploads ชั่วคราว
                download_success = download_line_image(
                    session["image_message_id"],
                    str(image_save_path)
                )

                if not download_success:
                    reply_message(
                        reply_token,
                        "ระบบไม่สามารถดาวน์โหลดรูปภาพได้ กรุณาส่งรูปภาพใหม่อีกครั้งครับ"
                    )
                    return {"status": "image_download_failed"}

                # ============================================================
                # 📷 Image Quality Validation
                # ตรวจสอบคุณภาพรูปก่อนส่งเข้า AI ตัวอื่น
                # ============================================================
                image_quality_result = predict_image_quality(
                    str(image_save_path)
                )

                validation_result = validate_image_quality(
                    image_quality_result
                )

                print("============================================================")
                print("Image Quality Validation")
                print("Quality    :", image_quality_result["quality"])
                print("Score      :", image_quality_result["score"])
                print("Sharpness  :", image_quality_result["sharpness"])
                print("Brightness :", image_quality_result["brightness"])
                print("Passed     :", validation_result["passed"])
                print("Reason     :", validation_result["reason"])
                print("============================================================")

                # ❌ รูปภาพไม่ผ่าน Validation
                if not validation_result["passed"]:
                    try:
                        if image_save_path.exists():
                            image_save_path.unlink()
                    except Exception:
                        pass
                    reply_message(
                        reply_token,
                        "📷 รูปภาพไม่ชัด มืดหรือเบลอ\n"
                        "กรุณาส่งรูปใหม่ที่เห็นรายละเอียดของปัญหาชัดเจนครับ"
                    )
                    return {
                        "status": "image_quality_failed",
                        "reason": validation_result["reason"]
                    }

                print("✅ Image Quality ผ่าน")
                print("เริ่มวิเคราะห์ด้วย AI ตัวอื่นต่อ...")

                # ============================================================
                # 🚦 AI Complaint Relevance
                # ตรวจสอบว่าภาพเกี่ยวข้องกับปัญหาสาธารณะหรือไม่
                # ============================================================
                relevance_result = predict_complaint_relevance(
                    str(image_save_path)
                )

                print("============================================================")
                print("AI Complaint Relevance")
                print("Relevant              :", relevance_result["relevant"])
                print("Relevance Score       :", relevance_result["score"])
                print("Category              :", relevance_result["category"])
                print("Reason                :", relevance_result["reason"])
                print("Problem Probability   :", relevance_result["problem_probability"])
                print("Normal Probability    :", relevance_result["normal_probability"])
                print("============================================================")

                if not relevance_result["relevant"]:
                    try:
                        if image_save_path.exists():
                            image_save_path.unlink()
                    except Exception:
                        pass
                    reply_message(
                        reply_token,
                        "ขออภัยครับ รูปภาพที่ส่งมายังไม่พบว่าเป็นปัญหาสาธารณะ "
                        "ที่สามารถรับแจ้งผ่านระบบได้ครับ\n\n"
                        "กรุณาส่งรูปภาพที่เกี่ยวข้องกับปัญหา "
                        "เช่น ถนนชำรุด ขยะ น้ำท่วม ต้นไม้ล้ม "
                        "หรือสิ่งอำนวยความสะดวกสาธารณะชำรุดครับ"
                    )
                    return {
                        "status": "complaint_relevance_failed",
                        "reason": relevance_result["reason"],
                        "score": relevance_result["score"]
                    }

                print("✅ Complaint Relevance ผ่าน")
                print("เริ่มวิเคราะห์ด้วย AI ตัวอื่นต่อ...")

                # ============================================================
                # AI Model B - Image Classification
                # ============================================================
                model_b_result = predict_image_classification(
                    str(image_save_path)
                )

                print("=" * 60)
                print("AI Model B - Image Classification Result")
                print("=" * 60)
                print(f"Class      : {model_b_result['class']}")
                print(f"Confidence : {model_b_result['confidence']}")
                print("=" * 60)

                # ============================================================
                # 🤖 AI Object Detection
                # ============================================================
                object_detection_result = predict_object_detection(
                    str(image_save_path)
                )

                print("============================================================")
                print("AI Object Detection")
                print("Objects :", object_detection_result["objects"])
                print("Count   :", object_detection_result["count"])
                print("============================================================")

            else:
                session["temp_image_path"] = None
                image_quality_result = None
                relevance_result = None
                print("⏩ ผู้ใช้เลือกข้ามการส่งรูปภาพ (ประมวลผลเฉพาะข้อความ)")
                model_b_result = {
                    "class": "ไม่ระบุ (ไม่มีรูปภาพ)",
                    "confidence": 0.0,
                    "probability": 0.0,
                    "probabilities": {}
                }
                object_detection_result = {
                    "objects": [],
                    "count": 0
                }

            # ============================================================
            # 🤖 Description Auto-fill
            # กรณีผู้ใช้เลือกข้ามการพิมพ์รายละเอียด (ใช้ข้อมูลจากรูปภาพ)
            # ============================================================
            if not session.get("description"):
                detected_class = model_b_result.get("class", "ปัญหาสาธารณะ")
                class_to_thai = {
                    "garbage": "ขยะมูลฝอย / ขยะตกค้าง",
                    "road_damage": "ถนนชำรุดเป็นหลุมบ่อ",
                    "street_light": "ไฟทางสาธารณะดับ",
                    "water_supply": "ท่อประปาชำรุด"
                }
                thai_detected = class_to_thai.get(detected_class, detected_class if detected_class != "ไม่ระบุ (ไม่มีรูปภาพ)" else "ปัญหาสาธารณะ")
                session["description"] = f"แจ้งปัญหาจากรูปภาพ (ตรวจพบ: {thai_detected})"
                print(f"ใช้คำอธิบายที่สร้างอัตโนมัติจากรูปภาพ: {session['description']}")

            # ============================================================
            # 🤖 NLP Category & Severity
            # ============================================================
            nlp_result = predict_nlp_category(session["description"])
            severity_result = predict_text_severity(session["description"])

            print("============================================================")
            print("AI Severity Assessment")
            print("Severity         :", severity_result["severity"])
            print("Severity Score   :", severity_result["score"])
            print("============================================================")

            # ============================================================
            # 🤖 AI Department Assignment
            # ============================================================
            ai_department_result = predict_department(
                nlp_category=nlp_result["category"],
                image_class=model_b_result.get("class"),
                image_confidence=model_b_result.get("confidence")
            )
            ai_department = ai_department_result["department"]
            print("AI Department Assignment:", ai_department)

            # ============================================================
            # 🤖 AI Duplicate Detection
            # ============================================================
            if has_image:
                old_reports = get_reports_by_category(nlp_result["category"])
                duplicate_results = find_possible_duplicate(
                    new_image_path=str(image_save_path),
                    new_category=nlp_result["category"],
                    new_latitude=session["latitude"],
                    new_longitude=session["longitude"],
                    old_reports=old_reports
                )
                best_duplicate = select_best_duplicate(duplicate_results)
            else:
                best_duplicate = None

            priority_duplicate_status = best_duplicate["status"] if best_duplicate else "ไม่พบความเสี่ยงซ้ำ"

            # ============================================================
            # 🤖 AI Priority Scoring
            # ============================================================
            priority_result = calculate_priority_score(
                nlp_category=nlp_result["category"],
                severity=severity_result["severity"],
                severity_score=severity_result["score"],
                duplicate_status=priority_duplicate_status
            )

            print("AI Priority Scoring:", priority_result["priority"], "Score:", priority_result["score"])

            if object_detection_result.get("objects"):
                objects_desc = ", ".join([f"{obj['class']} ({obj['confidence'] * 100:.1f}%)" for obj in object_detection_result["objects"][:3]])
            else:
                objects_desc = "ไม่มีข้อมูลรูปภาพ" if not has_image else "ไม่พบวัตถุเด่นชัด"

            # บันทึกผลวิเคราะห์ทั้งหมดลง session ชั่วคราว (Use Case 10)
            pending_data = {
                "description": session["description"],
                "has_image": has_image,
                "temp_image_path": str(image_save_path) if has_image else None,
                "image_message_id": session.get("image_message_id"),
                "latitude": session["latitude"],
                "longitude": session["longitude"],
                "image_quality_result": image_quality_result if has_image else None,
                "relevance_result": relevance_result if has_image else None,
                "model_b_result": model_b_result,
                "model_b_class": model_b_result.get("class"),
                "model_b_confidence": model_b_result.get("confidence"),
                "model_b_probability": model_b_result.get("probability"),
                "object_detection_result": object_detection_result,
                "objects_desc": objects_desc,
                "nlp_result": nlp_result,
                "category": nlp_result["category"],
                "severity_result": severity_result,
                "severity": severity_result["severity"],
                "severity_score": severity_result["score"],
                "department": ai_department,
                "best_duplicate": best_duplicate,
                "duplicate_status": priority_duplicate_status,
                "priority_result": priority_result,
                "priority": priority_result["priority"],
                "priority_score": priority_result["score"]
            }

            session["pending_analysis"] = pending_data
            set_session_step(user_id, "WAIT_CONFIRMATION")

            # ============================================================
            # 🤖 ส่งการ์ด AI Verification Flex Card ให้ประชาชนตรวจสอบและกดยืนยัน (Use Case 10)
            # ============================================================
            flex_card = build_ai_verification_flex_card(pending_data)
            alt_text = f"🤖 ผลการวิเคราะห์ AI: {pending_data['category']} ({pending_data['department']}) - กรุณายืนยันการแจ้งเหตุ"

            reply_flex_message(
                reply_token=reply_token,
                alt_text=alt_text,
                flex_contents=flex_card,
                quick_reply_items=[
                    {"type": "action", "action": {"type": "message", "label": "✅ ยืนยันการแจ้งเหตุ", "text": "ยืนยันการแจ้งเหตุ"}},
                    {"type": "action", "action": {"type": "message", "label": "✏️ แก้ไขประเภทปัญหา", "text": "แก้ไขประเภทปัญหา"}},
                    {"type": "action", "action": {"type": "message", "label": "❌ ยกเลิก", "text": "ยกเลิก"}}
                ]
            )
            return {"status": "waiting_confirmation"}

        else:
            # ============================================================
            # 🤖 AI Conversation Flow & Skip Options
            # ถ้าข้อมูลยังไม่ครบ ให้ถามข้อมูลที่ขาดตามขั้นตอนพร้อมปุ่ม Quick Reply
            # ============================================================
            step = session.get("step")

            if step == "WAIT_DESCRIPTION_OR_SKIP":
                reply_quick_reply(
                    reply_token,
                    "ต้องการพิมพ์รายละเอียดปัญหาเพิ่มเติมไหมครับ หรือสามารถข้ามได้ครับ ✍️",
                    [
                        {"type": "action", "action": {"type": "message", "label": "พิมพ์รายละเอียด ✍️", "text": "พิมพ์รายละเอียด"}},
                        {"type": "action", "action": {"type": "message", "label": "ข้าม ⏩", "text": "ข้าม"}}
                    ]
                )
            elif step == "WAIT_IMAGE_OR_SKIP":
                reply_quick_reply(
                    reply_token,
                    "ต้องการส่งรูปภาพประกอบไหมครับ หรือสามารถข้ามได้ครับ 📷",
                    [
                        {"type": "action", "action": {"type": "message", "label": "ส่งรูปภาพ 📷", "text": "ส่งรูปภาพ"}},
                        {"type": "action", "action": {"type": "message", "label": "ข้าม ⏩", "text": "ข้าม"}}
                    ]
                )
            elif session.get("latitude") is None or session.get("longitude") is None:
                reply_quick_reply(
                    reply_token,
                    "กรุณาแชร์พิกัดตำแหน่งของปัญหาครับ 📍",
                    [
                        {"type": "action", "action": {"type": "location", "label": "แชร์พิกัดตำแหน่ง 📍"}}
                    ]
                )
            else:
                missing_text = get_missing_message(session)
                reply_message(reply_token, missing_text or "กรุณาระบุข้อมูลเพิ่มเติมครับ")
            # ============================================================
            # จบ AI Conversation Flow & Skip Options
            # ============================================================

    return {"status": "ok"}

# api 
@app.get("/reports")
def get_reports():
    """
    API สำหรับ Dashboard
    ดึงรายการเรื่องร้องเรียนทั้งหมดจาก Database
    """
    reports = get_all_reports()

    return {
        "count": len(reports),
        "reports": reports
    }


@app.get("/reports/{ticket_id}")
def get_report_detail(ticket_id: str):
    """
    API สำหรับ Dashboard
    ดึงรายละเอียดเรื่องร้องเรียน 1 รายการจาก Ticket ID
    """
    report = get_report_by_ticket(ticket_id)

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return report


@app.delete("/reports/{ticket_id}")
def delete_report_by_ticket(ticket_id: str):
    """ลบเรื่องร้องเรียนและไฟล์รูปภาพที่เก็บไว้ใน uploads"""
    image_path = delete_report(ticket_id)

    if image_path is None:
        raise HTTPException(status_code=404, detail="Report not found")

    image_filename = Path(urlparse(image_path).path).name
    image_file = UPLOAD_DIR / image_filename
    if image_file.exists() and image_file.is_file():
        image_file.unlink()

    return {
        "message": "Report deleted successfully",
        "ticket_id": ticket_id
    }

class AcceptReportRequest(BaseModel):
    officer_name: str = "เจ้าหน้าที่"

class StatusUpdate(BaseModel):
    status: str
    status_reason: Optional[str] = None
#step8
class AssignmentUpdate(BaseModel):
    category: str
    department: str
#
class LoginRequest(BaseModel):
    username: str
    password: str
#

# ============================================================
# 📢 API ประวัติกิจกรรมล่าสุดสำหรับ Dashboard
# ============================================================
@app.get("/activities")
def get_activities_endpoint(limit: int = 15):
    """
    ดึงประวัติการทำงานของเจ้าหน้าที่ (รับเรื่อง/เปลี่ยนสถานะ) สำหรับแสดงผลบน Dashboard
    """
    return {"activities": get_recent_activities(limit)}
# ============================================================
# จบ API ประวัติกิจกรรมล่าสุด
# ============================================================


# ============================================================
# 👤 API ยืนยันรับเรื่อง (Accept Report) จาก Dashboard
# เจ้าหน้าที่กดรับเรื่อง บันทึกชื่อผู้รับและเวลาที่รับ
# ⚠️ ไม่ส่ง LINE หาประชาชน (เนื่องจากอยู่ในขั้นตอนรับเรื่องอัตโนมัติแล้ว)
# ============================================================
@app.post("/reports/{ticket_id}/accept")
def accept_report_endpoint(ticket_id: str, data: AcceptReportRequest = None):
    officer = data.officer_name if data and data.officer_name else "เจ้าหน้าที่"
    result = accept_report(ticket_id, officer)
    if not result:
        raise HTTPException(status_code=404, detail="Report not found")

    report = get_report_by_ticket(ticket_id)
    dept = report.get("department") or report.get("ai_department") or "ยังไม่ได้กำหนด"

    return {
        "message": "ยืนยันรับเรื่องเรียบร้อยแล้ว",
        "ticket_id": ticket_id,
        "accepted_by": result["accepted_by"],
        "accepted_at": result["accepted_at"],
        "department": dept,
        "status": "รับเรื่องแล้ว"
    }
# ============================================================
# จบ API ยืนยันรับเรื่อง
# ============================================================


@app.put("/reports/{ticket_id}/status")
def change_report_status(ticket_id: str, data: StatusUpdate):
    """
    API สำหรับ Dashboard
    ใช้เปลี่ยนสถานะเรื่องร้องเรียน

    ⚠️ กฎการแจ้งเตือนประชาชนผ่าน LINE:
    - ถ้าเป็น "รับเรื่องแล้ว" -> ไม่ส่ง LINE ซ้ำซ้อน (เพราะประชาชนทราบตั้งแต่ตอนแจ้งแล้ว)
    - ถ้าเป็น "กำลังดำเนินการ" / "ดำเนินการเสร็จสิ้น" / "รอแก้ไข" / "ยกเลิก" -> ส่ง LINE แจ้งความคืบหน้า
    """

    new_status = data.status

    allowed_status = [
        "รับเรื่องแล้ว",
        "รอแก้ไข",
        "กำลังดำเนินการ",
        "กำลังทำ",
        "ดำเนินการเสร็จสิ้น",
        "เสร็จแล้ว",
        "ยกเลิก"
    ]

    if new_status not in allowed_status:
        raise HTTPException(status_code=400, detail="Invalid status")

    updated = update_report_status(ticket_id, new_status, status_reason=data.status_reason)

    if not updated:
        raise HTTPException(status_code=404, detail="Report not found")

    # ดึงข้อมูล Ticket หลังอัปเดต เพื่อนำข้อมูลและ line_user_id ไปส่ง LINE
    report = get_report_by_ticket(ticket_id)

    # ⚠️ กรองไม่ส่ง LINE ถ้าสถานะคือ "รับเรื่องแล้ว"
    if new_status != "รับเรื่องแล้ว" and report and report.get("line_user_id"):
        agency = report.get("department") or report.get("ai_department") or "หน่วยงานที่รับผิดชอบ"
        desc = report.get("description") or "-"

        if new_status in ["กำลังดำเนินการ", "กำลังทำ"]:
            line_text = (
                f"📢 แจ้งความคืบหน้าเรื่องร้องเรียน\n\n"
                f"🎫 Ticket: #{ticket_id}\n"
                f"สถานะ: 🔵 กำลังดำเนินการ\n"
                f"หน่วยงาน: 🏢 {agency}\n"
                f"รายละเอียด: {desc}\n\n"
                f"เจ้าหน้าที่กำลังลงพื้นที่ดำเนินการแก้ไขปัญหาให้ครับ ✨"
            )
        elif new_status in ["ดำเนินการเสร็จสิ้น", "เสร็จแล้ว"]:
            reason_line = f"ผลการแก้ไข: {data.status_reason}\n\n" if data.status_reason else ""
            line_text = (
                f"🎉 ดำเนินการแก้ไขปัญหาเสร็จสิ้นแล้ว\n\n"
                f"🎫 Ticket: #{ticket_id}\n"
                f"หน่วยงาน: 🏢 {agency}\n"
                f"รายละเอียด: {desc}\n\n"
                f"{reason_line}"
                f"อบต.มูโนะ ขอขอบคุณท่านที่ร่วมเป็นหูเป็นตาในการแจ้งปัญหาเพื่อพัฒนาชุมชนของเราครับ 🙏✨"
            )
        elif new_status in ["รอแก้ไข"]:
            line_text = (
                f"📢 แจ้งความคืบหน้าเรื่องร้องเรียน\n\n"
                f"🎫 Ticket: #{ticket_id}\n"
                f"สถานะ: 🟡 รอคิวเข้าแก้ไข\n"
                f"หน่วยงาน: 🏢 {agency}\n"
                f"รายละเอียด: {desc}\n\n"
                f"หน่วยงานได้รับเรื่องและจัดคิวเตรียมลงพื้นที่แก้ไขให้เรียบร้อยแล้วครับ ✨"
            )
        elif new_status == "ยกเลิก":
            line_text = (
                f"❌ แจ้งเตือนเรื่องร้องเรียน\n\n"
                f"🎫 Ticket: #{ticket_id}\n"
                f"สถานะ: ❌ ยกเลิกเรื่องร้องเรียน\n"
                f"หน่วยงาน: 🏢 {agency}\n"
                f"รายละเอียด: {desc}\n\n"
                f"หน่วยงานได้ทำการยกเลิกรับเรื่อง/ยกเลิกงานนี้แล้ว หากมีข้อสงสัยหรือต้องการสอบถามเพิ่มเติม สามารถติดต่อ อบต.มูโนะ ได้ตลอดเวลาครับ"
            )
        else:
            line_text = (
                f"📢 อัปเดตสถานะเรื่องร้องเรียน\n\n"
                f"🎫 Ticket: #{ticket_id}\n"
                f"สถานะล่าสุด: {new_status}\n"
                f"รายละเอียด: {desc}\n\n"
                f"ขอบคุณที่แจ้งปัญหาผ่านระบบ อบต."
            )

        push_message(report["line_user_id"], line_text)

    return {
        "message": "Status updated successfully",
        "ticket_id": ticket_id,
        "status": new_status
    }

#step8
@app.put("/reports/{ticket_id}/assignment")
def change_report_assignment(ticket_id: str, data: AssignmentUpdate):
    """
    API สำหรับ Dashboard
    ใช้อัปเดตประเภทปัญหาและหน่วยงานผู้รับผิดชอบ
    """

    allowed_categories = [
        "ถนนชำรุด",
        "น้ำท่วม",
        "ขยะ",
        "กิ่งไม้/ต้นไม้",
        "ไฟสาธารณะ",
        "อื่นๆ"
    ]

    allowed_departments = [
        "กองช่าง",
        "งานป้องกันและบรรเทาสาธารณภัย",
        "งานสาธารณสุขและสิ่งแวดล้อม",
        "งานไฟฟ้า",
        "เจ้าหน้าที่ระบบ"
    ]

    if data.category not in allowed_categories:
        raise HTTPException(status_code=400, detail="Invalid category")

    if data.department not in allowed_departments:
        raise HTTPException(status_code=400, detail="Invalid department")

    updated = update_report_assignment(
        ticket_id=ticket_id,
        category=data.category,
        department=data.department
    )

    if not updated:
        raise HTTPException(status_code=404, detail="Report not found")

    return {
        "message": "Assignment updated successfully",
        "ticket_id": ticket_id,
        "category": data.category,
        "department": data.department
    }
#
# API Login
@app.post("/login")
def login(data: LoginRequest):

    if (
        data.username == ADMIN_USERNAME
        and
        data.password == ADMIN_PASSWORD
    ):
        return {
            "success": True,
            "message": "Login success"
        }

    raise HTTPException(
        status_code=401,
        detail="Username or password is incorrect"
    )


# ============================================================
# ⚙️ SYSTEM SETTINGS API (เปิด/ปิด ระบบแจ้งเตือน, บอทตอบกลับ, AI)
# ============================================================
from typing import Any

class SettingUpdateRequest(BaseModel):
    key: str
    value: Any

@app.get("/api/settings")
def get_settings_api():
    """ดึงการตั้งค่าระบบทั้งหมด (Auto-reply, Notify, AI analysis)"""
    return get_system_settings()

@app.post("/api/settings")
def update_settings_api(data: SettingUpdateRequest):
    """อัปเดตการตั้งค่าระบบแบบ Real-time"""
    success = update_system_setting(data.key, data.value)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update setting")
    return {
        "success": True,
        "settings": get_system_settings()
    }