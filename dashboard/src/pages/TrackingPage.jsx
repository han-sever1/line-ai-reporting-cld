// ไฟล์: src/pages/TrackingPage.jsx
// หน้าที่: หน้าติดตามสถานะเรื่องร้องเรียน และการค้นหาตามเลข Ticket

import React from "react";

// หน้าติดตามสถานะ
function TrackingPage({ reports, trackingReports, searchText, onSelectReport }) {
  return (
    <div className="page-placeholder">
      <h2>🔍 ติดตามสถานะ</h2>
      <p>ตรวจสอบสถานะการดำเนินงานของรายการร้องเรียน</p>

      {/* กล่องสรุปจำนวน Ticket */}
      <div className="tracking-summary">
        <div className="tracking-summary-card">
          <span>รายการทั้งหมด</span>
          <strong>{reports.length}</strong>
        </div>

        <div className="tracking-summary-card">
          <span>รอดำเนินการ</span>
          <strong>
            {
              reports.filter(
                (item) => item.status === "pending" || item.status === "รับเรื่องแล้ว"
              ).length
            }
          </strong>
        </div>

        <div className="tracking-summary-card">
          <span>กำลังดำเนินการ</span>
          <strong>
            {
              reports.filter(
                (item) => item.status === "in_progress" || item.status === "กำลังดำเนินการ"
              ).length
            }
          </strong>
        </div>

        <div className="tracking-summary-card">
          <span>เสร็จสิ้น</span>
          <strong>
            {
              reports.filter(
                (item) => item.status === "resolved" || item.status === "เสร็จสิ้น" || item.status === "ดำเนินการเสร็จสิ้น"
              ).length
            }
          </strong>
        </div>
      </div>

      {/* ตารางติดตามสถานะ */}
      <div className="placeholder-card">
        <h3>📋 รายการติดตามสถานะ</h3>

        <div className="tracking-table-wrapper">
          <table className="tracking-table">
            <thead>
              <tr>
                <th>Ticket ID</th>
                <th>รายละเอียด</th>
                <th>หน่วยงาน</th>
                <th>สถานะ</th>
              </tr>
            </thead>

            <tbody>
              {trackingReports.map((item) => {
                const deptDisplay =
                  item.department ||
                  item.ai_department ||
                  item.agency_name ||
                  item.agency ||
                  "ยังไม่ได้กำหนด";

                return (
                  <tr
                    key={item.id || item.ticket_id}
                    style={onSelectReport ? { cursor: "pointer" } : undefined}
                    onClick={() => onSelectReport && onSelectReport(item.ticket_id)}
                    title={onSelectReport ? "คลิกเพื่อดูรายละเอียดในตารางร้องเรียน" : ""}
                  >
                    <td>
                      <strong>{item.ticket_ref || item.ticket_id || "-"}</strong>
                    </td>

                    <td>{item.description || item.problem_type || "-"}</td>

                    <td>{deptDisplay}</td>

                    <td>
                      <span className="tracking-status">
                        {item.status === "resolved" || item.status === "ดำเนินการเสร็จสิ้น"
                          ? "🟢 เสร็จสิ้น"
                          : item.status === "in_progress" || item.status === "กำลังดำเนินการ"
                          ? "🔵 กำลังดำเนินการ"
                          : item.status === "cancelled" || item.status === "ยกเลิก"
                          ? "🔴 ยกเลิก"
                          : "🟡 รับเรื่องแล้ว"}
                      </span>
                    </td>
                  </tr>
                );
              })}

              {trackingReports.length === 0 && (
                <tr>
                  <td colSpan="4" className="tracking-empty">
                    {searchText.trim()
                      ? "ไม่พบรายการที่ค้นหา"
                      : "ยังไม่มีรายการร้องเรียน"}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
// จบหน้าติดตามสถานะ

export default TrackingPage;
