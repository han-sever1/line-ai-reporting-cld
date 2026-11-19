# ระบบรับแจ้งปัญหาและติดตามสถานะผ่าน LINE พร้อม AI วิเคราะห์อัตโนมัติ
## (Smart Complaint Reporting & Tracking System via LINE with AI & Web Admin Dashboard)
**สำหรับองค์การบริหารส่วนตำบล (อบต.สุไหงโกลก)**

---

## 📌 ภาพรวมสถาปัตยกรรมระบบ (System Architecture)
ระบบถูกพัฒนาตามสถาปัตยกรรม 3-Tier Layered Architecture แบ่งออกเป็น 3 ส่วนหลัก:
1. **ส่วนติดต่อประชาชน (Citizen Interface):** LINE Official Account (Rich Menu 3 เมนูหลัก, Guided Dialog 3 ขั้นตอน, Flex Message ตอบรับอัตโนมัติ)
2. **ส่วนประมวลผลแบ็กเอนด์และปัญญาประดิษฐ์ (Backend & AI Engine):** Python FastAPI + MySQL (XAMPP) + AI Pipeline 7 มิติ + n8n Automation
3. **ส่วนบริหารจัดการข้อมูลสำหรับเจ้าหน้าที่ (Web Admin Dashboard):** React 18 (Vite) + Tailwind CSS + Leaflet.js GIS Interactive Map + WebSocket Real-time

---

## 📂 โครงสร้างไฟล์ทั้งหมดของโปรเจกต์ (Project Directory Structure)

```
d:\line-ai-reporting-cld\
│
├── 📁 dashboard/                          # [FRONTEND] เว็บแอปพลิเคชันสำหรับเจ้าหน้าที่และผู้บริหาร
│   ├── 📁 public/                         # ไฟล์ Static (Favicon, Icons)
│   ├── 📁 src/                            # ซอร์สโค้ด React ทั้งหมด
│   │   ├── 📁 assets/                     # รูปภาพและ SVG ประกอบ UI
│   │   ├── 📁 components/                 # คอมโพเนนต์แยกตามโมดูล
│   │   │   ├── 📁 common/                 # คอมโพเนนต์ส่วนกลาง (LiveToast.jsx แจ้งเตือน Popup)
│   │   │   ├── 📁 layout/                 # โครงสร้างหน้าเว็บ (Sidebar, Header, NotificationBell)
│   │   │   ├── 📁 map/                    # แผนที่ GIS (ProblemMap.jsx บน Leaflet.js)
│   │   │   └── 📁 reports/                # จัดการใบงาน (ReportDetailDrawer.jsx รายละเอียดตั๋วงาน)
│   │   ├── 📁 pages/                      # หน้าจอการทำงานหลัก (Pages)
│   │   │   ├── DashboardPage.jsx          # หน้าแดชบอร์ดสรุปสถิติ KPI Cards และกราฟแนวโน้ม
│   │   │   ├── ReportsPage.jsx            # หน้ารายการตั๋วงาน (ตัวกรอง 3 ระดับ: ปกติ/ปานกลาง/เร่งด่วน)
│   │   │   ├── MapPage.jsx                # หน้าแผนที่สารสนเทศภูมิศาสตร์ GIS + ปุ่มนำทาง GPS
│   │   │   ├── AiAnalyticsPage.jsx        # หน้าจอแสดงผลการวิเคราะห์ AI 7 มิติเชิงลึก
│   │   │   ├── TrackingPage.jsx           # หน้าจอค้นหาและติดตามสถานะงานสำหรับประชาชน
│   │   │   ├── UsersPage.jsx              # หน้าจัดการบัญชีผู้ใช้งานและเจ้าหน้าที่
│   │   │   └── SettingsPage.jsx           # หน้าตั้งค่าระบบและหน่วยงานรับผิดชอบ
│   │   ├── 📁 services/                   # บริการเชื่อมต่อ API (api.js เชื่อมโยง FastAPI)
│   │   ├── 📁 utils/                      # ฟังก์ชันช่วยเหลือ (dateUtils.js แปลงวันที่ไทย, sound.js เสียงแจ้งเตือน)
│   │   ├── App.jsx                        # ศูนย์กลางการ Routing, จัดการสิทธิ์ และ WebSocket
│   │   ├── Login.jsx                      # หน้าต่างเข้าสู่ระบบของเจ้าหน้าที่
│   │   └── main.jsx                       # จุดเริ่มต้นการเรนเดอร์ React แอปพลิเคชัน
│   ├── package.json                       # รายการ Library ของ Node.js (React, Lucide, Leaflet, etc.)
│   └── vite.config.js                     # การตั้งค่าเซิร์ฟเวอร์สำหรับพัฒนาและ Build ของ Vite
│
├── 📁 models/                             # [AI MODELS] แบบจำลองปัญญาประดิษฐ์ที่ผ่านการฝึกฝน
│   ├── model_B_image_classification_4_classes.keras  # โมเดลจำแนกภาพความเสียหาย 4 ประเภท
│   └── model_B_class_names.json           # รายชื่อคลาส (garbage, road_damage, street_light, water_supply)
│
├── 📁 uploads/                            # [MEDIA STORAGE] โฟลเดอร์จัดเก็บภาพถ่ายความเสียหายจาก LINE
│
├── 🧠 โมดูลระบบปัญญาประดิษฐ์ 7 มิติ (AI Pipeline Core)
│   ├── image_quality_ai.py                # AI 1: ตรวจสอบความคมชัดของภาพ (Laplacian Variance ป้องกันภาพเบลอ)
│   ├── complaint_relevance_ai.py          # AI 2: คัดกรองภาพถ่ายปัญหาเทศบาลจริง ป้องกันภาพอาหาร/เซลฟี่
│   ├── image_classification_ai.py         # AI 3: จำแนกประเภทความเสียหายของโครงสร้างพื้นฐาน (4 คลาส)
│   ├── object_detection_ai.py             # AI 4: ตรวจจับวัตถุในภาพด้วย YOLO11 (yolo11n.pt)
│   ├── nlp_category_ai.py                 # AI 5: ประมวลผลข้อความภาษาไทยด้วย PyThaiNLP เพื่อจำแนกกองงาน
│   ├── duplicate_detection_ai.py          # AI 6: ตรวจจับการแจ้งเหตุซ้ำซ้อนด้วย Haversine Formula (30ม. / 48ชม.)
│   └── severity_ai.py / priority_scoring_ai.py # AI 7: ประเมินคะแนนความรุนแรง (1-3) และความเร่งด่วน (0-100)
│
├── ⚙️ บริการแบ็กเอนด์และการเชื่อมต่อ (Backend & Services)
│   ├── main.py                            # เซิร์ฟเวอร์หลัก FastAPI: รองรับ Webhook LINE, REST APIs, WebSocket
│   ├── database.py                        # เชื่อมต่อฐานข้อมูล MySQL (XAMPP) พร้อมโครงสร้างตาราง 3NF
│   ├── line_service.py                    # ส่ง-รับข้อความ LINE Messaging API, Rich Menu, Flex Message
│   ├── n8n_service.py                     # เชื่อมต่อ Webhook ส่งข้อมูลไปยัง n8n Automation
│   ├── session.py                         # บันทึกสถานะการสนทนาของประชาชนแบบ Step-by-step
│   ├── ticket.py                          # สร้างหมายเลขตั๋วงานอัตโนมัติรูปแบบ 'TK-XXXX'
│   ├── create_rich_menu.py                # สคริปต์สร้างและผูกริชเมนูเข้ากับ LINE Official Account
│   ├── generate_rich_menu_2500.py         # สคริปต์สร้างไฟล์ภาพริชเมนูขนาดมาตรฐาน 2,500 x 1,686 พิกเซล
│   └── yolo11n.pt                         # น้ำหนักโมเดล Ultralytics YOLO11 สำหรับตรวจจับวัตถุ
│
├── 📄 ไฟล์รูปภาพเมนูและแผนภาพระบบ (System Assets)
│   ├── rich_menu_tall_2500x1686.jpg       # ภาพ Rich Menu 3 เมนูหลักที่ติดตั้งบน LINE OA จริง
│   ├── rich_menu_custom.png / .jpg        # ไฟล์ต้นฉบับภาพ Rich Menu
│   ├── sdlc_diagram.png                   # แผนภาพวงจรการพัฒนาระบบ (SDLC)
│   ├── system_architecture.png            # แผนภาพสถาปัตยกรรมระบบโดยรวม
│   ├── system_flowchart.png               # ผังงานกระบวนการทำงานของระบบ
│   └── dfd_level_1.png                    # แผนภาพกระแสข้อมูล DFD Level 1
│
├── 📑 เอกสารวิจัยและสไลด์นำเสนอผลงาน (Master Documents)
│   ├── รายงานวิจัย.docx                   # เล่มรายงานวิจัยฉบับสมบูรณ์ 100% (บทที่ 1 ถึง บทที่ 5)
│   └── Smart_Complaint_Presentation.pptx  # สไลด์นำเสนอโครงงาน 20 สไลด์ พร้อมข้อมูลสถาปัตยกรรมระบบ
│
├── 🔐 ไฟล์การตั้งค่าสภาพแวดล้อม (Configuration)
│   ├── .env                               # เก็บกุญแจความลับ (LINE Token, DB Config, n8n Webhook URL)
│   └── requirements.txt                   # รายชื่อแพ็กเกจ Python ทั้งหมดที่ระบบต้องการ
```

---

## 🚀 รายละเอียดการทำงานของหน้าเว็บ Web Admin Dashboard (`dashboard/`)

| หน้าจอ (Page) | ไฟล์ต้นฉบับ | รายละเอียดหน้าที่การทำงาน |
| :--- | :--- | :--- |
| **ภาพรวม (Dashboard)** | `DashboardPage.jsx` | แสดงตัวชี้วัดสำคัญ (KPI Cards) 4 ช่อง: จำนวนเรื่องทั้งหมด (71 รายการ), รอดำเนินการ, แก้ไขแล้วเสร็จ, เรื่องเร่งด่วน พร้อมแผนภูมิแท่งเปรียบเทียบสถิติกองงาน และแผนภูมิวงกลมแสดงสัดส่วนประเภทความเสียหาย |
| **รายการใบงาน (Reports)** | `ReportsPage.jsx` | ตารางข้อมูลใบงานทั้งหมด รองรับการค้นหา คัดกรองตามสถานะ, กองงาน และ **ตัวกรองระดับความเร่งด่วน 3 ระดับ (ปกติ, ปานกลาง, เร่งด่วน)** พร้อมปุ่มกดดูรายละเอียด และปุ่มมอบหมายงาน |
| **แผนที่ปัญหา (GIS Map)** | `MapPage.jsx` + `ProblemMap.jsx` | แผนที่ดิจิทัลบน OpenStreetMap ด้วย Leaflet.js ปักหมุดตามพิกัดดาวเทียมจริงในพื้นที่ อบต.สุไหงโกลก แยกสีหมุดตามระดับความเร่งด่วน เมื่อคลิกจะแสดง Popup ภาพถ่าย พิกัด GPS และ **ปุ่มนำทางผ่าน Google Maps** |
| **วิเคราะห์ AI (AI Analytics)** | `AiAnalyticsPage.jsx` | แสดงผลการวิเคราะห์ของ AI Pipeline 7 มิติเชิงลึกสำหรับแต่ละตั๋วงาน เช่น คะแนนความคมชัด, % ความน่าจะเป็นของประเภทปัญหา, วัตถุที่ตรวจจับได้จาก YOLO และการตรวจจับเหตุซ้ำ |
| **ติดตามสถานะ (Tracking)** | `TrackingPage.jsx` | พอร์ทัลสำหรับตรวจสอบสถานะใบงาน เพียงกรอกรหัส Ticket ID (เช่น TK-0072) จะแสดง Timeline ขั้นตอนการซ่อมแซมและภาพถ่ายยืนยันหลังการแก้ไข |
| **จัดการผู้ใช้งาน (Users)** | `UsersPage.jsx` | จัดการรายชื่อเจ้าหน้าที่ผู้ใช้งานระบบ ผู้ดูแลระบบ (Admin) และกำหนดสิทธิ์การเข้าถึงข้อมูลของแต่ละกองงาน |
| **ตั้งค่าระบบ (Settings)** | `SettingsPage.jsx` | ตั้งค่าข้อมูลหน่วยงาน อบต.สุไหงโกลก, การแจ้งเตือน และการเชื่อมต่อ Webhook ภายนอก |

---

## ⚡ วิธีการรันระบบ (How to Run)

### 1. รันระบบ Backend & AI Server (FastAPI)
```powershell
# เปิดใช้งานสภาพแวดล้อมเสมือน (Virtual Environment)
.venv\Scripts\activate

# เริ่มต้นเซิร์ฟเวอร์ FastAPI (พอร์ต 8000)
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. รันระบบ Frontend Web Dashboard (React + Vite)
```powershell
cd dashboard

# ติดตั้ง Dependencies (ทำเฉพาะครั้งแรก)
npm install

# รันเซิร์ฟเวอร์สำหรับนักพัฒนา (พอร์ต 5173)
npm run dev
```
เข้าใช้งานผ่านเบราว์เซอร์ที่: `http://localhost:5173`
