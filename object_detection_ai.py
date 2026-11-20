# ============================================================
# 🤖 AI Object Detection
# ตรวจจับวัตถุที่พบในรูปภาพ
# ============================================================

from ultralytics import YOLO


# ============================================================
# โหลด YOLO Model
# ============================================================

MODEL_PATH = "yolo11n.pt"

model = YOLO(MODEL_PATH)

print("Object Detection Model โหลดสำเร็จ")


# ============================================================
# ฟังก์ชัน Object Detection
# ============================================================

def predict_object_detection(image_path):

    """
    วิเคราะห์รูปภาพและตรวจจับวัตถุที่พบ

    Parameters
    ----------
    image_path : str
        path ของรูปภาพ

    Returns
    -------
    dict
        ผลการตรวจจับวัตถุ
    """

    results = model(
        image_path,
     conf=0.30,    #รับเฉพาะวัตถุที่ AI มั่นใจตั้งแต่ 30% ขึ้นไป
        verbose=False
    )

    detected_objects = []

    # ========================================================
    # อ่านผลลัพธ์จาก YOLO
    # ========================================================

    result = results[0]

    for box in result.boxes:

        class_id = int(box.cls[0])

        confidence = float(box.conf[0])

        class_name = result.names[class_id]

        detected_objects.append({
            "class": class_name,
            "confidence": confidence
        })

    # ========================================================
    # คืนค่าผลลัพธ์
    # ========================================================

    return {
        "objects": detected_objects,
        "count": len(detected_objects)
    }


# ============================================================
# จบ AI Object Detection
# ============================================================