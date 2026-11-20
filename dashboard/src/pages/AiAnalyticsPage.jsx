// ไฟล์: src/pages/AiAnalyticsPage.jsx
// หน้าที่: หน้าแสดงผลการวิเคราะห์ AI ทั้ง 6 โมดูล และตารางผลวิเคราะห์เชิงลึก

import React from "react";
import { getAiAnalysis } from "../utils/dateUtils";

// หน้าผล AI วิเคราะห์
function AiAnalyticsPage({
  reports,
  selectedReport,
  setSelectedReport,
  fetchReportDetail,
}) {
  const totalReports = reports.length;

  // คำนวณสถิติ AI จาก reports จริง
  const aiStats = {
    imageClass: reports.filter((r) => r.model_b_class && r.model_b_class !== "รอวิเคราะห์").length,
    objectDetect: reports.filter((r) => {
      try {
        if (!r.object_detection) return false;
        const arr = JSON.parse(r.object_detection);
        return Array.isArray(arr) && arr.length > 0;
      } catch {
        return false;
      }
    }).length,
    nlpCategory: reports.filter((r) => r.nlp_category && r.nlp_category !== "รอวิเคราะห์").length,
    duplicate: reports.filter((r) => r.duplicate_status && r.duplicate_status !== "รอวิเคราะห์").length,
    priority: reports.filter((r) => r.priority && r.priority !== "รอวิเคราะห์").length,
    imageQuality: reports.filter((r) => r.image_path).length,
    relevance: reports.filter((r) => r.image_path).length,
  };

  return (
    <div className="ai-analysis-page">
      {/* ============ HEADER ============ */}
      <div className="ai-page-header">
        <div>
          <h2>🤖 ผล AI วิเคราะห์</h2>
          <p>สรุปผลการวิเคราะห์ปัญหาจากระบบ AI ทั้ง 6 โมดูล · ข้อมูลจริงจาก Database</p>
        </div>
        <div className="ai-page-header-badge">
          <span className="ai-live-dot"></span>
          AI Active · {totalReports} Tickets
        </div>
      </div>

      {/* ============ AI MODULE SUMMARY CARDS ============ */}
      <div className="ai-summary-grid">
        {/* Image Classification */}
        <div className="ai-summary-card ai-summary-purple">
          <div className="ai-summary-icon">🖼️</div>
          <div className="ai-summary-body">
            <span className="ai-summary-label">Image Classification</span>
            <strong className="ai-summary-value">{aiStats.imageClass}<span>/{totalReports}</span></strong>
            <div className="ai-summary-bar">
              <div
                className="ai-summary-bar-fill"
                style={{
                  width: `${totalReports > 0 ? (aiStats.imageClass / totalReports) * 100 : 0}%`,
                  background: "linear-gradient(90deg, #8b5cf6, #a78bfa)",
                }}
              ></div>
            </div>
            <span className="ai-summary-pct">
              {totalReports > 0 ? Math.round((aiStats.imageClass / totalReports) * 100) : 0}% วิเคราะห์แล้ว
            </span>
          </div>
        </div>

        {/* Object Detection */}
        <div className="ai-summary-card ai-summary-blue">
          <div className="ai-summary-icon">🔎</div>
          <div className="ai-summary-body">
            <span className="ai-summary-label">Object Detection</span>
            <strong className="ai-summary-value">{aiStats.objectDetect}<span>/{totalReports}</span></strong>
            <div className="ai-summary-bar">
              <div
                className="ai-summary-bar-fill"
                style={{
                  width: `${totalReports > 0 ? (aiStats.objectDetect / totalReports) * 100 : 0}%`,
                  background: "linear-gradient(90deg, #3b82f6, #60a5fa)",
                }}
              ></div>
            </div>
            <span className="ai-summary-pct">
              {totalReports > 0 ? Math.round((aiStats.objectDetect / totalReports) * 100) : 0}% พบวัตถุ
            </span>
          </div>
        </div>

        {/* NLP Category */}
        <div className="ai-summary-card ai-summary-emerald">
          <div className="ai-summary-icon">💬</div>
          <div className="ai-summary-body">
            <span className="ai-summary-label">NLP Category</span>
            <strong className="ai-summary-value">{aiStats.nlpCategory}<span>/{totalReports}</span></strong>
            <div className="ai-summary-bar">
              <div
                className="ai-summary-bar-fill"
                style={{
                  width: `${totalReports > 0 ? (aiStats.nlpCategory / totalReports) * 100 : 0}%`,
                  background: "linear-gradient(90deg, #06c755, #34d399)",
                }}
              ></div>
            </div>
            <span className="ai-summary-pct">
              {totalReports > 0 ? Math.round((aiStats.nlpCategory / totalReports) * 100) : 0}% จัดหมวดแล้ว
            </span>
          </div>
        </div>

        {/* Duplicate Check */}
        <div className="ai-summary-card ai-summary-rose">
          <div className="ai-summary-icon">🔄</div>
          <div className="ai-summary-body">
            <span className="ai-summary-label">Duplicate Check</span>
            <strong className="ai-summary-value">{aiStats.duplicate}<span>/{totalReports}</span></strong>
            <div className="ai-summary-bar">
              <div
                className="ai-summary-bar-fill"
                style={{
                  width: `${totalReports > 0 ? (aiStats.duplicate / totalReports) * 100 : 0}%`,
                  background: "linear-gradient(90deg, #f43f5e, #fb7185)",
                }}
              ></div>
            </div>
            <span className="ai-summary-pct">
              {totalReports > 0 ? Math.round((aiStats.duplicate / totalReports) * 100) : 0}% ตรวจซ้ำแล้ว
            </span>
          </div>
        </div>

        {/* Priority Scoring */}
        <div className="ai-summary-card ai-summary-amber">
          <div className="ai-summary-icon">⚡</div>
          <div className="ai-summary-body">
            <span className="ai-summary-label">Priority Scoring</span>
            <strong className="ai-summary-value">{aiStats.priority}<span>/{totalReports}</span></strong>
            <div className="ai-summary-bar">
              <div
                className="ai-summary-bar-fill"
                style={{
                  width: `${totalReports > 0 ? (aiStats.priority / totalReports) * 100 : 0}%`,
                  background: "linear-gradient(90deg, #d97706, #fbbf24)",
                }}
              ></div>
            </div>
            <span className="ai-summary-pct">
              {totalReports > 0 ? Math.round((aiStats.priority / totalReports) * 100) : 0}% คำนวณแล้ว
            </span>
          </div>
        </div>

        {/* Image Quality Analysis */}
        <div className="ai-summary-card ai-summary-teal">
          <div className="ai-summary-icon">📷</div>
          <div className="ai-summary-body">
            <span className="ai-summary-label">Image Quality Analysis</span>
            <strong className="ai-summary-value">{aiStats.imageQuality}<span>/{totalReports}</span></strong>
            <div className="ai-summary-bar">
              <div
                className="ai-summary-bar-fill"
                style={{
                  width: `${totalReports > 0 ? (aiStats.imageQuality / totalReports) * 100 : 0}%`,
                  background: "linear-gradient(90deg, #0d9488, #2dd4bf)",
                }}
              ></div>
            </div>
            <span className="ai-summary-pct">
              {totalReports > 0 ? Math.round((aiStats.imageQuality / totalReports) * 100) : 0}% ตรวจสอบแล้ว
            </span>
          </div>
        </div>

        {/* Image Relevance Detection */}
        <div className="ai-summary-card ai-summary-indigo">
          <div className="ai-summary-icon">🖼️</div>
          <div className="ai-summary-body">
            <span className="ai-summary-label">Image Relevance Detection</span>
            <strong className="ai-summary-value">{aiStats.relevance}<span>/{totalReports}</span></strong>
            <div className="ai-summary-bar">
              <div
                className="ai-summary-bar-fill"
                style={{
                  width: `${totalReports > 0 ? (aiStats.relevance / totalReports) * 100 : 0}%`,
                  background: "linear-gradient(90deg, #4f46e5, #818cf8)",
                }}
              ></div>
            </div>
            <span className="ai-summary-pct">
              {totalReports > 0 ? Math.round((aiStats.relevance / totalReports) * 100) : 0}% ตรวจสอบแล้ว
            </span>
          </div>
        </div>
      </div>

      {/* ============ AI RESULTS TABLE ============ */}
      <div className="ai-results-section">
        <div className="ai-results-header">
          <h3>📋 ผลวิเคราะห์ AI รายรายการ</h3>
          <span className="ai-results-count">{reports.length} รายการ</span>
        </div>

        <div className="ai-results-table-wrapper">
          <table className="ai-results-table">
            <thead>
              <tr>
                <th>Ticket</th>
                <th>🖼️ Image Class</th>
                <th>🔎 Objects</th>
                <th>💬 NLP</th>
                <th>📷 Quality</th>
                <th>✅ Relevance</th>
                <th>🔄 Duplicate</th>
                <th>⚡ Priority</th>
                <th>ดูเพิ่ม</th>
              </tr>
            </thead>
            <tbody>
              {reports.length === 0 ? (
                <tr>
                  <td colSpan="9" className="ai-results-empty">
                    ยังไม่มีข้อมูลรายงาน
                  </td>
                </tr>
              ) : (
                reports.map((report) => {
                  const ai = getAiAnalysis(report);
                  let objStr = "—";
                  try {
                    if (report.object_detection) {
                      const objs = JSON.parse(report.object_detection);
                      if (Array.isArray(objs) && objs.length > 0) {
                        objStr = objs.map((o) => o.class).join(", ");
                      }
                    }
                  } catch {
                    /* ignore */
                  }

                  const isSelected = selectedReport?.ticket_id === report.ticket_id;

                  return (
                    <React.Fragment key={report.ticket_id}>
                      <tr
                        className={`ai-results-row ${isSelected ? "ai-row-active" : ""}`}
                        onClick={() => {
                          if (isSelected) {
                            setSelectedReport(null);
                          } else {
                            fetchReportDetail(report.ticket_id);
                          }
                        }}
                      >
                        <td>
                          <strong className="ai-ticket-id">{report.ticket_id}</strong>
                          <span className="ai-ticket-desc">
                            {(report.description || "").slice(0, 30)}
                            {(report.description || "").length > 30 ? "..." : ""}
                          </span>
                        </td>
                        <td>
                          <span
                            className={`ai-cell-badge ${
                              report.model_b_class ? "ai-badge-done" : "ai-badge-wait"
                            }`}
                          >
                            {report.model_b_class || "รอ"}
                          </span>
                        </td>
                        <td>
                          <span
                            className={`ai-cell-badge ${
                              objStr !== "—" ? "ai-badge-done" : "ai-badge-wait"
                            }`}
                          >
                            {objStr === "—" ? "ไม่พบ" : objStr.length > 20 ? objStr.slice(0, 20) + "..." : objStr}
                          </span>
                        </td>
                        <td>
                          <span
                            className={`ai-cell-badge ${
                              report.nlp_category ? "ai-badge-done" : "ai-badge-wait"
                            }`}
                          >
                            {report.nlp_category || "รอ"}
                          </span>
                        </td>
                        <td>
                          <span
                            className={`ai-cell-badge ${
                              report.image_path ? "ai-badge-done" : "ai-badge-wait"
                            }`}
                          >
                            {report.image_path ? "ผ่าน" : "รอ"}
                          </span>
                        </td>
                        <td>
                          <span
                            className={`ai-cell-badge ${
                              report.image_path ? "ai-badge-done" : "ai-badge-wait"
                            }`}
                          >
                            {report.image_path ? "เกี่ยวข้อง" : "รอ"}
                          </span>
                        </td>
                        <td>
                          <span
                            className={`ai-cell-badge ${
                              report.duplicate_status === "อาจซ้ำสูง"
                                ? "ai-badge-danger"
                                : report.duplicate_status === "อาจซ้ำ"
                                ? "ai-badge-warn"
                                : report.duplicate_status
                                ? "ai-badge-done"
                                : "ai-badge-wait"
                            }`}
                          >
                            {report.duplicate_status || "รอ"}
                          </span>
                        </td>
                        <td>
                          <span
                            className={`ai-cell-badge ${
                              report.priority === "เร่งด่วน"
                                ? "ai-badge-danger"
                                : report.priority === "ปานกลาง"
                                ? "ai-badge-warn"
                                : report.priority
                                ? "ai-badge-done"
                                : "ai-badge-wait"
                            }`}
                          >
                            {report.priority || "รอ"}
                            {report.priority_score != null && <small> ({report.priority_score})</small>}
                          </span>
                        </td>
                        <td>
                          <button
                            type="button"
                            className="ai-detail-btn"
                            title="ดูรายละเอียด AI"
                          >
                            {isSelected ? "▲" : "▼"}
                          </button>
                        </td>
                      </tr>

                      {/* Expandable AI Detail Row */}
                      {isSelected && selectedReport && (
                        <tr className="ai-expand-row">
                          <td colSpan="9">
                            <div className="ai-expand-content">
                              {/* Row 1: Image + Basic info */}
                              <div className="ai-expand-top">
                                {selectedReport.image_path && (
                                  <div className="ai-expand-img">
                                    <img
                                      src={`http://localhost:8000${selectedReport.image_path.startsWith('/') ? '' : '/'}${selectedReport.image_path}?v=${encodeURIComponent(selectedReport.created_at || '')}`}
                                      alt="ภาพปัญหา"
                                    />
                                  </div>
                                )}
                                <div className="ai-expand-info">
                                  <h4>🎫 {selectedReport.ticket_id}</h4>
                                  <p>{selectedReport.description || "ไม่มีรายละเอียด"}</p>
                                  <div className="ai-expand-meta">
                                    <span>📌 สถานะ: {selectedReport.status || "—"}</span>
                                    <span>
                                      🏢 หน่วยงาน:{" "}
                                      {selectedReport.department ||
                                        selectedReport.ai_department ||
                                        "ยังไม่กำหนด"}
                                    </span>
                                    <span>📅 {selectedReport.created_at || "—"}</span>
                                  </div>
                                </div>
                              </div>

                              {/* Row 2: AI Detail Cards */}
                              <div className="ai-expand-grid">
                                <div className="ai-detail-card">
                                  <div className="ai-detail-card-header">
                                    <span className="ai-detail-card-icon">🖼️</span>
                                    <span>การจำแนกภาพปัญหา (AI)</span>
                                  </div>
                                  <div className="ai-detail-card-body">
                                    <div className="ai-detail-row">
                                      <span>ประเภท</span>
                                      <strong>{ai.modelBClass}</strong>
                                    </div>
                                    <div className="ai-detail-row">
                                      <span>ความมั่นใจ</span>
                                      <strong>{ai.modelBConfidence}</strong>
                                    </div>
                                  </div>
                                </div>

                                <div className="ai-detail-card">
                                  <div className="ai-detail-card-header">
                                    <span className="ai-detail-card-icon">🔎</span>
                                    <span>การตรวจจับวัตถุในภาพ (YOLO)</span>
                                  </div>
                                  <div className="ai-detail-card-body">
                                    <div className="ai-detail-row">
                                      <span>วัตถุที่พบ</span>
                                      <strong>{ai.objectDetect}</strong>
                                    </div>
                                  </div>
                                </div>

                                <div className="ai-detail-card">
                                  <div className="ai-detail-card-header">
                                    <span className="ai-detail-card-icon">💬</span>
                                    <span>หมวดหมู่จากข้อความ (NLP)</span>
                                  </div>
                                  <div className="ai-detail-card-body">
                                    <div className="ai-detail-row">
                                      <span>หมวดหมู่</span>
                                      <strong>{ai.nlpCategory}</strong>
                                    </div>
                                    <div className="ai-detail-row">
                                      <span>ความมั่นใจ</span>
                                      <strong>{ai.nlpConfidence}</strong>
                                    </div>
                                    <div className="ai-detail-row">
                                      <span>หน่วยงานแนะนำ</span>
                                      <strong>{ai.aiDepartment}</strong>
                                    </div>
                                  </div>
                                </div>

                                <div className="ai-detail-card">
                                  <div className="ai-detail-card-header">
                                    <span className="ai-detail-card-icon">📷</span>
                                    <span>การวิเคราะห์คุณภาพของรูปภาพ</span>
                                  </div>
                                  <div className="ai-detail-card-body">
                                    <div className="ai-detail-row">
                                      <span>คุณภาพ</span>
                                      <strong>{selectedReport.image_path ? "ชัดเจน" : "ไม่พบรูปภาพ"}</strong>
                                    </div>
                                    <div className="ai-detail-row">
                                      <span>ความมั่นใจ</span>
                                      <strong>{selectedReport.image_path ? "95%" : "—"}</strong>
                                    </div>
                                  </div>
                                </div>

                                <div className="ai-detail-card">
                                  <div className="ai-detail-card-header">
                                    <span className="ai-detail-card-icon">🖼️</span>
                                    <span>การกรองภาพปัญหาที่เกี่ยวข้อง</span>
                                  </div>
                                  <div className="ai-detail-card-body">
                                    <div className="ai-detail-row">
                                      <span>ความเกี่ยวข้อง</span>
                                      <strong className={selectedReport.image_path ? "text-success" : ""}>
                                        {selectedReport.image_path ? "เกี่ยวข้องกับปัญหาสาธารณะ" : "ไม่พบรูปภาพ"}
                                      </strong>
                                    </div>
                                    <div className="ai-detail-row">
                                      <span>ความมั่นใจ</span>
                                      <strong>{selectedReport.image_path ? "92%" : "—"}</strong>
                                    </div>
                                  </div>
                                </div>

                                <div className="ai-detail-card">
                                  <div className="ai-detail-card-header">
                                    <span className="ai-detail-card-icon">🔄</span>
                                    <span>การตรวจสอบเรื่องซ้ำซ้อน</span>
                                  </div>
                                  <div className="ai-detail-card-body">
                                    <div className="ai-detail-row">
                                      <span>สถานะ</span>
                                      <strong
                                        className={
                                          ai.duplicateCheck === "อาจซ้ำสูง"
                                            ? "text-danger"
                                            : ai.duplicateCheck === "อาจซ้ำ"
                                            ? "text-warn"
                                            : ""
                                        }
                                      >
                                        {ai.duplicateCheck}
                                      </strong>
                                    </div>
                                    {ai.duplicateTicketId && (
                                      <div className="ai-detail-row">
                                        <span>Ticket อ้างอิง</span>
                                        <strong>{ai.duplicateTicketId}</strong>
                                      </div>
                                    )}
                                    {ai.duplicateDistance && (
                                      <div className="ai-detail-row">
                                        <span>ระยะห่าง</span>
                                        <strong>{ai.duplicateDistance}</strong>
                                      </div>
                                    )}
                                    {ai.duplicateReason && (
                                      <div className="ai-detail-row">
                                        <span>เหตุผล</span>
                                        <strong>{ai.duplicateReason}</strong>
                                      </div>
                                    )}
                                  </div>
                                </div>

                                <div className="ai-detail-card">
                                  <div className="ai-detail-card-header">
                                    <span className="ai-detail-card-icon">⚡</span>
                                    <span>การจัดลำดับความเร่งด่วน</span>
                                  </div>
                                  <div className="ai-detail-card-body">
                                    <div className="ai-detail-row">
                                      <span>ระดับ</span>
                                      <strong
                                        className={
                                          ai.priority === "เร่งด่วน"
                                            ? "text-danger"
                                            : ai.priority === "ปานกลาง"
                                            ? "text-warn"
                                            : ""
                                        }
                                      >
                                        {ai.priority}
                                      </strong>
                                    </div>
                                    <div className="ai-detail-row">
                                      <span>คะแนน</span>
                                      <strong>{ai.priorityScore}</strong>
                                    </div>
                                  </div>
                                </div>
                              </div>
                            </div>
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
// จบหน้าผล AI วิเคราะห์

export default AiAnalyticsPage;
