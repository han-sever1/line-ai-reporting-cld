// ไฟล์: src/components/layout/Sidebar.jsx
// หน้าที่: แถบเมนูด้านซ้ายสำหรับเปลี่ยนหน้า พร้อมแสดงสัญลักษณ์และจำนวนเรื่องค้าง

import React from "react";

// แถบเมนูข้าง Sidebar
function Sidebar({
  activePage,
  mobileMenuOpen,
  setMobileMenuOpen,
  handleNavClick,
  stats,
  handleLogout,
}) {
  return (
    <aside className={`sidebar ${mobileMenuOpen ? "mobile-open" : "mobile-closed"}`}>
      {/* โลโก้และชื่อระบบ + ปุ่ม 3 ขีดบนมือถือ พร้อมไฟเขียวเรดาร์ */}
      <div className="sidebar-brand">
        <div className="brand-logo-container">
          <div className="brand-radar-ring"></div>
          <div className="brand-radar-ring ring-2"></div>
          <div className="brand-logo modern-icon-logo">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#ffffff" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14 2 14 8 20 8"></polyline>
              <line x1="9" y1="15" x2="15" y2="15"></line>
            </svg>
          </div>
          <div className="brand-status-dot"></div>
        </div>
        <div className="brand-text">
          <h2>ร้องเรียน(อบต.)</h2>
          <span>v1.0 · Admin Panel</span>
        </div>
        <button
          type="button"
          className="mobile-hamburger-btn"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          aria-label="เมนูนำทาง"
          title="เปิด/ปิด เมนู"
        >
          {mobileMenuOpen ? "✕" : "☰"}
        </button>
      </div>

      {/* เมนู navigation */}
      <nav className="sidebar-nav">
        {/* เมนู Dashboard */}
        <a
          className={`nav-item ${activePage === "dashboard" ? "active" : ""}`}
          onClick={() => handleNavClick("dashboard")}
        >
          <span className="nav-icon">📊</span> Dashboard
        </a>

        {/* เมนูรายการปัญหา — แสดง badge จำนวนที่รอ */}
        <a
          className={`nav-item ${activePage === "reports" ? "active" : ""}`}
          onClick={() => handleNavClick("reports")}
        >
          <span className="nav-icon">📋</span> รายการปัญหา
          {stats.pending > 0 && (
            <span className="nav-badge">{stats.pending}</span>
          )}
        </a>

        {/* เมนูติดตามสถานะ */}
        <a
          className={`nav-item ${activePage === "tracking" ? "active" : ""}`}
          onClick={() => handleNavClick("tracking")}
        >
          <span className="nav-icon">🔍</span> ติดตามสถานะ
        </a>

        {/* เมนูผล AI วิเคราะห์ */}
        <a
          className={`nav-item ${activePage === "ai" ? "active" : ""}`}
          onClick={() => handleNavClick("ai")}
        >
          <span className="nav-icon">🤖</span> ผล AI วิเคราะห์
          <span className="nav-badge" style={{ background: "#8b5cf6" }}>ใหม่</span>
        </a>

        {/* เมนูแผนที่ปัญหา */}
        <a
          className={`nav-item ${activePage === "map" ? "active" : ""}`}
          onClick={() => handleNavClick("map")}
        >
          <span className="nav-icon">🗺️</span> แผนที่ปัญหา
        </a>

        {/* เส้นคั่นแบ่งหมวดหมู่ */}
        <hr className="nav-divider" />

        {/* เมนูจัดการผู้ใช้ */}
        <a
          className={`nav-item ${activePage === "users" ? "active" : ""}`}
          onClick={() => handleNavClick("users")}
        >
          <span className="nav-icon">👥</span> จัดการผู้ใช้
        </a>

        {/* เมนูตั้งค่าระบบ */}
        <a
          className={`nav-item ${activePage === "settings" ? "active" : ""}`}
          onClick={() => handleNavClick("settings")}
        >
          <span className="nav-icon">⚙️</span> ตั้งค่าระบบ
        </a>
      </nav>

      {/* ส่วนท้าย Sidebar — ปุ่มออกจากระบบ */}
      <div className="sidebar-footer">
        <button
          type="button"
          className="sidebar-logout-btn"
          onClick={handleLogout}
          title="ออกจากระบบ"
        >
          <span className="nav-icon">🚪</span>
          <span>ออกจากระบบ</span>
        </button>
      </div>
    </aside>
  );
}
// จบแถบเมนูข้าง Sidebar

export default Sidebar;
