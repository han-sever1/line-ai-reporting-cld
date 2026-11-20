// ไฟล์: src/pages/ReportsPage.jsx
// หน้าที่: หน้ารายการปัญหา ตารางเรื่องร้องเรียน ตัวกรองสถานะ/เวลา/ระดับความเร่งด่วน และแผงรายละเอียด

import React from "react";
import ReportDetailDrawer from "../components/reports/ReportDetailDrawer";
import {
  formatShortThaiDate,
  getStatusDotClass,
  getStatusBarColor,
  getTabLabel,
  timeFilterOptions,
} from "../utils/dateUtils";

// ตัวเลือกระดับความเร่งด่วน
const priorityFilterOptions = [
  { value: "all", label: "ทั้งหมด", icon: "⚪", className: "" },
  { value: "เร่งด่วน", label: "เร่งด่วน", icon: "🔴", className: "item-urgent" },
  { value: "ปานกลาง", label: "ปานกลาง", icon: "🟡", className: "item-medium" },
  { value: "ปกติ", label: "ปกติ", icon: "🟢", className: "item-normal" },
];

// หน้ารายการปัญหา
function ReportsPage({
  filteredReports,
  reports,
  selectedReport,
  loading,
  error,
  statusFilter,
  setStatusFilter,
  tableTimeFilter,
  setTableTimeFilter,
  showTableTimeMenu,
  setShowTableTimeMenu,
  tableTimeRef,
  priorityFilter,
  setPriorityFilter,
  showPriorityMenu,
  setShowPriorityMenu,
  priorityRef,
  fetchReportDetail,
  deleteReport,
  updateAssignment,
  handleAcceptReport,
  updateStatus,
  activities,
  chartData,
  chartMax,
}) {
  const currentPriorityLabel =
    priorityFilterOptions.find((o) => o.value === priorityFilter)?.label || "ทั้งหมด";

  const getPriorityBtnClass = () => {
    if (priorityFilter === "เร่งด่วน") return "active-urgent";
    if (priorityFilter === "ปานกลาง") return "active-medium";
    if (priorityFilter === "ปกติ") return "active-normal";
    return "";
  };

  return (
    <>
      {/* ============ CONTENT GRID ============ */}
      <div className="content-grid">
        {/* ส่วนตารางรายการปัญหา */}
        <div className="table-section">
          <div className="table-header">
            <div className="table-header-left">
              <h2>รายการแจ้งปัญหาล่าสุด</h2>

              {/* ตัวกรองเวลาเฉพาะตาราง */}
              <div className="time-filter-dropdown-container" ref={tableTimeRef}>
                <button
                  type="button"
                  className={`table-time-dropdown-btn ${tableTimeFilter !== "all" ? "active" : ""}`}
                  onClick={() => setShowTableTimeMenu((prev) => !prev)}
                  title="ตัวกรองเวลาเฉพาะตาราง"
                >
                  <span>🕒 {timeFilterOptions.find((o) => o.value === tableTimeFilter)?.label || "ทั้งหมด"}</span>
                  <span className="dropdown-arrow">▼</span>
                </button>
                {showTableTimeMenu && (
                  <div className="time-filter-dropdown-menu">
                    <div className="time-filter-menu-header">กรองตารางตามเวลา</div>
                    {timeFilterOptions.map((opt) => (
                      <button
                        key={opt.value}
                        type="button"
                        className={`time-filter-menu-item ${tableTimeFilter === opt.value ? "active" : ""}`}
                        onClick={() => {
                          setTableTimeFilter(opt.value);
                          setShowTableTimeMenu(false);
                        }}
                      >
                        <span className="option-icon">{opt.icon}</span>
                        <span className="option-label">{opt.label}</span>
                        {tableTimeFilter === opt.value && <span className="option-check">✓</span>}
                      </button>
                    ))}
                  </div>
                )}
              </div>

              {/* ตัวกรองระดับความเร่งด่วน */}
              <div className="priority-filter-dropdown-container" ref={priorityRef}>
                <button
                  type="button"
                  className={`table-priority-dropdown-btn ${getPriorityBtnClass()}`}
                  onClick={() => setShowPriorityMenu((prev) => !prev)}
                  title="กรองตามระดับความเร่งด่วน"
                >
                  <span>
                    {priorityFilter === "เร่งด่วน" && "🔴 "}
                    {priorityFilter === "ปานกลาง" && "🟡 "}
                    {priorityFilter === "ปกติ" && "🟢 "}
                    {priorityFilter === "all" && "⚡ "}
                    ระดับ: {currentPriorityLabel}
                  </span>
                  <span className="dropdown-arrow">▼</span>
                </button>
                {showPriorityMenu && (
                  <div className="priority-filter-dropdown-menu">
                    <div className="priority-filter-menu-header">กรองตามระดับความเร่งด่วน</div>
                    {priorityFilterOptions.map((opt) => (
                      <button
                        key={opt.value}
                        type="button"
                        className={`priority-filter-menu-item ${opt.className} ${
                          priorityFilter === opt.value ? "active" : ""
                        }`}
                        onClick={() => {
                          setPriorityFilter(opt.value);
                          setShowPriorityMenu(false);
                        }}
                      >
                        <span className="option-icon">{opt.icon}</span>
                        <span className="option-label">{opt.label}</span>
                        {priorityFilter === opt.value && <span className="option-check">✓</span>}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* ปุ่ม tabs สำหรับกรองสถานะ */}
            <div className="filter-tabs">
              {["ทั้งหมด", "รับเรื่องแล้ว", "รอแก้ไข", "กำลังดำเนินการ", "ดำเนินการเสร็จสิ้น", "ยกเลิก"].map((tab) => (
                <button
                  key={tab}
                  type="button"
                  className={`tab-btn ${statusFilter === tab ? "active" : ""}`}
                  onClick={() => setStatusFilter(tab)}
                >
                  {getTabLabel(tab)}
                </button>
              ))}
            </div>
          </div>

          {loading && <p className="loading-text">⏳ กำลังโหลดข้อมูล...</p>}
          {error && <p className="error-text">❌ Error: {error}</p>}

          {!loading && !error && (
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>TICKET ID</th>
                    <th>ปัญหา</th>
                    <th>ระดับ</th>
                    <th>สถานะ</th>
                    <th>AI SCORE</th>
                    <th aria-label="ลบรายการ"></th>
                  </tr>
                </thead>
                <tbody>
                  {filteredReports.length === 0 ? (
                    <tr>
                      <td colSpan="6" className="empty-row">
                        ไม่พบข้อมูลร้องเรียน
                      </td>
                    </tr>
                  ) : (
                    filteredReports.map((report) => {
                      const score = report.priority_score ?? 0;
                      const priority = {
                        label: report.priority || "ไม่ระบุ",
                        className:
                          report.priority === "เร่งด่วน"
                            ? "priority-urgent"
                            : report.priority === "ปานกลาง"
                            ? "priority-medium"
                            : "priority-normal",
                      };

                      return (
                        <tr
                          key={report.ticket_id}
                          className={selectedReport?.ticket_id === report.ticket_id ? "row-active" : ""}
                          onClick={() => fetchReportDetail(report.ticket_id)}
                        >
                          <td>
                            <div className="ticket-cell-wrapper">
                              <span className="ticket-link">#{report.ticket_id}</span>
                              <span className="ticket-date-sub">
                                {formatShortThaiDate(report.created_at)}
                              </span>
                            </div>
                          </td>
                          <td className="desc-cell">{report.description}</td>
                          <td>
                            <span className={`priority-badge ${priority.className}`}>
                              {priority.label}
                            </span>
                          </td>
                          <td>
                            <span className={`status-dot ${getStatusDotClass(report.status)}`}></span>
                            {report.status}
                            {report.status === "รอแก้ไข" && (
                              <div style={{ fontSize: "11px", color: "#d97706", marginTop: "3px", fontWeight: "500" }}>
                                📌 สาเหตุ: {report.status_reason || "-"}
                              </div>
                            )}
                            {(report.status === "กำลังดำเนินการ" || report.status === "กำลังทำ") && (
                              <div style={{ fontSize: "11px", color: "#2563eb", marginTop: "3px", fontWeight: "500" }}>
                                🚗 ความคืบหน้า: {report.status_reason || "-"}
                              </div>
                            )}
                            {report.status === "ยกเลิก" && report.status_reason && (
                              <div style={{ fontSize: "11px", color: "#dc2626", marginTop: "3px", fontWeight: "500" }}>
                                ❌ สาเหตุ: {report.status_reason}
                              </div>
                            )}
                            {report.status === "ดำเนินการเสร็จสิ้น" && report.status_reason && (
                              <div style={{ fontSize: "11px", color: "#059669", marginTop: "3px", fontWeight: "500" }}>
                                🎉 ผลการแก้ไข: {report.status_reason}
                              </div>
                            )}
                          </td>
                          <td>
                            <div className="ai-score-cell">
                              <span className="ai-score-num">{score}</span>
                              <div className="ai-score-bar">
                                <div
                                  className="ai-score-fill"
                                  style={{
                                    width: `${score}%`,
                                    backgroundColor: getStatusBarColor(report.status),
                                  }}
                                ></div>
                              </div>
                            </div>
                          </td>
                          <td className="action-cell">
                            <button
                              type="button"
                              className="delete-report-btn btn-delete"
                              title="ลบรายการนี้"
                              onClick={(e) => {
                                e.stopPropagation();
                                deleteReport(report.ticket_id);
                              }}
                            >
                              🗑️
                            </button>
                          </td>
                        </tr>
                      );
                    })
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* แผงรายละเอียดด้านขวา */}
        <ReportDetailDrawer
          selectedReport={selectedReport}
          handleAcceptReport={handleAcceptReport}
          updateStatus={updateStatus}
          updateAssignment={updateAssignment}
          activities={activities}
          chartData={chartData}
          chartMax={chartMax}
        />
      </div>
    </>
  );
}
// จบหน้ารายการปัญหา

export default ReportsPage;
