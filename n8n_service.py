# ส่งข้อมูล Ticket จาก FastAPI ไป n8n
import os
import requests
from dotenv import load_dotenv

# โหลดค่าจากไฟล์ .env
load_dotenv()

# ดึง URL ของ n8n webhook จาก .env
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")


def send_ticket_to_n8n(ticket_data: dict):
    """
    ฟังก์ชันนี้ใช้ส่งข้อมูล Ticket ใหม่ไปยัง n8n

    ticket_data คือข้อมูลเรื่องร้องเรียน เช่น:
    - ticket_id
    - description
    - latitude
    - longitude
    - status
    """

    # ถ้าไม่ได้ใส่ N8N_WEBHOOK_URL ใน .env ให้หยุดทำงาน
    if not N8N_WEBHOOK_URL:
        print("N8N_WEBHOOK_URL is not set in .env")
        return None

    try:
        response = requests.post(
            N8N_WEBHOOK_URL,
            json=ticket_data,
            timeout=10
        )

        print("n8n status:", response.status_code)
        print("n8n response:", response.text)

        return response.status_code, response.text

    except requests.exceptions.RequestException as error:
        print("Error sending ticket to n8n:", error)
        return None