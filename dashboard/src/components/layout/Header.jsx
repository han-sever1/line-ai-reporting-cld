// ไฟล์: src/components/layout/Header.jsx
// หน้าที่: แถบส่วนหัวด้านบน ประกอบด้วยปุ่มเมนูมือถือ หัวข้อหน้า ตัวกรองปฏิทิน สลับธีม กระดิ่ง และปุ่มออกจากระบบ

import React from "react";
import NotificationBell from "./NotificationBell";
import { thaiMonthsNames, timeFilterOptions } from "../../utils/dateUtils";

// แถบส่วนหัว Header
function Header({
  activePage,
  mobileMenuOpen,
  setMobileMenuOpen,
  searchText,
  setSearchText,
  // Date filter props
  globalTimeFilter,
  setGlobalTimeFilter,
  customStartDate,
  setCustomStartDate,
  customEndDate,
  setCustomEndDate,
  calendarViewDate,
  showGlobalTimeMenu,
  setShowGlobalTimeMenu,
  globalTimeRef,
  reportDatesSet,
  getGlobalTimeFilterLabel,
  handlePrevMonth,
  handleNextMonth,
  handleMonthChange,
  handleYearChange,
  handleCalendarDayClick,
  daysInCurrentMonth,
  firstDayOfWeek,
  calYear,
  calMonth,
  // Theme & Notif
  darkMode,
  toggleDarkMode,
  reports,
  isBellRinging,
  setIsBellRinging,
  showNotifMenu,
  setShowNotifMenu,
  notifRef,
  onSelectReportFromNotif,
  onViewAllReports,
  handleLogout,
}) {
  const getPageTitle = () => {
    switch (activePage) {
      case "dashboard": return "Dashboard · ภาพรวมระบบ";
      case "reports": return "รายการปัญหา · จัดการแจ้งปัญหา";
      case "tracking": return "ติดตามสถานะ · เรื่องร้องเรียน";
      case "ai": return "ผล AI วิเคราะห์ · ระบบตรวจจับปัญหา";
      case "map": return "แผนที่ปัญหา · ตำแหน่ง GPS";
      case "users": return "จัดการผู้ใช้ · บัญชีเจ้าหน้าที่";
      case "settings": return "ตั้งค่าระบบ · อบต.สุไหงโกลก";
      default: return "ระบบรับแจ้งปัญหา";
    }
  };

  return (
    <header className="top-header">
      <div className="header-title">
        <button
          type="button"
          className="mobile-hamburger-btn mobile-hamburger-header"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          aria-label="เมนูนำทาง"
          title="เปิด/ปิด เมนู"
        >
          ☰
        </button>
        <h1>{getPageTitle()}</h1>
      </div>

      <div className="header-actions">
        {/* ช่องค้นหา (แสดงในหน้า reports, tracking, map) */}
        {(activePage === "reports" || activePage === "tracking" || activePage === "map") && (
          <div className="search-box">
            <span className="search-icon">🔍</span>
            <input
              type="text"
              placeholder="ค้นหา Ticket ID หรือรายละเอียด..."
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
            />
          </div>
        )}

        {/* ตัวกรองเวลาและปฏิทิน */}
        <div className="time-filter-dropdown-container" ref={globalTimeRef}>
          <button
            type="button"
            className={`global-time-filter-btn ${globalTimeFilter !== "all" ? "active" : ""}`}
            onClick={() => setShowGlobalTimeMenu((prev) => !prev)}
            title="กรองช่วงเวลาข้อมูลในระบบ"
          >
            <span className="filter-btn-icon">📅</span>
            <span className="filter-btn-text">{getGlobalTimeFilterLabel()}</span>
            <span className="dropdown-arrow">▼</span>
          </button>

          {showGlobalTimeMenu && (
            <div className="calendar-dropdown-card">
              <div className="cal-dropdown-header">
                <span className="cal-dropdown-title">📅 เลือกช่วงเวลาหรือวันที่</span>
                <button
                  type="button"
                  className="cal-close-btn"
                  onClick={() => setShowGlobalTimeMenu(false)}
                  title="ปิด"
                >
                  ✕
                </button>
              </div>

              {/* ปุ่มลัดเลือกเวลาด่วน */}
              <div className="cal-presets-row">
                {timeFilterOptions.map((opt) => (
                  <button
                    key={opt.value}
                    type="button"
                    className={`cal-preset-btn ${globalTimeFilter === opt.value ? "active" : ""}`}
                    onClick={() => {
                      setGlobalTimeFilter(opt.value);
                      if (opt.value !== "custom") {
                        setCustomStartDate("");
                        setCustomEndDate("");
                        setShowGlobalTimeMenu(false);
                      }
                    }}
                  >
                    <span>{opt.icon}</span> {opt.label}
                  </button>
                ))}
              </div>

              {/* นำทางเดือนและปี */}
              <div className="cal-month-nav">
                <button type="button" className="cal-nav-arrow" onClick={handlePrevMonth}>◀</button>
                <div className="cal-selectors-group">
                  <select
                    value={calMonth}
                    onChange={(e) => handleMonthChange(e.target.value)}
                    className="cal-select-month"
                  >
                    {thaiMonthsNames.map((name, i) => (
                      <option key={i} value={i}>{name}</option>
                    ))}
                  </select>
                  <select
                    value={calYear}
                    onChange={(e) => handleYearChange(e.target.value)}
                    className="cal-select-year"
                  >
                    {Array.from({ length: 6 }, (_, idx) => 2024 + idx).map((y) => (
                      <option key={y} value={y}>{y + 543}</option>
                    ))}
                  </select>
                </div>
                <button type="button" className="cal-nav-arrow" onClick={handleNextMonth}>▶</button>
              </div>

              {/* วันในสัปดาห์ */}
              <div className="cal-weekdays-grid">
                <span className="cal-weekday-label sunday">อา</span>
                <span className="cal-weekday-label">จ</span>
                <span className="cal-weekday-label">อ</span>
                <span className="cal-weekday-label">พ</span>
                <span className="cal-weekday-label">พฤ</span>
                <span className="cal-weekday-label">ศ</span>
                <span className="cal-weekday-label">ส</span>
              </div>

              {/* ตารางวันที่ในเดือน */}
              <div className="cal-days-grid">
                {Array.from({ length: firstDayOfWeek }).map((_, idx) => (
                  <span key={`empty-${idx}`} className="cal-day-cell empty"></span>
                ))}

                {Array.from({ length: daysInCurrentMonth }, (_, idx) => {
                  const dayNum = idx + 1;
                  const dayStr = `${calYear}-${String(calMonth + 1).padStart(2, "0")}-${String(dayNum).padStart(2, "0")}`;
                  const isSelected = customStartDate === dayStr || customEndDate === dayStr;
                  const hasReport = reportDatesSet.has(dayStr);
                  const isToday = (() => {
                    const t = new Date();
                    return t.getFullYear() === calYear && t.getMonth() === calMonth && t.getDate() === dayNum;
                  })();

                  return (
                    <button
                      key={`day-${dayNum}`}
                      type="button"
                      className={`cal-day-cell ${isSelected ? "selected" : ""} ${isToday ? "today" : ""}`}
                      onClick={() => handleCalendarDayClick(dayNum)}
                      title={hasReport ? "มีเรื่องร้องเรียนในวันนี้" : ""}
                    >
                      <span>{dayNum}</span>
                      {hasReport && <span className="cal-day-dot"></span>}
                    </button>
                  );
                })}
              </div>

              {/* ส่วนกำหนดช่วงวันเอง */}
              <div className="cal-range-section">
                <span className="cal-range-header">หรือกำหนดช่วงวันที่เอง:</span>
                <div className="cal-range-inputs">
                  <div className="cal-input-group">
                    <label>ตั้งแต่วันที่</label>
                    <input
                      type="date"
                      value={customStartDate}
                      onChange={(e) => {
                        setCustomStartDate(e.target.value);
                        setGlobalTimeFilter("custom");
                      }}
                    />
                  </div>
                  <div className="cal-input-group">
                    <label>ถึงวันที่</label>
                    <input
                      type="date"
                      value={customEndDate}
                      onChange={(e) => {
                        setCustomEndDate(e.target.value);
                        setGlobalTimeFilter("custom");
                      }}
                    />
                  </div>
                </div>

                <div className="cal-footer-actions">
                  <button
                    type="button"
                    className="cal-btn-reset"
                    onClick={() => {
                      setGlobalTimeFilter("all");
                      setCustomStartDate("");
                      setCustomEndDate("");
                      setShowGlobalTimeMenu(false);
                    }}
                  >
                    ล้างค่า
                  </button>
                  <button
                    type="button"
                    className="cal-btn-apply"
                    onClick={() => setShowGlobalTimeMenu(false)}
                  >
                    นำไปใช้
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* สลับ Dark/Light Mode */}
        <button
          type="button"
          className="dark-mode-toggle"
          onClick={toggleDarkMode}
          title={darkMode ? "เปลี่ยนเป็น Light Mode" : "เปลี่ยนเป็น Dark Mode"}
        >
          {darkMode ? "☀️" : "🌙"}
        </button>

        {/* ปุ่มกระดิ่งแจ้งเตือน */}
        <NotificationBell
          reports={reports}
          isBellRinging={isBellRinging}
          showNotifMenu={showNotifMenu}
          setShowNotifMenu={(fn) => {
            setShowNotifMenu(fn);
            setIsBellRinging(false);
          }}
          notifRef={notifRef}
          onSelectReport={onSelectReportFromNotif}
          onViewAllReports={onViewAllReports}
        />

        {/* ปุ่มออกจากระบบ */}
        <button
          type="button"
          className="logout-btn"
          onClick={handleLogout}
          title="ออกจากระบบ"
        >
          ออกจากระบบ
        </button>

        {/* Avatar ผู้ใช้ */}
        <div className="header-avatar" title="ผู้ดูแลระบบ (Admin)">
          A
        </div>
      </div>
    </header>
  );
}
// จบแถบส่วนหัว Header

export default Header;
