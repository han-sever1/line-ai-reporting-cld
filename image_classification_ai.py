# ============================================================
# Model B - Image Classification
# ============================================================

import os
import json
import numpy as np
import tensorflow as tf
from PIL import Image


# ============================================================
# ตั้งค่า Model
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "model_B_image_classification_4_classes.keras"
)

CLASS_NAMES_PATH = os.path.join(
    BASE_DIR,
    "models",
    "model_B_class_names.json"
)

IMAGE_SIZE = (224, 224)


# ============================================================
# โหลด Model B
# ============================================================

model = tf.keras.models.load_model(
    MODEL_PATH
)


# ============================================================
# โหลด Class Names
# ============================================================

with open(
    CLASS_NAMES_PATH,
    "r",
    encoding="utf-8"
) as f:

    class_names = json.load(f)


# ============================================================
# จบ Model B - Image Classification
# ============================================================
# ============================================================
# STEP 10.5: Function สำหรับ Predict Model B
# ============================================================

def predict_image_classification(
    image_path: str
):
    """
    วิเคราะห์รูปภาพด้วย Model B
    """

    # ========================================================
    # โหลดรูปภาพ
    # ========================================================

    image = Image.open(
        image_path
    ).convert("RGB")

    # ========================================================
    # Resize เป็นขนาดเดียวกับตอน Train
    # ========================================================

    image = image.resize(
        IMAGE_SIZE
    )

    # ========================================================
    # แปลงรูปเป็น NumPy
    # ========================================================

    image_array = np.array(
        image,
        dtype=np.float32
    )

    # ========================================================
    # เพิ่ม Batch Dimension
    # ========================================================

    image_array = np.expand_dims(
        image_array,
        axis=0
    )

    # ========================================================
    # Predict
    # ========================================================

    predictions = model.predict(
        image_array,
        verbose=0
    )

    # ========================================================
    # หา Class ที่มี Probability สูงที่สุด
    # ========================================================

    predicted_index = int(
        np.argmax(
            predictions[0]
        )
    )

    predicted_class = class_names[
        predicted_index
    ]

    confidence = float(
        predictions[0][
            predicted_index
        ]
    )

    # ========================================================
    # Probability ของทุก Class
    # ========================================================

    probabilities = {}

    for index, class_name in enumerate(
        class_names
    ):

        probabilities[class_name] = float(
            predictions[0][index]
        )

    # ========================================================
    # ส่งผลลัพธ์กลับ
    # ========================================================

    return {
        "class": predicted_class,
        "confidence": confidence,
        "probability": confidence,
        "probabilities": probabilities
    }


# ============================================================
# จบ STEP 10.5
# ============================================================