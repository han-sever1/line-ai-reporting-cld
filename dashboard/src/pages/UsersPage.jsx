// ไฟล์: src/pages/UsersPage.jsx
// หน้าที่: หน้าจัดการบัญชีผู้ใช้งานและสิทธิ์เจ้าหน้าที่

import React from "react";

// หน้าจัดการผู้ใช้
function UsersPage() {
  return (
    <div className="page-placeholder">
      <h2>👥 จัดการผู้ใช้</h2>
      <p>จัดการบัญชีเจ้าหน้าที่และสิทธิ์การใช้งานระบบ</p>

      <div className="placeholder-card">
        <h3>👤 ผู้ใช้งานระบบ</h3>

        <div className="user-demo-row">
          <strong>admin</strong>
          <span>Administrator</span>
          <span className="user-status">● ใช้งานอยู่</span>
        </div>
      </div>
    </div>
  );
}
// จบหน้าจัดการผู้ใช้

export default UsersPage;
