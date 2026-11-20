# ============================================================
# 🗄️ DATABASE MODULE — MySQL (XAMPP) & Schema Architecture
# จัดการฐานข้อมูลระบบรับแจ้งปัญหา อบต.สุไหงโกลก ด้วย MySQL (XAMPP)
# รองรับโครงสร้างแยกตาราง reports และ report_ai_analysis ตามหลัก 3NF
# ============================================================

import os
import json
from datetime import datetime
import pymysql
import pymysql.cursors
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "line_reporting")


def get_db():
    """
    เชื่อมต่อฐานข้อมูล MySQL (XAMPP) แบบ DictCursor
    คืนค่าเป็น Dictionary เพื่อความสะดวกและแม่นยำในการใช้งาน
    """
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )


def init_db():
    """
    สร้างฐานข้อมูลและตารางทั้ง 5 ตารางใน MySQL หากยังไม่มี
    ฟังก์ชันนี้จะถูกเรียกตอนเปิดเซิร์ฟเวอร์ FastAPI
    """
    # 1. เชื่อมต่อเซิร์ฟเวอร์เพื่อสร้าง Database ก่อน (ถ้ายังไม่มี)
    server_conn = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        charset="utf8mb4",
        autocommit=True
    )
    with server_conn.cursor() as cur:
        cur.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    server_conn.close()

    # 2. เชื่อมต่อ Database เพื่อสร้างตารางตามลำดับ
    conn = get_db()
    with conn.cursor() as cur:
        # ตารางหน่วยงาน
        cur.execute("""
        CREATE TABLE IF NOT EXISTS departments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL UNIQUE,
            line_channel_token TEXT NULL,
            line_group_id VARCHAR(64) NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)

        # ตารางผู้ใช้งาน Dashboard
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            full_name VARCHAR(100) NOT NULL,
            department VARCHAR(100) NULL,
            role VARCHAR(30) DEFAULT 'officer',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)

        # ตารางเรื่องร้องเรียนหลัก (reports)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INT AUTO_INCREMENT PRIMARY KEY,
            ticket_id VARCHAR(30) NOT NULL UNIQUE,
            line_user_id VARCHAR(64) NULL,
            description TEXT NULL,
            image_message_id VARCHAR(64) NULL,
            image_path VARCHAR(255) NULL,
            latitude DECIMAL(10, 7) NULL,
            longitude DECIMAL(10, 7) NULL,
            status VARCHAR(50) DEFAULT 'รับเรื่องแล้ว',
            status_reason VARCHAR(255) NULL,
            category VARCHAR(100) NULL,
            department VARCHAR(100) NULL,
            accepted_by VARCHAR(100) NULL,
            accepted_at DATETIME NULL,
            created_at DATETIME NULL,
            updated_at DATETIME NULL,
            INDEX idx_ticket (ticket_id),
            INDEX idx_status (status),
            INDEX idx_dept (department)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)

        # ตารางเก็บผลวิเคราะห์ AI Pipeline ทั้ง 7 โมเดล (report_ai_analysis)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS report_ai_analysis (
            id INT AUTO_INCREMENT PRIMARY KEY,
            ticket_id VARCHAR(30) NOT NULL UNIQUE,
            ai1_image_quality VARCHAR(50) NULL,
            ai2_relevance_status VARCHAR(50) NULL,
            ai2_relevance_confidence FLOAT NULL,
            ai3_image_class VARCHAR(50) NULL,
            ai3_image_confidence FLOAT NULL,
            ai4_object_detection TEXT NULL,
            ai5_nlp_category VARCHAR(100) NULL,
            ai5_nlp_confidence FLOAT NULL,
            ai6_duplicate_status VARCHAR(30) NULL,
            ai6_duplicate_ticket_id VARCHAR(30) NULL,
            ai6_duplicate_distance FLOAT NULL,
            ai7_severity VARCHAR(30) NULL,
            ai7_severity_score INT DEFAULT 0,
            ai7_priority VARCHAR(30) NULL,
            ai7_priority_score INT DEFAULT 0,
            ai7_suggested_dept VARCHAR(100) NULL,
            analyzed_at DATETIME NULL,
            CONSTRAINT fk_ai_ticket FOREIGN KEY (ticket_id) REFERENCES reports(ticket_id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)

        # ตารางประวัติกิจกรรม (activities)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS activities (
            id INT AUTO_INCREMENT PRIMARY KEY,
            ticket_id VARCHAR(30) NOT NULL,
            action VARCHAR(50) NOT NULL,
            officer_name VARCHAR(100) NULL,
            department VARCHAR(100) NULL,
            status VARCHAR(50) NULL,
            message TEXT NULL,
            created_at DATETIME NOT NULL,
            INDEX idx_act_ticket (ticket_id),
            CONSTRAINT fk_act_ticket FOREIGN KEY (ticket_id) REFERENCES reports(ticket_id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)

        # ตารางตั้งค่าระบบ (system_settings)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS system_settings (
            `key` VARCHAR(50) PRIMARY KEY,
            `value` TEXT NOT NULL,
            `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)
        # เพิ่มคอลัมน์ status_reason ใน reports ถ้ายังไม่มี
        try:
            cur.execute("ALTER TABLE reports ADD COLUMN status_reason VARCHAR(255) NULL AFTER status")
        except Exception:
            pass

        # กำหนดค่าเริ่มต้นระบบ (ถ้ายังไม่มี)
        default_settings = [
            ("line_auto_reply", "true"),
            ("line_department_notify", "true"),
            ("ai_auto_analysis", "true"),
            ("database_type", "PostgreSQL")
        ]
        for k, v in default_settings:
            cur.execute("INSERT IGNORE INTO system_settings (`key`, `value`) VALUES (%s, %s)", (k, v))

        # Seed รายชื่อหน่วยงานเริ่มต้น (ถ้ายังไม่มี)
        departments = [
            "กองช่าง",
            "งานป้องกันและบรรเทาสาธารณภัย",
            "งานสาธารณสุขและสิ่งแวดล้อม",
            "งานไฟฟ้า",
            "เจ้าหน้าที่ระบบ"
        ]
        for dept in departments:
            cur.execute("INSERT IGNORE INTO departments (name) VALUES (%s)", (dept,))

    conn.close()
    print("✅ [MySQL] เชื่อมต่อและตรวจสอบโครงสร้างตารางทั้ง 5 ตารางเรียบร้อยแล้ว")


def get_system_settings():
    """
    ดึงการตั้งค่าระบบทั้งหมด คืนค่าเป็น Dict
    เช่น {'line_auto_reply': True, 'line_department_notify': True, 'ai_auto_analysis': True, 'database_type': 'PostgreSQL'}
    """
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("SELECT `key`, `value` FROM system_settings")
            rows = cur.fetchall()
        conn.close()
        settings = {}
        for r in rows:
            val = str(r["value"]).strip()
            if val.lower() == "true":
                settings[r["key"]] = True
            elif val.lower() == "false":
                settings[r["key"]] = False
            else:
                settings[r["key"]] = val

        settings.setdefault("line_auto_reply", True)
        settings.setdefault("line_department_notify", True)
        settings.setdefault("ai_auto_analysis", True)
        settings.setdefault("database_type", "PostgreSQL")
        return settings
    except Exception as e:
        print("Error get_system_settings:", e)
        return {
            "line_auto_reply": True,
            "line_department_notify": True,
            "ai_auto_analysis": True,
            "database_type": "PostgreSQL"
        }


def update_system_setting(key: str, value: str):
    """
    อัปเดตการตั้งค่าระบบ 1 ค่า (เช่น key='line_auto_reply', value='false')
    """
    try:
        val_str = "true" if value is True or str(value).lower() == "true" else ("false" if value is False or str(value).lower() == "false" else str(value))
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("""
            INSERT INTO system_settings (`key`, `value`)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE `value` = %s
            """, (key, val_str, val_str))
        conn.close()
        return True
    except Exception as e:
        print(f"Error update_system_setting({key}, {value}):", e)
        return False


def _format_report_dict(row):
    """แปลงแถวข้อมูล MySQL ให้เป็น Dictionary ที่ตรงกับที่ React Dashboard และ LINE Bot ใช้งาน"""
    if not row:
        return None
    return {
        "ticket_id": row.get("ticket_id"),
        "line_user_id": row.get("line_user_id"),
        "description": row.get("description"),
        "image_message_id": row.get("image_message_id"),
        "image_path": row.get("image_path"),
        "latitude": float(row["latitude"]) if row.get("latitude") is not None else None,
        "longitude": float(row["longitude"]) if row.get("longitude") is not None else None,
        "status": row.get("status") or "รับเรื่องแล้ว",
        "status_reason": row.get("status_reason") or "",
        "created_at": str(row["created_at"]) if row.get("created_at") else "",
        "updated_at": str(row["updated_at"]) if row.get("updated_at") else "",
        "category": row.get("category"),
        "department": row.get("department"),
        "accepted_by": row.get("accepted_by"),
        "accepted_at": str(row["accepted_at"]) if row.get("accepted_at") else None,
        "ai1_image_quality": row.get("ai1_image_quality"),
        "ai2_relevance_status": row.get("ai2_relevance_status"),
        "ai2_relevance_confidence": row.get("ai2_relevance_confidence"),
        "model_b_class": row.get("model_b_class"),
        "model_b_confidence": row.get("model_b_confidence"),
        "model_b_probability": row.get("model_b_probability"),
        "nlp_category": row.get("nlp_category"),
        "nlp_confidence": row.get("nlp_confidence"),
        "ai_department": row.get("ai_department"),
        "object_detection": row.get("object_detection"),
        "duplicate_status": row.get("duplicate_status"),
        "duplicate_ticket_id": row.get("duplicate_ticket_id"),
        "duplicate_distance_meters": row.get("duplicate_distance_meters"),
        "severity": row.get("severity"),
        "severity_score": row.get("severity_score") or 0,
        "priority": row.get("priority"),
        "priority_score": row.get("priority_score") or 0,
    }


def create_report(ticket_id, line_user_id, description, image_message_id, image_path, latitude, longitude):
    """
    บันทึกเรื่องร้องเรียนใหม่ลงตาราง reports และเตรียมแถวใน report_ai_analysis
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_db()
    with conn.cursor() as cur:
        # บันทึกตาราง reports
        cur.execute("""
            INSERT INTO reports (
                ticket_id, line_user_id, description, image_message_id,
                image_path, latitude, longitude, status, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            ticket_id, line_user_id, description, image_message_id,
            image_path, latitude, longitude, "รับเรื่องแล้ว", now, now
        ))

        # บันทึกตาราง report_ai_analysis ตั้งต้น
        cur.execute("""
            INSERT INTO report_ai_analysis (ticket_id, analyzed_at)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE analyzed_at = VALUES(analyzed_at)
        """, (ticket_id, now))
    conn.close()


def delete_report(ticket_id):
    """
    ลบเรื่องร้องเรียนและคืน path รูปภาพที่ผูกกับเรื่องนั้น
    (ตาราง report_ai_analysis และ activities จะถูกลบอัตโนมัติตาม Foreign Key CASCADE)
    """
    conn = get_db()
    image_path = None
    with conn.cursor() as cur:
        cur.execute("SELECT image_path FROM reports WHERE ticket_id = %s", (ticket_id,))
        row = cur.fetchone()
        if row:
            image_path = row.get("image_path")
        cur.execute("DELETE FROM reports WHERE ticket_id = %s", (ticket_id,))
    conn.close()
    return image_path


def get_all_reports():
    """
    ดึงข้อมูลเรื่องร้องเรียนทั้งหมด โดย JOIN ตาราง reports เข้ากับ report_ai_analysis
    สำหรับแสดงผลตาราง แผนที่ และสถิติบน Dashboard
    """
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT 
                r.ticket_id,
                r.line_user_id,
                r.description,
                r.image_message_id,
                r.image_path,
                r.latitude,
                r.longitude,
                r.status,
                r.status_reason,
                r.category,
                r.department,
                r.accepted_by,
                r.accepted_at,
                r.created_at,
                r.updated_at,
                a.ai1_image_quality,
                a.ai2_relevance_status,
                a.ai2_relevance_confidence,
                a.ai3_image_class AS model_b_class,
                a.ai3_image_confidence AS model_b_confidence,
                a.ai4_object_detection AS object_detection,
                a.ai5_nlp_category AS nlp_category,
                a.ai5_nlp_confidence AS nlp_confidence,
                a.ai6_duplicate_status AS duplicate_status,
                a.ai6_duplicate_ticket_id AS duplicate_ticket_id,
                a.ai6_duplicate_distance AS duplicate_distance_meters,
                a.ai7_severity AS severity,
                a.ai7_severity_score AS severity_score,
                a.ai7_priority AS priority,
                a.ai7_priority_score AS priority_score,
                a.ai7_suggested_dept AS ai_department
            FROM reports r
            LEFT JOIN report_ai_analysis a ON r.ticket_id = a.ticket_id
            ORDER BY r.id DESC
        """)
        rows = cur.fetchall()
    conn.close()
    return [_format_report_dict(r) for r in rows]


def get_report_by_ticket(ticket_id):
    """
    ดึงข้อมูลเรื่องร้องเรียนรายการเดียวตาม Ticket ID พร้อมผล AI ทั้งหมด
    """
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT 
                r.ticket_id,
                r.line_user_id,
                r.description,
                r.image_message_id,
                r.image_path,
                r.latitude,
                r.longitude,
                r.status,
                r.status_reason,
                r.category,
                r.department,
                r.accepted_by,
                r.accepted_at,
                r.created_at,
                r.updated_at,
                a.ai1_image_quality,
                a.ai2_relevance_status,
                a.ai2_relevance_confidence,
                a.ai3_image_class AS model_b_class,
                a.ai3_image_confidence AS model_b_confidence,
                a.ai4_object_detection AS object_detection,
                a.ai5_nlp_category AS nlp_category,
                a.ai5_nlp_confidence AS nlp_confidence,
                a.ai6_duplicate_status AS duplicate_status,
                a.ai6_duplicate_ticket_id AS duplicate_ticket_id,
                a.ai6_duplicate_distance AS duplicate_distance_meters,
                a.ai7_severity AS severity,
                a.ai7_severity_score AS severity_score,
                a.ai7_priority AS priority,
                a.ai7_priority_score AS priority_score,
                a.ai7_suggested_dept AS ai_department
            FROM reports r
            LEFT JOIN report_ai_analysis a ON r.ticket_id = a.ticket_id
            WHERE r.ticket_id = %s
        """, (ticket_id,))
        row = cur.fetchone()
    conn.close()
    return _format_report_dict(row)


def get_reports_by_category(category, exclude_ticket_id=None):
    """
    ค้นหา Ticket เดิมที่มีประเภทปัญหาเดียวกัน สำหรับตรวจสอบเรื่องแจ้งซ้ำ (Duplicate Detection)
    """
    conn = get_db()
    with conn.cursor() as cur:
        if exclude_ticket_id:
            cur.execute("""
                SELECT 
                    r.*, 
                    a.ai5_nlp_category AS nlp_category,
                    a.ai3_image_class AS model_b_class
                FROM reports r
                LEFT JOIN report_ai_analysis a ON r.ticket_id = a.ticket_id
                WHERE a.ai5_nlp_category = %s AND r.ticket_id != %s
                ORDER BY r.created_at DESC
            """, (category, exclude_ticket_id))
        else:
            cur.execute("""
                SELECT 
                    r.*, 
                    a.ai5_nlp_category AS nlp_category,
                    a.ai3_image_class AS model_b_class
                FROM reports r
                LEFT JOIN report_ai_analysis a ON r.ticket_id = a.ticket_id
                WHERE a.ai5_nlp_category = %s
                ORDER BY r.created_at DESC
            """, (category,))
        rows = cur.fetchall()
    conn.close()
    return [_format_report_dict(r) for r in rows]


def update_report_duplicate(ticket_id, duplicate_status, duplicate_ticket_id=None, duplicate_distance_meters=None):
    """
    บันทึกผล Duplicate Detection (AI ขั้นตอนที่ 6) ลงในตาราง report_ai_analysis
    """
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE report_ai_analysis
            SET ai6_duplicate_status = %s,
                ai6_duplicate_ticket_id = %s,
                ai6_duplicate_distance = %s,
                analyzed_at = CURRENT_TIMESTAMP
            WHERE ticket_id = %s
        """, (duplicate_status, duplicate_ticket_id, duplicate_distance_meters, ticket_id))
        updated = cur.rowcount > 0
    conn.close()
    return updated


def update_report_status(ticket_id, status, officer_name=None, status_reason=None):
    """
    อัปเดตสถานะของเรื่องร้องเรียน และบันทึกกิจกรรมลงในตาราง activities
    รองรับการระบุเหตุผล/สถานะย่อย (status_reason) เช่น 'รองบประมาณ', 'กำลังลงพื้นที่'
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_db()
    updated = False
    dept = "หน่วยงาน"
    with conn.cursor() as cur:
        if status in ["ดำเนินการเสร็จสิ้น", "เสร็จแล้ว", "รับเรื่องแล้ว"] and status_reason is None:
            # ล้างค่า status_reason เมื่อเปลี่ยนเป็นดำเนินการเสร็จสิ้น หรือรับเรื่องใหม่
            cur.execute("""
                UPDATE reports
                SET status = %s, status_reason = NULL, updated_at = %s
                WHERE ticket_id = %s
            """, (status, now, ticket_id))
        elif status_reason is not None:
            cur.execute("""
                UPDATE reports
                SET status = %s, status_reason = %s, updated_at = %s
                WHERE ticket_id = %s
            """, (status, status_reason, now, ticket_id))
        else:
            cur.execute("""
                UPDATE reports
                SET status = %s, updated_at = %s
                WHERE ticket_id = %s
            """, (status, now, ticket_id))
        updated = cur.rowcount > 0

        if updated:
            cur.execute("SELECT department FROM reports WHERE ticket_id = %s", (ticket_id,))
            row = cur.fetchone()
            if row and row.get("department"):
                dept = row["department"]
    conn.close()

    if updated:
        officer = officer_name or "เจ้าหน้าที่"
        reason_msg = f" (เหตุผล: {status_reason})" if status_reason else ""
        log_activity(
            ticket_id=ticket_id,
            action="status",
            officer_name=officer,
            department=dept,
            status=status,
            message=f"{dept} ({officer}) ได้เปลี่ยนสถานะ {ticket_id} เป็น '{status}'{reason_msg}"
        )
    return updated


def accept_report(ticket_id: str, officer_name: str = "เจ้าหน้าที่"):
    """
    เจ้าหน้าที่กดยืนยันรับเรื่อง (เปลี่ยนสถานะเป็น 'รับเรื่องแล้ว' บันทึกชื่อและเวลา)
    """
    now_display = datetime.now().strftime("%d/%m/%Y %H:%M")
    now_db = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_db()
    updated = False
    dept = "หน่วยงาน"
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE reports
            SET accepted_by = %s,
                accepted_at = %s,
                status = %s,
                updated_at = %s
            WHERE ticket_id = %s
        """, (officer_name, now_db, "รับเรื่องแล้ว", now_db, ticket_id))
        updated = cur.rowcount > 0

        if updated:
            cur.execute("SELECT department FROM reports WHERE ticket_id = %s", (ticket_id,))
            row = cur.fetchone()
            if row and row.get("department"):
                dept = row["department"]
    conn.close()

    if updated:
        log_activity(
            ticket_id=ticket_id,
            action="accept",
            officer_name=officer_name,
            department=dept,
            status="รับเรื่องแล้ว",
            message=f"{dept} ({officer_name}) ได้กดยืนยันรับเรื่อง {ticket_id} แล้ว"
        )
        return {
            "ticket_id": ticket_id,
            "accepted_by": officer_name,
            "accepted_at": now_display,
            "status": "รับเรื่องแล้ว",
            "department": dept
        }
    return None


def cancel_accept_report(ticket_id: str, officer_name: str = "เจ้าหน้าที่", status_reason: str = None):
    """
    ยกเลิกการรับเรื่อง / ยกเลิกงาน (เปลี่ยนสถานะเป็น 'ยกเลิก' และบันทึกผู้กดยกเลิกพร้อมเหตุผล)
    """
    now_display = datetime.now().strftime("%d/%m/%Y %H:%M")
    now_db = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_db()
    updated = False
    dept = "หน่วยงาน"
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE reports
            SET status = 'ยกเลิก',
                status_reason = %s,
                accepted_by = %s,
                accepted_at = %s,
                updated_at = %s
            WHERE ticket_id = %s
        """, (status_reason, officer_name, now_db, now_db, ticket_id))
        updated = cur.rowcount > 0

        if updated:
            cur.execute("SELECT department FROM reports WHERE ticket_id = %s", (ticket_id,))
            row = cur.fetchone()
            if row and row.get("department"):
                dept = row["department"]
    conn.close()

    if updated:
        reason_msg = f" (สาเหตุ: {status_reason})" if status_reason else ""
        log_activity(
            ticket_id=ticket_id,
            action="cancel_accept",
            officer_name=officer_name,
            department=dept,
            status="ยกเลิก",
            message=f"{dept} ({officer_name}) ได้กดยกเลิกรับเรื่อง/ยกเลิกงาน {ticket_id}{reason_msg}"
        )
        return {
            "ticket_id": ticket_id,
            "accepted_by": officer_name,
            "accepted_at": now_display,
            "status": "ยกเลิก",
            "status_reason": status_reason,
            "department": dept
        }
    return None


def update_report_assignment(ticket_id, category, department):
    """
    อัปเดตประเภทปัญหาและหน่วยงานผู้รับผิดชอบ (ใช้เมื่อเจ้าหน้าที่เลือกเปลี่ยนใน Dashboard)
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE reports
            SET category = %s, department = %s, updated_at = %s
            WHERE ticket_id = %s
        """, (category, department, now, ticket_id))
        updated = cur.rowcount > 0
    conn.close()
    return updated


def update_report_image_quality(ticket_id, quality_status):
    """บันทึกผล Image Quality Analysis (AI Step 1) ลงตาราง report_ai_analysis"""
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE report_ai_analysis
            SET ai1_image_quality = %s, analyzed_at = CURRENT_TIMESTAMP
            WHERE ticket_id = %s
        """, (quality_status, ticket_id))
        updated = cur.rowcount > 0
    conn.close()
    return updated


def update_report_relevance(ticket_id, relevance_status, relevance_confidence=None):
    """บันทึกผล Complaint Relevance (AI Step 2) ลงตาราง report_ai_analysis"""
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE report_ai_analysis
            SET ai2_relevance_status = %s, ai2_relevance_confidence = %s, analyzed_at = CURRENT_TIMESTAMP
            WHERE ticket_id = %s
        """, (relevance_status, relevance_confidence, ticket_id))
        updated = cur.rowcount > 0
    conn.close()
    return updated


def update_report_model_b_result(ticket_id, model_b_class, model_b_confidence, model_b_probability=None):
    """บันทึกผล Image Classification Model B (AI Step 3) ลงตาราง report_ai_analysis"""
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE report_ai_analysis
            SET ai3_image_class = %s, ai3_image_confidence = %s, analyzed_at = CURRENT_TIMESTAMP
            WHERE ticket_id = %s
        """, (model_b_class, model_b_confidence, ticket_id))
        updated = cur.rowcount > 0
    conn.close()
    return updated


def update_report_object_detection(ticket_id, object_detection):
    """บันทึกผล YOLO Object Detection (AI Step 4) ลงตาราง report_ai_analysis"""
    conn = get_db()
    obj_json = json.dumps(object_detection, ensure_ascii=False) if isinstance(object_detection, (list, dict)) else str(object_detection)
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE report_ai_analysis
            SET ai4_object_detection = %s, analyzed_at = CURRENT_TIMESTAMP
            WHERE ticket_id = %s
        """, (obj_json, ticket_id))
        updated = cur.rowcount > 0
    conn.close()
    return updated


def update_report_nlp_result(ticket_id, nlp_category, nlp_confidence):
    """บันทึกผล NLP Category (AI Step 5) ลงตาราง report_ai_analysis"""
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE report_ai_analysis
            SET ai5_nlp_category = %s, ai5_nlp_confidence = %s, analyzed_at = CURRENT_TIMESTAMP
            WHERE ticket_id = %s
        """, (nlp_category, nlp_confidence, ticket_id))
        updated = cur.rowcount > 0
    conn.close()
    return updated


def update_report_severity(ticket_id, severity, severity_score):
    """บันทึกผล Severity Assessment (AI Step 6/7) ลงตาราง report_ai_analysis"""
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE report_ai_analysis
            SET ai7_severity = %s, ai7_severity_score = %s, analyzed_at = CURRENT_TIMESTAMP
            WHERE ticket_id = %s
        """, (severity, severity_score, ticket_id))
        updated = cur.rowcount > 0
    conn.close()
    return updated


def update_report_priority(ticket_id, priority, priority_score):
    """บันทึกผล Priority Scoring (AI Step 7) ลงตาราง report_ai_analysis"""
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE report_ai_analysis
            SET ai7_priority = %s, ai7_priority_score = %s, analyzed_at = CURRENT_TIMESTAMP
            WHERE ticket_id = %s
        """, (priority, priority_score, ticket_id))
        updated = cur.rowcount > 0
    conn.close()
    return updated


def update_report_ai_department(ticket_id, ai_department):
    """บันทึกหน่วยงานที่ AI แนะนำ (AI Step 7) ลงตาราง report_ai_analysis"""
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE report_ai_analysis
            SET ai7_suggested_dept = %s, analyzed_at = CURRENT_TIMESTAMP
            WHERE ticket_id = %s
        """, (ai_department, ticket_id))
        updated = cur.rowcount > 0
    conn.close()
    return updated


def get_reports_by_user(line_user_id, limit=3):
    """ดึงรายการเรื่องร้องเรียนล่าสุดของผู้ใช้คนนั้นจาก line_user_id"""
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT ticket_id, description, status, created_at, updated_at
            FROM reports
            WHERE line_user_id = %s
            ORDER BY id DESC
            LIMIT %s
        """, (line_user_id, limit))
        rows = cur.fetchall()
    conn.close()
    return [
        {
            "ticket_id": r.get("ticket_id"),
            "description": r.get("description"),
            "status": r.get("status"),
            "created_at": str(r.get("created_at")),
            "updated_at": str(r.get("updated_at"))
        }
        for r in rows
    ]


def log_activity(ticket_id: str, action: str, officer_name: str, department: str, status: str, message: str):
    """บันทึกกิจกรรมเมื่อเจ้าหน้าที่กดรับเรื่องหรือเปลี่ยนสถานะลงตาราง activities"""
    conn = get_db()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO activities (ticket_id, action, officer_name, department, status, message, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (ticket_id, action, officer_name, department, status, message, now))
    conn.close()


def get_recent_activities(limit: int = 15):
    """ดึงกิจกรรมล่าสุดสำหรับแสดงผลแจ้งเตือนบน Dashboard"""
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, ticket_id, action, officer_name, department, status, message, created_at
            FROM activities
            ORDER BY id DESC
            LIMIT %s
        """, (limit,))
        rows = cur.fetchall()
    conn.close()
    return [
        {
            "id": r.get("id"),
            "ticket_id": r.get("ticket_id"),
            "action": r.get("action"),
            "officer_name": r.get("officer_name"),
            "department": r.get("department"),
            "status": r.get("status"),
            "message": r.get("message"),
            "created_at": str(r.get("created_at"))
        }
        for r in rows
    ]