# ============================================================
# 🤖 Session Management & Conversation Flow
# จัดการเก็บข้อมูลชั่วคราวและ State Machine สำหรับ LINE Bot
# รองรับกรณีส่งรูปก่อน หรือส่งข้อความก่อน พร้อมตัวเลือกข้าม (Skip)
# และขั้นตอนให้ประชาชนตรวจสอบ/ยืนยัน/แก้ไขผลวิเคราะห์ AI (Use Case 10)
# ============================================================

# เก็บข้อมูลชั่วคราวของผู้ใช้แต่ละคน
user_sessions = {}


def get_or_create_session(user_id):
    """
    ถ้ายังไม่มี session ของ user นี้ ให้สร้างใหม่
    ถ้ามีแล้ว ให้ดึง session เดิมกลับมา
    """
    if user_id not in user_sessions:
        user_sessions[user_id] = {
            "description": None,
            "image_message_id": None,
            "latitude": None,
            "longitude": None,
            "step": "START",
            "skip_description": False,
            "skip_image": False,
            "temp_image_path": None,
            "pending_analysis": None
        }

    return user_sessions[user_id]


def update_session(user_id, message_type, message):
    """
    อัปเดตข้อมูลใน session ตามชนิดข้อความที่ผู้ใช้ส่งมา
    """
    session = get_or_create_session(user_id)

    if message_type == "text":
        session["description"] = message.get("text")

    elif message_type == "image":
        session["image_message_id"] = message.get("id")

    elif message_type == "location":
        session["latitude"] = message.get("latitude")
        session["longitude"] = message.get("longitude")

    return session


def set_session_step(user_id, step):
    """
    อัปเดตขั้นตอน (Step) ปัจจุบันของบทสนทนา
    เช่น WAIT_DESCRIPTION_OR_SKIP, WAIT_IMAGE_OR_SKIP, WAIT_LOCATION,
    WAIT_CONFIRMATION, WAIT_EDIT_CATEGORY
    """
    session = get_or_create_session(user_id)
    session["step"] = step
    return session


def skip_session_description(user_id):
    """
    บันทึกว่าผู้ใช้เลือกข้ามการพิมพ์รายละเอียด (กรณีส่งรูปก่อน)
    """
    session = get_or_create_session(user_id)
    session["skip_description"] = True
    session["step"] = "WAIT_LOCATION"
    return session


def skip_session_image(user_id):
    """
    บันทึกว่าผู้ใช้เลือกข้ามการส่งรูปภาพ (กรณีส่งข้อความก่อน)
    """
    session = get_or_create_session(user_id)
    session["skip_image"] = True
    session["step"] = "WAIT_LOCATION"
    return session


def is_session_complete(session):
    """
    ตรวจว่าข้อมูลครบถ้วนสำหรับวิเคราะห์ AI หรือยัง
    เงื่อนไข:
    1. ไม่อยู่ในสถานะ WAIT_CONFIRMATION หรือ WAIT_EDIT_CATEGORY (เพื่อไม่ให้วิเคราะห์ซ้ำ)
    2. ต้องมีพิกัด (latitude และ longitude)
    3. ต้องมีรูปภาพ หรือเลือกข้ามรูปภาพ
    4. ต้องมีข้อความรายละเอียด หรือเลือกข้ามรายละเอียด
    5. ต้องมีข้อมูลอย่างใดอย่างหนึ่ง (มีรูป หรือ มีข้อความ)
    """
    # หากอยู่ในขั้นตอนรอการยืนยันหรือรอแก้ไขหมวดหมู่ ไม่ต้องเข้า pipeline AI เริ่มต้นซ้ำ
    if session.get("step") in ["WAIT_CONFIRMATION", "WAIT_EDIT_CATEGORY"]:
        return False

    has_location = (
        session.get("latitude") is not None and
        session.get("longitude") is not None
    )

    has_image_or_skipped = (
        session.get("image_message_id") is not None or
        session.get("skip_image") is True
    )

    has_desc_or_skipped = (
        session.get("description") is not None or
        session.get("skip_description") is True
    )

    has_at_least_one_info = (
        session.get("image_message_id") is not None or
        session.get("description") is not None
    )

    return (
        has_location and
        has_image_or_skipped and
        has_desc_or_skipped and
        has_at_least_one_info
    )


def get_missing_message(session):
    """
    ถ้าข้อมูลยังไม่ครบ ระบบจะบอกประชาชนว่าขาดอะไรตามสถานะปัจจุบัน
    """
    step = session.get("step")

    if step == "WAIT_DESCRIPTION_OR_SKIP":
        return "ต้องการพิมพ์รายละเอียดปัญหาเพิ่มเติมไหมครับ หรือสามารถกด 'ข้าม' ได้ครับ ✍️"

    if step == "WAIT_IMAGE_OR_SKIP":
        return "ต้องการส่งรูปภาพประกอบไหมครับ หรือสามารถกด 'ข้าม' ได้ครับ 📷"

    if session.get("latitude") is None or session.get("longitude") is None:
        return "กรุณาแชร์พิกัดตำแหน่งของปัญหาเพิ่มเติมครับ 📍"

    if session.get("description") is None and not session.get("skip_description"):
        return "กรุณาพิมพ์รายละเอียดของปัญหาก่อนครับ เช่น ถนนหน้าบ้านเป็นหลุม"

    if session.get("image_message_id") is None and not session.get("skip_image"):
        return "กรุณาส่งรูปภาพของปัญหาเพิ่มเติมครับ 📷"

    return None


def clear_session(user_id):
    """
    ลบ session หลังจากสร้าง Ticket สำเร็จ หรือเมื่อผู้ใช้ยกเลิก
    เพื่อให้ผู้ใช้เริ่มแจ้งปัญหาใหม่ได้
    """
    if user_id in user_sessions:
        del user_sessions[user_id]

# ============================================================
# จบ Session Management & Conversation Flow
# ============================================================
