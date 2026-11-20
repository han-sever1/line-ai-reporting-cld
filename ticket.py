import re
from database import get_db


def generate_ticket_id():
    """
    สร้างเลขอ้างอิง Ticket ID แบบ TK-0001, TK-0002
    จากฐานข้อมูล MySQL (XAMPP)
    """
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            # ดึงรหัส ticket_id ล่าสุดเพื่อเพิ่มเลขต่อ
            cursor.execute("SELECT ticket_id FROM reports ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            if row and row.get("ticket_id"):
                latest_ticket = row["ticket_id"]
                match = re.search(r"TK-(\d+)", latest_ticket)
                if match:
                    next_number = int(match.group(1)) + 1
                    return f"TK-{next_number:04d}"

            # กรณีเพิ่งเริ่ม หรือยังไม่มีรูปแบบ TK-xxxx
            cursor.execute("SELECT COUNT(*) AS total FROM reports")
            count_row = cursor.fetchone()
            count = count_row["total"] if count_row else 0
            next_number = count + 1
            return f"TK-{next_number:04d}"
    finally:
        conn.close()