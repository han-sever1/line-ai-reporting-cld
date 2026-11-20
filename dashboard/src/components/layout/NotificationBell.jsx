// ไฟล์: src/components/layout/NotificationBell.jsx
// หน้าที่: ปุ่มกระดิ่งแจ้งเตือน Real-time พร้อมดรอปดาวน์แสดงเรื่องร้องเรียนล่าสุด

import React from "react";
import { formatShortThaiDate } from "../../utils/dateUtils";

// กระดิ่งแจ้งเตือน
function NotificationBell({
  reports,
  isBellRinging,
  showNotifMenu,
  setShowNotifMenu,
  notifRef,
  onSelectReport,
  onViewAllReports,
}) {
  const pendingReports = reports.filter((r) => r.status === "รับเรื่องแล้ว");
  const pendingCount = pendingReports.length;

  return (
    <div className="notif-bell-container" ref={notifRef}>
      <button
        type="button"
        className={`notif-bell-btn ${isBellRinging ? "notif-bell-ringing" : ""}`}
        onClick={() => setShowNotifMenu((prev) => !prev)}
        title="แจ้งเตือนเรื่องร้องเรียนใหม่ (คลิกเพื่อดูรายการ)"
        aria-label="แจ้งเตือนเรื่องร้องเรียนใหม่"
      >
        🔔
        {pendingCount > 0 && (
          <span className="notif-badge notif-badge-pulse">
            {pendingCount > 9 ? "9+" : pendingCount}
          </span>
        )}
      </button>

      {showNotifMenu && (
        <div className="notif-dropdown">
          <div className="notif-dropdown-header">
            <strong>🔔 เรื่องร้องเรียนล่าสุด</strong>
            <span className="notif-total-badge">
              ใหม่ {pendingCount} เรื่อง
            </span>
          </div>

          <div className="notif-list">
            {reports.length > 0 ? (
              reports.slice(0, 8).map((item) => (
                <div
                  key={item.ticket_id}
                  className={`notif-item notif-item-clickable ${
                    item.status === "รับเรื่องแล้ว" ? "notif-unread" : ""
                  }`}
                  onClick={() => onSelectReport(item)}
                >
                  <span className="notif-dot">
                    {item.status === "รับเรื่องแล้ว" ? "🔴" : "🟢"}
                  </span>
                  <div className="notif-info">
                    <div className="notif-item-head">
                      <span className="notif-ticket">#{item.ticket_id}</span>
                      <span
                        className={`notif-status-tag ${
                          item.status === "รับเรื่องแล้ว" ? "tag-pending" : "tag-done"
                        }`}
                      >
                        {item.status}
                      </span>
                    </div>
                    <p className="notif-text">
                      {item.description || "ไม่ระบุรายละเอียด"}
                    </p>
                    <span className="notif-time">
                      {item.created_at
                        ? formatShortThaiDate(item.created_at) || item.created_at
                        : "เมื่อสักครู่"}
                    </span>
                  </div>
                </div>
              ))
            ) : (
              <div className="notif-empty">ไม่มีรายการเรื่องร้องเรียน</div>
            )}
          </div>

          <div className="notif-dropdown-footer">
            <button
              type="button"
              className="notif-view-all-btn"
              onClick={onViewAllReports}
            >
              📋 ดูหน้ารายการปัญหาทั้งหมด
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
// จบกระดิ่งแจ้งเตือน

export default NotificationBell;
