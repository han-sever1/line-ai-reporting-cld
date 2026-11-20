# ============================================================
# 🤖 AI Department Assignment
# แนะนำหน่วยงานผู้รับผิดชอบแบบ Multimodal (ผสานทั้งข้อความและรูปภาพ)
# ============================================================

def predict_department(nlp_category="อื่นๆ", image_class=None, image_confidence=0.0):
    """
    แนะนำหน่วยงานผู้รับผิดชอบอย่างแม่นยำ โดยผสานข้อมูล 2 มิติ:
    1. วิเคราะห์รูปภาพ (Image Classification Model B) -> กองสาธารณสุข / กองช่าง
    2. วิเคราะห์ข้อความ (NLP Category)
    """

    # ตารางจับคู่จากรูปภาพ (Image Classification Model B)
    image_department_mapping = {
        "garbage": "กองสาธารณสุข",
        "road_damage": "กองช่าง",
        "street_light": "กองช่าง",
        "water_supply": "กองช่าง"
    }

    # ตารางจับคู่จากข้อความ (NLP Category)
    nlp_department_mapping = {
        "ขยะ": "กองสาธารณสุข",
        "ถนนชำรุด": "กองช่าง",
        "น้ำท่วม": "กองช่าง",
        "กิ่งไม้/ต้นไม้": "งานป้องกันและบรรเทาสาธารณภัย",
        "ไฟสาธารณะ": "กองช่าง",
        "ประปา": "กองช่าง",
        "อื่นๆ": "สำนักปลัด"
    }

    # แปลงค่า confidence
    try:
        conf_val = float(image_confidence) if image_confidence is not None else 0.0
    except (ValueError, TypeError):
        conf_val = 0.0

    # กรณีที่ 1: รูปภาพชัดเจนมาก (เช่น ขยะ ความมั่นใจสูง)
    # ให้รูปภาพช่วยชี้ขาดกรณีข้อความเป็น "อื่นๆ" หรือพิมพ์คลุมเครือ
    if image_class in image_department_mapping and conf_val >= 0.50:
        # หากข้อความระบุชัดเจนและตรงกัน หรือข้อความเป็น "อื่นๆ" -> ใช้หน่วยงานจากรูปภาพ
        if nlp_category == "อื่นๆ" or nlp_category is None:
            return {"department": image_department_mapping[image_class]}

    # กรณีที่ 2: ข้อความระบุหมวดหมู่ชัดเจน (ไม่ใช่ "อื่นๆ")
    if nlp_category and nlp_category in nlp_department_mapping and nlp_category != "อื่นๆ":
        return {"department": nlp_department_mapping[nlp_category]}

    # กรณีที่ 3: ถ้าข้อความเป็น "อื่นๆ" แต่มีรูปภาพที่จำแนกได้ (แม้ confidence ปานกลาง)
    if image_class in image_department_mapping and conf_val >= 0.35:
        return {"department": image_department_mapping[image_class]}

    # กรณีที่ 4: ไม่ตรงกับหมวดใดเลย -> สำนักปลัด (รับเรื่องทั่วไป)
    department = nlp_department_mapping.get(nlp_category, "สำนักปลัด")
    return {"department": department}

# ============================================================
# จบ AI Department Assignment
# ============================================================