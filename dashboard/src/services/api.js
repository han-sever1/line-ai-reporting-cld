// ไฟล์: src/services/api.js
// หน้าที่: รวมฟังก์ชันเชื่อมต่อ Backend FastAPI ทั้งหมด

const API_BASE = "http://localhost:8000";

// ดึงข้อมูลรายงาน
export const fetchReportsApi = async () => {
  const response = await fetch(`${API_BASE}/reports`);
  if (!response.ok) {
    throw new Error("ดึงข้อมูลไม่สำเร็จ");
  }
  return await response.json();
};
// จบดึงข้อมูลรายงาน

// ดึงประวัติกิจกรรม
export const fetchActivitiesApi = async () => {
  const response = await fetch(`${API_BASE}/activities`);
  if (!response.ok) {
    throw new Error("ดึงประวัติกิจกรรมไม่สำเร็จ");
  }
  return await response.json();
};
// จบดึงประวัติกิจกรรม

// ดึงรายละเอียดตั๋ว
export const fetchReportDetailApi = async (ticketId) => {
  const response = await fetch(`${API_BASE}/reports/${ticketId}`);
  if (!response.ok) {
    throw new Error("ไม่พบรายละเอียด Ticket");
  }
  return await response.json();
};
// จบดึงรายละเอียดตั๋ว

// อัปเดตสถานะตั๋ว (รองรับการระบุเหตุผล/ความคืบหน้า)
export const updateStatusApi = async (ticketId, newStatus, statusReason = null) => {
  const response = await fetch(`${API_BASE}/reports/${ticketId}/status`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status: newStatus, status_reason: statusReason }),
  });
  if (!response.ok) {
    throw new Error("อัปเดตสถานะไม่สำเร็จ");
  }
  return await response.json();
};
// จบอัปเดตสถานะตั๋ว

// ยืนยันรับเรื่องโดยเจ้าหน้าที่
export const acceptReportApi = async (ticketId, officerName) => {
  const response = await fetch(`${API_BASE}/reports/${ticketId}/accept`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ officer_name: officerName }),
  });
  if (!response.ok) {
    throw new Error("ยืนยันรับเรื่องไม่สำเร็จ");
  }
  return await response.json();
};
// จบยืนยันรับเรื่องโดยเจ้าหน้าที่

// อัปเดตการมอบหมายงาน
export const updateAssignmentApi = async (ticketId, category, department) => {
  const response = await fetch(`${API_BASE}/reports/${ticketId}/assignment`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ category, department }),
  });
  if (!response.ok) {
    throw new Error("อัปเดตประเภท/หน่วยงานไม่สำเร็จ");
  }
  return await response.json();
};
// จบอัปเดตการมอบหมายงาน

// ลบรายงาน
export const deleteReportApi = async (ticketId) => {
  const response = await fetch(`${API_BASE}/reports/${ticketId}`, {
    method: "DELETE",
  });
  if (!response.ok) {
    throw new Error("ลบเรื่องร้องเรียนไม่สำเร็จ");
  }
  return await response.json();
};
// จบลบรายงาน

// การตั้งค่าระบบ
export const fetchSettingsApi = async () => {
  const response = await fetch(`${API_BASE}/api/settings`);
  if (!response.ok) {
    throw new Error("ดึงการตั้งค่าระบบไม่สำเร็จ");
  }
  return await response.json();
};

export const updateSettingApi = async (key, value) => {
  const response = await fetch(`${API_BASE}/api/settings`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ key, value }),
  });
  if (!response.ok) {
    throw new Error("บันทึกการตั้งค่าระบบไม่สำเร็จ");
  }
  return await response.json();
};
// จบการตั้งค่าระบบ
