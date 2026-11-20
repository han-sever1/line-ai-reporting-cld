// ไฟล์: src/pages/SettingsPage.jsx
// หน้าที่: หน้าตั้งค่าระบบ สวิตช์เปิด-ปิด LINE Auto-Reply, Department Notify และ AI

import React from "react";

// หน้าตั้งค่าระบบ
function SettingsPage({
  systemSettings,
  handleToggleSetting,
  settingsSaving,
  settingsNotice,
}) {
  return (
    <div className="page-placeholder settings-page-container">
      <div className="settings-header">
        <h2>⚙️ ตั้งค่าระบบ</h2>
        <p>ควบคุมการทำงานของระบบรับแจ้งปัญหา, การแจ้งเตือน LINE, บอทตอบกลับ และ AI</p>
      </div>

      {settingsNotice && (
        <div className="settings-alert-toast">
          ✅ {settingsNotice}
        </div>
      )}

      <div className="placeholder-card settings-card-box">
        <div className="settings-card-header">
          <h3>⚙️ System Settings (สวิตช์ควบคุมระบบ)</h3>
          <span className="settings-subbadge">Real-time Control</span>
        </div>

        {/* สวิตช์ 1: ระบบตอบกลับอัตโนมัติ / AI Chat */}
        <div className="setting-toggle-row">
          <div className="setting-info">
            <div className="setting-title-line">
              <span className="setting-icon">🤖</span>
              <strong>ระบบ LINE ตอบกลับอัตโนมัติ (LINE Auto-Reply & AI Chat)</strong>
              <span
                className={`status-pill ${
                  systemSettings.line_auto_reply ? "pill-on" : "pill-off"
                }`}
              >
                {systemSettings.line_auto_reply
                  ? "เปิดใช้งาน (Auto)"
                  : "ปิดใช้งาน (Manual แอดมินคุยเอง)"}
              </span>
            </div>
            <p className="setting-desc">
              {systemSettings.line_auto_reply
                ? "เปิดอยู่: บอทและ AI Agent จะคอยตอบข้อความและรับเรื่องร้องเรียนอัตโนมัติ"
                : "ปิดอยู่: บอทจะเงียบสนิท ไม่ส่งข้อความใดๆ ให้เจ้าหน้าที่พิมพ์คุยกับประชาชนผ่าน LINE Official Account Manager ได้เหมือน LINE ทั่วไป"}
            </p>
          </div>
          <div className="setting-control">
            <button
              type="button"
              className={`toggle-switch-btn ${
                systemSettings.line_auto_reply ? "is-active" : ""
              }`}
              onClick={() => handleToggleSetting("line_auto_reply")}
              disabled={settingsSaving}
              aria-label="Toggle LINE Auto-Reply"
            >
              <span className="toggle-switch-slider"></span>
            </button>
          </div>
        </div>

        {/* สวิตช์ 2: ระบบแจ้งเตือน LINE หน่วยงาน */}
        <div className="setting-toggle-row">
          <div className="setting-info">
            <div className="setting-title-line">
              <span className="setting-icon">📢</span>
              <strong>ระบบแจ้งเตือน LINE (Department Group Notification)</strong>
              <span
                className={`status-pill ${
                  systemSettings.line_department_notify ? "pill-on" : "pill-off"
                }`}
              >
                {systemSettings.line_department_notify
                  ? "เปิดใช้งาน"
                  : "ปิดใช้งาน (งดส่งการ์ด)"}
              </span>
            </div>
            <p className="setting-desc">
              {systemSettings.line_department_notify
                ? "เปิดอยู่: ส่งการ์ดแจ้งเตือน Flex Message เข้าไลน์กลุ่มหน่วยงาน (กองช่าง, ไฟฟ้า, ปลัด ฯลฯ) ทันทีที่มีเรื่องร้องเรียน"
                : "ปิดอยู่: บันทึกข้อมูลเข้าระบบตามปกติ แต่งดส่งการ์ดแจ้งเตือนเข้าไลน์กลุ่มหน่วยงาน"}
            </p>
          </div>
          <div className="setting-control">
            <button
              type="button"
              className={`toggle-switch-btn ${
                systemSettings.line_department_notify ? "is-active" : ""
              }`}
              onClick={() => handleToggleSetting("line_department_notify")}
              disabled={settingsSaving}
              aria-label="Toggle Department Notification"
            >
              <span className="toggle-switch-slider"></span>
            </button>
          </div>
        </div>

        {/* สวิตช์ 3: AI วิเคราะห์อัตโนมัติ */}
        <div className="setting-toggle-row">
          <div className="setting-info">
            <div className="setting-title-line">
              <span className="setting-icon">🧠</span>
              <strong>AI วิเคราะห์อัตโนมัติ (AI Pipeline & YOLO Detection)</strong>
              <span
                className={`status-pill ${
                  systemSettings.ai_auto_analysis ? "pill-on" : "pill-off"
                }`}
              >
                {systemSettings.ai_auto_analysis
                  ? "เปิดใช้งาน"
                  : "ปิดใช้งาน (Manual Triage)"}
              </span>
            </div>
            <p className="setting-desc">
              {systemSettings.ai_auto_analysis
                ? "เปิดอยู่: ให้ AI ตรวจจับวัตถุในรูป (YOLO), จำแนกประเภทปัญหา, และคำนวณระดับความเร่งด่วนอัตโนมัติ"
                : "ปิดอยู่: บันทึกเรื่องร้องเรียนแบบพื้นฐาน รอให้เจ้าหน้าที่ตรวจสอบและเลือกหน่วยงานเอง"}
            </p>
          </div>
          <div className="setting-control">
            <button
              type="button"
              className={`toggle-switch-btn ${
                systemSettings.ai_auto_analysis ? "is-active" : ""
              }`}
              onClick={() => handleToggleSetting("ai_auto_analysis")}
              disabled={settingsSaving}
              aria-label="Toggle AI Auto Analysis"
            >
              <span className="toggle-switch-slider"></span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
// จบหน้าตั้งค่าระบบ

export default SettingsPage;
