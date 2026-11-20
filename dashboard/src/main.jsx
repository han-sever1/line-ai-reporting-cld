import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

// ======================= Router (เพิ่มใหม่) =======================
// BrowserRouter คือตัวที่ทำให้แอปของเรามี "หลายหน้า" ได้ เช่น
// หน้า Dashboard (/)  และหน้ารายการปัญหา (/reports)
// โดยไม่ต้อง reload หน้าเว็บใหม่ทั้งหมด (เปลี่ยนแค่เนื้อหาข้างใน)
// ต้องติดตั้งก่อนใช้งาน ด้วยคำสั่ง:
//   npm install react-router-dom
import { BrowserRouter } from 'react-router-dom'
// ==================== จบ Router (เพิ่มใหม่) ========================

createRoot(document.getElementById('root')).render(
  <StrictMode>
    {/* ห่อ App ทั้งก้อนด้วย BrowserRouter เพื่อให้ App.jsx
        ใช้ <Routes> / <Link> / useNavigate ได้ทุกที่ */}
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </StrictMode>,
)