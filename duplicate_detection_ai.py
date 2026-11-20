# ============================================================
# 🤖 AI Duplicate Detection
# ตรวจสอบภาพซ้ำด้วย Perceptual Hash (pHash)
# ============================================================

from PIL import Image
import imagehash
from pathlib import Path


# ============================================================
# 📁 Image Path Helper
# แปลง path จาก Database ให้เป็น path ของไฟล์จริง
# ============================================================

BASE_DIR = Path(__file__).resolve().parent


def convert_image_path(image_path):
    """
    แปลง /uploads/TK-0001.jpg
    เป็น E:\\line-ai-reporting-cld\\uploads\\TK-0001.jpg
    """

    if not image_path:
        return None

    image_path = str(image_path)

    # ถ้าเป็น path ของ FastAPI เช่น /uploads/xxx.jpg
    if image_path.startswith("/uploads/"):

        filename = image_path.replace(
            "/uploads/",
            "",
            1
        )

        return str(
            BASE_DIR / "uploads" / filename
        )

    # ถ้าเป็น file path อยู่แล้ว
    return image_path


# ============================================================
# จบ Image Path Helper
# ============================================================


# ============================================================
# คำนวณ pHash ของรูปภาพ
# ============================================================

def calculate_image_hash(image_path):

    image = Image.open(image_path)

    image_hash = imagehash.phash(image)

    return str(image_hash)


# ============================================================
# คำนวณความแตกต่างระหว่างภาพ 2 ภาพ
# ============================================================

def calculate_image_difference(
    image_path_1,
    image_path_2
):

    hash_1 = imagehash.phash(
        Image.open(image_path_1)
    )

    hash_2 = imagehash.phash(
        Image.open(image_path_2)
    )

    difference = hash_1 - hash_2

    return difference


# ============================================================
# ตรวจสอบว่าภาพ 2 ภาพซ้ำกันหรือใกล้เคียงกันหรือไม่
# ============================================================

def predict_image_duplicate(
    new_image_path,
    old_image_path,
    threshold=10
):

    difference = calculate_image_difference(
        new_image_path,
        old_image_path
    )

    if difference <= threshold:

        is_duplicate = True

    else:

        is_duplicate = False

    return {
        "is_duplicate": is_duplicate,
        "difference": difference
    }


# ============================================================
# จบ AI Duplicate Detection
# ============================================================

# ============================================================
# 📍 Duplicate Detection - Location Distance
# คำนวณระยะห่างระหว่างตำแหน่ง 2 จุด
# ============================================================

from math import radians, sin, cos, sqrt, atan2


def calculate_location_distance(
    latitude_1,
    longitude_1,
    latitude_2,
    longitude_2
):
    """
    คำนวณระยะทางระหว่างพิกัด GPS 2 จุด
    ผลลัพธ์เป็นเมตร
    """

    # รัศมีโลกโดยประมาณ หน่วยเมตร
    earth_radius = 6371000

    # แปลงองศาเป็นเรเดียน
    lat1 = radians(latitude_1)
    lon1 = radians(longitude_1)

    lat2 = radians(latitude_2)
    lon2 = radians(longitude_2)

    # ความต่างของพิกัด
    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1

    # Haversine Formula
    a = (
        sin(delta_lat / 2) ** 2
        + cos(lat1)
        * cos(lat2)
        * sin(delta_lon / 2) ** 2
    )

    c = 2 * atan2(
        sqrt(a),
        sqrt(1 - a)
    )

    distance = earth_radius * c

    return round(distance, 2)


# ============================================================
# ตรวจสอบว่าตำแหน่งอยู่ใกล้กันหรือไม่
# ============================================================

def is_location_nearby(
    latitude_1,
    longitude_1,
    latitude_2,
    longitude_2,
    threshold_meters=50
):
    """
    ตรวจสอบว่าตำแหน่ง 2 จุดอยู่ภายในระยะที่กำหนดหรือไม่
    ค่าเริ่มต้น = 50 เมตร
    """

    distance = calculate_location_distance(
        latitude_1,
        longitude_1,
        latitude_2,
        longitude_2
    )

    return {
        "is_nearby": distance <= threshold_meters,
        "distance_meters": distance,
        "threshold_meters": threshold_meters
    }


# ============================================================
# จบ Duplicate Detection - Location Distance
# ============================================================

# ============================================================
# 🤖 Duplicate Detection - Combined Analysis
# รวมประเภทปัญหา + ความคล้ายของภาพ + ตำแหน่ง
# ============================================================

def predict_duplicate_report(
    new_image_path,
    old_image_path,
    new_category,
    old_category,
    new_latitude,
    new_longitude,
    old_latitude,
    old_longitude,
    image_threshold=10,
    location_threshold_meters=50
):
    """
    ตรวจสอบว่ารายงานใหม่อาจเป็นปัญหาซ้ำกับรายงานเดิมหรือไม่

    เงื่อนไข:
    1. ประเภทปัญหาต้องเหมือนกัน
    2. ภาพคล้ายกัน หรือ ตำแหน่งอยู่ใกล้กัน
    """

    # ========================================================
    # 1. ตรวจประเภทปัญหา
    # ========================================================

    same_category = (
        new_category.strip().lower()
        == old_category.strip().lower()
    )

    # ========================================================
    # 2. ตรวจความคล้ายของภาพ
    # ========================================================

    image_result = predict_image_duplicate(
        new_image_path,
        old_image_path,
        threshold=image_threshold
    )

    image_is_similar = image_result["is_duplicate"]

    image_difference = image_result["difference"]

    # ========================================================
    # 3. ตรวจตำแหน่ง
    # ========================================================

    location_result = is_location_nearby(
        new_latitude,
        new_longitude,
        old_latitude,
        old_longitude,
        threshold_meters=location_threshold_meters
    )

    location_is_nearby = location_result["is_nearby"]

    distance_meters = location_result["distance_meters"]

    # ========================================================
    # 4. ตัดสินผล Duplicate
    # ========================================================

    if same_category and (
        image_is_similar
        or location_is_nearby
    ):

        is_possible_duplicate = True

    else:

        is_possible_duplicate = False

    # ========================================================
    # 5. กำหนดระดับผลการตรวจสอบ
    # ========================================================

    if not same_category:

        result_status = "ไม่ซ้ำ"

    elif image_is_similar and location_is_nearby:

        result_status = "อาจซ้ำสูง"

    elif image_is_similar or location_is_nearby:

        result_status = "อาจซ้ำ"

    else:

        result_status = "ไม่พบความเสี่ยงซ้ำ"

    # ========================================================
    # 6. ส่งผลลัพธ์
    # ========================================================

    return {
        "is_possible_duplicate": is_possible_duplicate,
        "status": result_status,
        "same_category": same_category,
        "image_is_similar": image_is_similar,
        "image_difference": int(image_difference),
        "location_is_nearby": location_is_nearby,
        "distance_meters": distance_meters
    }

# ============================================================
# จบ Duplicate Detection - Combined Analysis
# ============================================================

# ============================================================
# 🤖 AI Duplicate Detection
# ค้นหา Ticket ที่อาจซ้ำกับรายงานใหม่
# ============================================================

def find_possible_duplicate(
    new_image_path,
    new_category,
    new_latitude,
    new_longitude,
    old_reports,
    image_threshold=10,
    location_threshold_meters=50
):
    """
    ตรวจสอบรายงานใหม่กับ Ticket เดิมหลายรายการ

    เงื่อนไข:
    1. ประเภทปัญหาต้องเหมือนกัน
    2. ภาพคล้ายกัน หรือ ตำแหน่งอยู่ใกล้กัน
    """

    possible_duplicates = []

    for old_report in old_reports:
        # ====================================================
        # 🧪 Debug Duplicate
        # ตรวจสอบ Ticket ที่กำลังนำมาเปรียบเทียบ
        # ====================================================

        print(
            "กำลังตรวจ Ticket:",
            old_report.get("ticket_id")
        )

        # ====================================================
        # จบ Debug Duplicate
        # ====================================================

        old_image_path = old_report.get("image_path")

        # ====================================================
        # 📁 แปลง Database Path → File Path จริง
        # ====================================================

        old_image_path = convert_image_path(
            old_image_path
        )

        # ====================================================
        # จบการแปลง Image Path
        # ====================================================

        old_category = old_report.get("nlp_category")

        old_latitude = old_report.get("latitude")
        old_longitude = old_report.get("longitude")

        # ====================================================
        # ตรวจสอบว่าข้อมูลตำแหน่งครบหรือไม่
        # ====================================================

        if (
            old_image_path is None
            or old_latitude is None
            or old_longitude is None
        ):
            continue

        # ====================================================
        # ตรวจสอบ Duplicate
        # ====================================================

        result = predict_duplicate_report(
            new_image_path=new_image_path,
            old_image_path=old_image_path,
            new_category=new_category,
            old_category=old_category,
            new_latitude=new_latitude,
            new_longitude=new_longitude,
            old_latitude=old_latitude,
            old_longitude=old_longitude,
            image_threshold=image_threshold,
            location_threshold_meters=location_threshold_meters
        )

        # ====================================================
        # ถ้ามีความเสี่ยงซ้ำ
        # ====================================================
        # ====================================================
        # 🧪 Debug Duplicate Result
        # ตรวจสอบผลของแต่ละ Ticket
        # ====================================================

        print(
            "ผลตรวจ:",
            old_report.get("ticket_id"),
            "| Category:",
            result["same_category"],
            "| Image:",
            result["image_is_similar"],
            "| Location:",
            result["location_is_nearby"],
            "| Possible:",
            result["is_possible_duplicate"]
        )

        # ====================================================
        # จบ Debug Duplicate Result
        # ====================================================
        if result["is_possible_duplicate"]:

            # ========================================================
            # 🤖 คำนวณคะแนน Duplicate
            # ========================================================

            score_result = calculate_duplicate_score(
                image_is_similar=result["image_is_similar"],
                location_is_nearby=result["location_is_nearby"]
            )

            # ========================================================
            # บันทึกผล Duplicate
            # ========================================================

            possible_duplicates.append({
                "ticket_id": old_report.get("ticket_id"),
                "status": score_result["status"],
                "score": score_result["score"],
                "image_is_similar": result["image_is_similar"],
                "image_difference": result["image_difference"],
                "location_is_nearby": result["location_is_nearby"],
                "distance_meters": result["distance_meters"]
            })

    # ============================================================
    # คืนค่าผลลัพธ์
    # ============================================================

    return possible_duplicates


# ============================================================
# จบ AI Duplicate Detection
# ============================================================

# ============================================================
# 🤖 AI Duplicate Detection
# คำนวณคะแนนความเสี่ยง Duplicate
# ============================================================

def calculate_duplicate_score(
    image_is_similar,
    location_is_nearby
):
    """
    คำนวณคะแนนความเสี่ยงของรายงานซ้ำ

    ภาพเหมือน      = 70 คะแนน
    ตำแหน่งใกล้    = 30 คะแนน
    """

    score = 0

    # ========================================================
    # คะแนนจากภาพ
    # ========================================================

    if image_is_similar:
        score += 70

    # ========================================================
    # คะแนนจากตำแหน่ง
    # ========================================================

    if location_is_nearby:
        score += 30

    # ========================================================
    # แปลงคะแนนเป็นสถานะ
    # ========================================================

    if score >= 100:

        status = "อาจซ้ำสูง"

    elif score >= 30:

        status = "อาจซ้ำ"

    else:

        status = "ไม่พบความเสี่ยงซ้ำ"

    return {
        "score": score,
        "status": status
    }


# ============================================================
# จบ AI Duplicate Detection
# ============================================================
# ============================================================
# 🤖 AI Duplicate Detection
# เลือก Ticket ที่อาจซ้ำที่สุด
# ถ้าคะแนนเท่ากัน ให้เลือก Ticket ที่อยู่ใกล้ที่สุด
# ============================================================

def select_best_duplicate(possible_duplicates):
    """
    เลือก Ticket ที่มีคะแนน Duplicate สูงที่สุด

    กรณีคะแนนเท่ากัน:
    เลือก Ticket ที่มีระยะทางใกล้ที่สุด
    """

    if not possible_duplicates:
        return None

    best_duplicate = min(
        possible_duplicates,
        key=lambda item: (
            -item.get("score", 0),
            item.get("distance_meters", float("inf"))
        )
    )

    return best_duplicate


# ============================================================
# จบ AI Duplicate Detection
# ============================================================