# ============================================================
# 🤖 AI Complaint Relevance Detection
# ตรวจสอบว่ารูปภาพเกี่ยวข้องกับการแจ้งปัญหาสาธารณะหรือไม่
# ใช้ CLIP Zero-Shot Image Classification
# ============================================================

from PIL import Image
from transformers import CLIPProcessor, CLIPModel


# ============================================================
# ⚙️ ตั้งค่า CLIP Model
# ============================================================

MODEL_NAME = "openai/clip-vit-base-patch32"

print("กำลังโหลด CLIP Model...")

model = CLIPModel.from_pretrained(MODEL_NAME)
processor = CLIPProcessor.from_pretrained(MODEL_NAME)

print("โหลด CLIP Model สำเร็จ")


# ============================================================
# 📋 ประเภทปัญหาที่ระบบ อบต. รองรับ
# ============================================================

# ============================================================
# 📋 ประเภทปัญหาที่ระบบ อบต. รองรับ
# เปรียบเทียบ "ภาพปัญหา" กับ "ภาพปกติ"
# ============================================================

COMPLAINT_LABELS = [
    {
        "category": "ถนนชำรุด",
        "problem_prompt": (
            "a damaged public road with potholes, "
            "broken pavement, cracks, or damaged drainage"
        ),
        "normal_prompt": (
            "a normal public road in good condition "
            "without potholes, cracks, or visible damage"
        )
    },
    {
        "category": "ขยะ / สิ่งแวดล้อม",
        "problem_prompt": (
            "a public area with a large amount of garbage, "
            "waste, litter, pollution, or environmental damage"
        ),
        "normal_prompt": (
            "a clean public area without garbage, "
            "waste, litter, or visible pollution"
        )
    },
    {
        "category": "น้ำท่วม / น้ำขัง",
        "problem_prompt": (
            "a public road or area affected by flooding "
            "or significant standing water"
        ),
        "normal_prompt": (
            "a normal dry public road or area "
            "without flooding or standing water"
        )
    },
    {
        "category": "ต้นไม้ล้ม / สิ่งกีดขวาง",
        "problem_prompt": (
            "a fallen tree, collapsed tree, dangerous tree, "
            "or large obstruction blocking a public road"
        ),
        "normal_prompt": (
            "a normal standing tree in good condition "
            "that is not fallen and does not block a public road"
        )
    },
    {
        "category": "สิ่งอำนวยความสะดวกสาธารณะชำรุด",
        "problem_prompt": (
            "a damaged public facility, broken public equipment, "
            "or damaged public property"
        ),
        "normal_prompt": (
            "a normal public facility or public equipment "
            "in good condition without visible damage"
        )
    },
{
    "category": "ปัญหาสาธารณะอื่น ๆ",
    "problem_prompt": (
        "a specific public problem that does not belong to "
        "road damage, garbage or environmental problems, "
        "flooding or standing water, fallen trees or road obstructions, "
        "or damaged public facilities"
    ),
    "normal_prompt": (
        "a normal public area without a specific problem "
        "that needs to be reported"
    )
},
]
# ============================================================
# 🚦 AI Relevance Gate
# ตรวจสอบก่อนว่า "ภาพนี้เป็นปัญหาสาธารณะหรือไม่"
# ============================================================
RELEVANCE_LABELS = [
    {
        "category": "ปัญหาสาธารณะ",
        "prompt": (
            "a photo clearly showing a real public problem, "
            "damaged public infrastructure, environmental problem, "
            "or dangerous condition that should be reported "
            "to a local government organization"
        )
    },
    {
        "category": "ภาพทั่วไป / ไม่ใช่ปัญหา",
        "prompt": (
            "a normal everyday photo with no visible public problem, "
            "no damaged public infrastructure, and nothing that "
            "needs to be reported to a local government organization"
        )
    }
]

# ============================================================
# 🚦 AI Relevance Gate
# ตรวจสอบก่อนว่า "ภาพนี้เป็นปัญหาสาธารณะหรือไม่"
# ============================================================
def check_relevance_gate(image):
    """
    ตรวจสอบภาพเบื้องต้นว่าเป็นปัญหาสาธารณะหรือไม่

    Return:
        relevant      : True / False
        score         : คะแนนความเกี่ยวข้อง
        category      : ปัญหาสาธารณะ / ภาพทั่วไป / ไม่ใช่ปัญหา
    """

    text_inputs = [
        item["prompt"]
        for item in RELEVANCE_LABELS
    ]

    inputs = processor(
        text=text_inputs,
        images=image,
        return_tensors="pt",
        padding=True
    )

    outputs = model(**inputs)

    logits_per_image = outputs.logits_per_image
    probabilities = logits_per_image.softmax(dim=1)[0]

    problem_probability = probabilities[0].item()
    normal_probability = probabilities[1].item()

    # --------------------------------------------------------
    # คำนวณคะแนนความเกี่ยวข้อง
    # --------------------------------------------------------
    total = problem_probability + normal_probability

    if total > 0:
        relevance_score = problem_probability / total
    else:
        relevance_score = 0.0

    # --------------------------------------------------------
    # กำหนด Threshold
    # --------------------------------------------------------
    RELEVANCE_THRESHOLD = 0.70

    if relevance_score >= RELEVANCE_THRESHOLD:
        relevant = True
        category = "ปัญหาสาธารณะ"
    else:
        relevant = False
        category = "ภาพทั่วไป / ไม่ใช่ปัญหา"

    return {
        "relevant": relevant,
        "score": round(relevance_score * 100, 2),
        "category": category,
        "problem_probability": round(problem_probability * 100, 2),
        "normal_probability": round(normal_probability * 100, 2)
    }

# ============================================================
# 🤖 ฟังก์ชันตรวจสอบความเกี่ยวข้องของรูปภาพ
# เปรียบเทียบ "ภาพปัญหา" กับ "ภาพปกติ"
# ============================================================

def predict_complaint_relevance(image_path):
    # --------------------------------------------------------
    # โหลดรูปภาพ
    # --------------------------------------------------------
    image = Image.open(image_path).convert("RGB")

    # ========================================================
    # 🚦 STEP 1: Relevance Gate
    # ตรวจสอบก่อนว่าเป็น "ปัญหาสาธารณะ" หรือไม่
    # ========================================================

    relevance_result = check_relevance_gate(image)


    # --------------------------------------------------------
    # ❌ ถ้าไม่เกี่ยวข้อง
    # ไม่ต้องวิเคราะห์ประเภทปัญหาต่อ
    # --------------------------------------------------------

    if not relevance_result["relevant"]:

        return {
            "relevant": False,
            "result": "ไม่เกี่ยวข้อง",

            "score": relevance_result["score"],

            "category": "ไม่เกี่ยวข้อง",

            "reason": (
                "ภาพไม่พบหลักฐานที่ชัดเจนว่าเป็น "
                "ปัญหาสาธารณะที่ระบบรับแจ้ง"
            ),

            "best_label": (
                "a photo showing a normal everyday photo "
                "with no visible public problem"
            ),

            "best_probability": relevance_result["score"],

            "unrelated_probability": (
                100.0 - relevance_result["score"]
            ),

            "problem_probability": (
                relevance_result["problem_probability"]
            ),

            "normal_probability": (
                relevance_result["normal_probability"]
            )
        }


    # ========================================================
    # 🤖 STEP 2: Category Classification
    # ถ้าผ่าน Relevance Gate
    # จึงค่อยวิเคราะห์ประเภทของปัญหา
    # ========================================================


    # --------------------------------------------------------
    # 📝 สร้าง Prompt สำหรับแต่ละประเภท
    # --------------------------------------------------------

    text_inputs = []

    prompt_info = []

    for item in COMPLAINT_LABELS:

        problem_text = (
            f"a photo showing {item['problem_prompt']}"
        )

        normal_text = (
            f"a photo showing {item['normal_prompt']}"
        )

        text_inputs.append(problem_text)
        text_inputs.append(normal_text)

        prompt_info.append({
            "category": item["category"],
            "problem_prompt": problem_text,
            "normal_prompt": normal_text
        })


    # --------------------------------------------------------
    # 🤖 ส่งรูป + Prompt เข้า CLIP
    # --------------------------------------------------------

    inputs = processor(
        text=text_inputs,
        images=image,
        return_tensors="pt",
        padding=True
    )

    outputs = model(**inputs)


    # --------------------------------------------------------
    # 📊 คำนวณ Probability
    # --------------------------------------------------------

    logits_per_image = outputs.logits_per_image

    probabilities = logits_per_image.softmax(dim=1)[0]


    # ========================================================
    # 📋 วิเคราะห์คะแนนของแต่ละประเภท
    # ========================================================

    category_results = []

    for i, item in enumerate(prompt_info):

        problem_index = i * 2
        normal_index = i * 2 + 1

        problem_probability = (
            probabilities[problem_index].item()
        )

        normal_probability = (
            probabilities[normal_index].item()
        )


        # ----------------------------------------------------
        # 📈 คำนวณว่า "ปัญหา" ชนะ "ปกติ" มากแค่ไหน
        # ----------------------------------------------------

        total = (
            problem_probability +
            normal_probability
        )

        if total > 0:

            problem_score = (
                problem_probability / total
            )

        else:

            problem_score = 0.0


        category_results.append({
            "category": item["category"],
            "problem_prompt": item["problem_prompt"],
            "normal_prompt": item["normal_prompt"],
            "problem_probability": problem_probability,
            "normal_probability": normal_probability,
            "problem_score": problem_score
        })


    # ========================================================
    # 🏆 เลือกประเภทปัญหาที่มีคะแนนสูงสุด
    # ========================================================

    best_result = max(
        category_results,
        key=lambda x: x["problem_probability"]
    )


    best_problem_score = (
        best_result["problem_score"]
    )


    # --------------------------------------------------------
    # ⚙️ Threshold สำหรับ Category
    # --------------------------------------------------------

    PROBLEM_THRESHOLD = 0.60


    # ========================================================
    # ✅ ตัดสินผล Category
    # ========================================================

    if best_problem_score >= PROBLEM_THRESHOLD:

        relevant = True

        result = "เกี่ยวข้อง"

        category = best_result["category"]

        reason = (
            f"ภาพมีลักษณะเป็นปัญหาในประเภท "
            f"'{category}'"
        )

    else:

        # ----------------------------------------------------
        # ⚠️ ผ่าน Relevance Gate แต่ Category ยังไม่ชัดเจน
        # ----------------------------------------------------

        relevant = True

        result = "เกี่ยวข้อง"

        category = "ปัญหาสาธารณะอื่น ๆ"

        reason = (
            "ภาพมีลักษณะเป็นปัญหาสาธารณะ "
            "แต่ยังไม่สามารถระบุประเภทได้อย่างชัดเจน"
        )


    # ========================================================
    # 📦 ส่งผลลัพธ์กลับ
    # ========================================================

    return {

        "relevant": relevant,

        "result": result,

        "score": relevance_result["score"],

        "category": category,

        "reason": reason,

        "best_label": (
            best_result["problem_prompt"]
        ),

        "best_probability": round(
            best_problem_score * 100,
            2
        ),

        "unrelated_probability": round(
            relevance_result["normal_probability"],
            2
        ),

        "problem_probability": round(
            best_result["problem_probability"] * 100,
            2
        ),

        "normal_probability": round(
            best_result["normal_probability"] * 100,
            2
        )
    }
    # ============================================================
# 🧪 ทดสอบ AI Relevance Gate จาก Terminal
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("AI Relevance Gate")
    print("=" * 60)

    image_path = input(
        "\nใส่ path ของรูปภาพที่ต้องการทดสอบ: "
    ).strip()


    try:

        # --------------------------------------------------------
        # โหลดรูปภาพ
        # --------------------------------------------------------
        image = Image.open(image_path).convert("RGB")

        # --------------------------------------------------------
        # 🚦 AI Relevance Gate
        # ทำงานแบบ 2 ขั้น:
        # 1. Relevance Gate
        # 2. Category Classification

        # --------------------------------------------------------
        result = predict_complaint_relevance(
            image_path
        )

        print("\n")
        print("=" * 60)
        print("AI Relevance Gate Result")
        print("=" * 60)

        print(
            f"Relevant                : "
            f"{result['relevant']}"
        )

        print(
            f"Relevance Score         : "
            f"{result['score']}%"
        )

        print(
            f"Category                : "
            f"{result['category']}"
        )

        print(
            f"Problem Probability     : "
            f"{result['problem_probability']}%"
        )

        print(
            f"Normal Probability      : "
            f"{result['normal_probability']}%"
        )

        print("=" * 60)


    except Exception as e:

        print("\nเกิดข้อผิดพลาด:")
        print(e)


# ============================================================
# จบ AI Relevance Gate Test
# ============================================================