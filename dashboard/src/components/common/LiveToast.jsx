// ไฟล์: src/components/common/LiveToast.jsx
// หน้าที่: แสดงกล่องแจ้งเตือนป๊อปอัปมุมขวาบนเมื่อเจ้าหน้าที่อัปเดตผ่าน LINE แบบเรียลไทม์

import React from "react";

// แสดงผล LiveToast
function LiveToast({ liveToast, onClose }) {
  if (!liveToast) return null;

  return (
    <div className="live-toast-alert" onClick={onClose}>
      <div className="toast-icon">
        {liveToast.action === "accept"
          ? "👷‍♂️"
          : liveToast.status === "ดำเนินการเสร็จสิ้น"
          ? "🎉"
          : liveToast.status === "รอแก้ไข"
          ? "⏳"
          : "⚙️"}
      </div>
      <div className="toast-body">
        <div className="toast-title">
          {liveToast.action === "accept"
            ? "✅ เจ้าหน้าที่ยืนยันรับเรื่องแล้ว"
            : `📢 เจ้าหน้าที่อัปเดตสถานะ: [${liveToast.status}]`}
        </div>
        <div className="toast-desc">{liveToast.message}</div>
        <div className="toast-time">เมื่อสักครู่ ({liveToast.created_at})</div>
      </div>
      <button
        type="button"
        className="toast-close"
        onClick={(e) => {
          e.stopPropagation();
          onClose();
        }}
      >
        ×
      </button>
    </div>
  );
}
// จบแสดงผล LiveToast

export default LiveToast;
