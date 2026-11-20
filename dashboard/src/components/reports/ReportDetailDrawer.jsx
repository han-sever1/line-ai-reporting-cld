// ไฟล์: src/components/reports/ReportDetailDrawer.jsx
// หน้าที่: แผงแสดงรายละเอียดเรื่องร้องเรียนด้านขวา ผลวิเคราะห์ AI เปลี่ยนสถานะ/หน่วยงาน และแผนที่พิกัด

import React, { useState, useEffect } from "react";
import {
  formatFullThaiDateTime,
  getRelativeTimeThai,
  getAiAnalysis,
} from "../../utils/dateUtils";

// แผงรายละเอียดตั๋ว
function ReportDetailDrawer({
  selectedReport,
  updateAssignment,
  handleAcceptReport,
  updateStatus,
  fetchReportDetail,
}) {
  const [selectedStatus, setSelectedStatus] = useState("");
  const [selectedReason, setSelectedReason] = useState("");
  const [isCustomReason, setIsCustomReason] = useState(false);
  const [customReasonText, setCustomReasonText] = useState("");

  const waitFixPresetReasons = [
    "รองบประมาณ",
    "รออุปกรณ์/อะไหล่",
    "รอประสานหน่วยงานภายนอก",
  ];

  const inProgressPresetReasons = [
    "กำลังลงพื้นที่",
    "กำลังซ่อมแซม",
    "กำลังตรวจหน้างาน",
  ];

  useEffect(() => {
    if (selectedReport) {
      setSelectedStatus(selectedReport.status || "รับเรื่องแล้ว");
      const currentReason = selectedReport.status_reason || "";
      setSelectedReason(currentReason);

      const isPreset =
        waitFixPresetReasons.includes(currentReason) ||
        inProgressPresetReasons.includes(currentReason);

      if (currentReason && !isPreset) {
        setIsCustomReason(true);
        setCustomReasonText(currentReason);
      } else {
        setIsCustomReason(false);
        setCustomReasonText("");
      }
    }
  }, [selectedReport]);

  const handleStatusChange = (newStatus) => {
    setSelectedStatus(newStatus);
    if (newStatus !== "รอแก้ไข" && newStatus !== "กำลังดำเนินการ") {
      updateStatus(selectedReport.ticket_id, newStatus, null);
    } else {
      if (newStatus === "รอแก้ไข") {
        setSelectedReason(waitFixPresetReasons[0]);
        setIsCustomReason(false);
      } else if (newStatus === "กำลังดำเนินการ") {
        setSelectedReason(inProgressPresetReasons[0]);
        setIsCustomReason(false);
      }
    }
  };

  const handleSaveStatusWithReason = () => {
    const finalReason = isCustomReason ? customReasonText.trim() : selectedReason;
    updateStatus(selectedReport.ticket_id, selectedStatus, finalReason || null);
  };
  if (!selectedReport) {
    return (
      <div className="detail-section">
        <div className="detail-empty">
          <span className="detail-empty-icon">📄</span>
          <p>เลือกรายการจากตารางเพื่อดูรายละเอียด</p>
        </div>
      </div>
    );
  }

  const ai = getAiAnalysis(selectedReport);

  return (
    <div className="detail-section">
      <div className="detail-card">
        {/* หัวข้อรายละเอียด */}
        <div className="detail-header">
          <span className="detail-ai-badge">🤖 ผล AI วิเคราะห์ LINE</span>
          <span className="detail-ticket-id">#{selectedReport.ticket_id}</span>
        </div>

        {/* แสดงรูปภาพปัญหา */}
        {selectedReport.image_path && (
          <img
            src={`http://localhost:8000${selectedReport.image_path.startsWith('/') ? '' : '/'}${selectedReport.image_path}?v=${encodeURIComponent(selectedReport.created_at || '')}`}
            alt="รูปภาพปัญหา"
            className="detail-image"
          />
        )}

        {/* กล่องแสดงวันที่และเวลาที่แจ้งปัญหา */}
        <div className="detail-date-badge-box">
          <div className="detail-date-main">
            <span className="detail-date-icon">📅</span>
            <span className="detail-date-label">วันที่แจ้ง:</span>
            <strong className="detail-date-value">
              {formatFullThaiDateTime(selectedReport.created_at) || "ไม่ระบุวันเวลา"}
            </strong>
          </div>
          {getRelativeTimeThai(selectedReport.created_at) && (
            <div className="detail-date-relative">
              ({getRelativeTimeThai(selectedReport.created_at)})
            </div>
          )}
        </div>

        {/* ตารางผลวิเคราะห์ AI */}
        <div className="ai-analysis-grid">
          {/* AI Image Classification */}
          <div className="ai-row">
            <span className="ai-row-label">การจำแนกภาพปัญหา (AI)</span>
            <span className="ai-row-value text-green">{ai.imageClass}</span>
          </div>

          <div className="ai-row">
            <span className="ai-row-label">ความมั่นใจการจำแนกภาพ</span>
            <span className="ai-row-value text-blue">{ai.modelBConfidence}</span>
          </div>

          <div className="ai-row">
            <span className="ai-row-label">ความน่าจะเป็น</span>
            <span className="ai-row-value text-blue">{ai.modelBProbability}</span>
          </div>

          {/* NLP Category */}
          <div className="ai-row">
            <span className="ai-row-label">หมวดหมู่จากข้อความ (NLP)</span>
            <span className="ai-row-value text-green">{ai.nlpCategory}</span>
          </div>

          <div className="ai-row">
            <span className="ai-row-label">ความมั่นใจจากข้อความ</span>
            <span className="ai-row-value text-blue">{ai.nlpConfidence}</span>
          </div>

          {/* AI Department Assignment */}
          <div className="ai-row">
            <span className="ai-row-label">หน่วยงานที่แนะนำ (AI)</span>
            <span className="ai-row-value text-green">{ai.aiDepartment}</span>
          </div>

          {/* Object Detection */}
          <div className="ai-row">
            <span className="ai-row-label">การตรวจจับวัตถุ (YOLO)</span>
            <span className="ai-row-value text-blue">{ai.objectDetect}</span>
          </div>

          {/* Image Quality */}
          <div className="ai-row">
            <span className="ai-row-label">คุณภาพของรูปภาพ</span>
            <span className="ai-row-value text-orange">{ai.imageQuality}</span>
          </div>

          {/* Duplicate Detection */}
          <div className="ai-row">
            <span className="ai-row-label">การตรวจสอบเรื่องซ้ำซ้อน</span>
            <span
              className={`ai-row-value ${
                ai.duplicateCheck === "อาจซ้ำสูง"
                  ? "duplicate-danger"
                  : ai.duplicateCheck === "อาจซ้ำ"
                  ? "duplicate-warning"
                  : ai.duplicateCheck === "ไม่ซ้ำ" || ai.duplicateCheck === "ไม่พบความเสี่ยงซ้ำ"
                  ? "duplicate-success"
                  : ""
              }`}
            >
              {ai.duplicateCheck}
            </span>
          </div>

          {ai.duplicateTicketId && (
            <div className="ai-row">
              <span className="ai-row-label">Ticket ที่อาจซ้ำ</span>
              <button
                type="button"
                className="ai-row-value duplicate-ticket-link"
                onClick={() => fetchReportDetail(ai.duplicateTicketId)}
              >
                {ai.duplicateTicketId}
              </button>
            </div>
          )}

          {ai.duplicateDistance && (
            <div className="ai-row">
              <span className="ai-row-label">ระยะห่าง</span>
              <span className="ai-row-value">{ai.duplicateDistance}</span>
            </div>
          )}

          {ai.duplicateReason && (
            <div className="ai-row">
              <span className="ai-row-label">เหตุผลการตรวจสอบ</span>
              <span className="ai-row-value">{ai.duplicateReason}</span>
            </div>
          )}

          {/* Priority */}
          <div className="ai-row">
            <span className="ai-row-label">ระดับความเร่งด่วน</span>
            <span className="ai-row-value">{selectedReport?.priority || "รอวิเคราะห์"}</span>
          </div>

          <div className="ai-row">
            <span className="ai-row-label">คะแนนความเร่งด่วน</span>
            <span className="ai-row-value text-red">
              {selectedReport?.priority_score != null ? `${selectedReport.priority_score}/100` : "รอวิเคราะห์"}
            </span>
          </div>
        </div>

        {/* เส้นคั่น */}
        <hr className="detail-divider" />

        {/* Dropdown เลือกประเภทปัญหา */}
        <div className="detail-field">
          <label>ประเภทปัญหา</label>
          <select
            value={selectedReport.category || ""}
            onChange={(e) =>
              updateAssignment(
                selectedReport.ticket_id,
                e.target.value,
                selectedReport.department || "เจ้าหน้าที่ระบบ"
              )
            }
          >
            <option value="">เลือกประเภทปัญหา</option>
            <option value="ถนนชำรุด">ถนนชำรุด</option>
            <option value="น้ำท่วม">น้ำท่วม</option>
            <option value="ขยะ">ขยะ</option>
            <option value="กิ่งไม้/ต้นไม้">กิ่งไม้/ต้นไม้</option>
            <option value="ไฟสาธารณะ">ไฟสาธารณะ</option>
            <option value="อื่นๆ">อื่นๆ</option>
          </select>
        </div>

        {/* Dropdown เลือกหน่วยงานผู้รับผิดชอบ */}
        <div className="detail-field">
          <label>หน่วยงานผู้รับผิดชอบ</label>
          <select
            value={selectedReport.department || ""}
            onChange={(e) =>
              updateAssignment(
                selectedReport.ticket_id,
                selectedReport.category || "อื่นๆ",
                e.target.value
              )
            }
          >
            <option value="">เลือกหน่วยงาน</option>
            <option value="กองช่าง">กองช่าง</option>
            <option value="งานป้องกันและบรรเทาสาธารณภัย">งานป้องกันและบรรเทาสาธารณภัย</option>
            <option value="งานสาธารณสุขและสิ่งแวดล้อม">งานสาธารณสุขและสิ่งแวดล้อม</option>
            <option value="งานไฟฟ้า">งานไฟฟ้า</option>
            <option value="เจ้าหน้าที่ระบบ">เจ้าหน้าที่ระบบ</option>
          </select>
        </div>

        {/* ข้อมูลการรับเรื่องของเจ้าหน้าที่ */}
        {selectedReport.accepted_by ? (
          <div className="accepted-info-card">
            <div className="accepted-info-title">
              <span>✅ ยืนยันรับเรื่องเรียบร้อยแล้ว</span>
            </div>
            <div className="accepted-info-details">
              <div>👤 <strong>ผู้รับเรื่อง:</strong> {selectedReport.accepted_by}</div>
              <div>🏢 <strong>หน่วยงาน:</strong> {selectedReport.department || selectedReport.ai_department || "ยังไม่ได้กำหนด"}</div>
              <div>🕐 <strong>วันที่รับเรื่อง:</strong> {selectedReport.accepted_at || "-"}</div>
            </div>
          </div>
        ) : (
          <div className="waiting-line-accept-card">
            <div className="waiting-line-header">
              <span className="waiting-pulse-dot"></span>
              <span>📲 รอหน่วยงานกดยืนยันรับเรื่องผ่าน LINE</span>
            </div>
            <p className="waiting-line-desc">
              ส่งการ์ดไปที่ <strong>{selectedReport.department || selectedReport.ai_department || "หน่วยงาน"}</strong> แล้ว เมื่อเจ้าหน้าที่กดรับเรื่องใน LINE ข้อมูลจะเข้าตรงนี้อัตโนมัติ ไม่ต้องให้เจ้าหน้าที่ Dashboard กดอีกทีครับ
            </p>
            <button
              type="button"
              className="btn-manual-accept-link"
              onClick={() => handleAcceptReport(selectedReport.ticket_id)}
              title="กดรับเรื่องแทนในกรณีจำเป็น"
            >
              (หรือคลิกที่นี่ หากต้องการกดยืนยันรับเรื่องแทนเจ้าหน้าที่)
            </button>
          </div>
        )}

        {/* Dropdown เปลี่ยนสถานะ */}
        <div className="detail-field">
          <label>เปลี่ยนสถานะ</label>
          <select
            value={selectedStatus}
            onChange={(e) => handleStatusChange(e.target.value)}
          >
            <option value="รับเรื่องแล้ว">รับเรื่องแล้ว</option>
            <option value="รอแก้ไข">⏳ รอแก้ไข</option>
            <option value="กำลังดำเนินการ">⚙️ กำลังดำเนินการ</option>
            <option value="ดำเนินการเสร็จสิ้น">🎉 ดำเนินการเสร็จสิ้น</option>
            <option value="ยกเลิก">❌ ยกเลิก</option>
          </select>
        </div>

        {/* ตัวเลือกเหตุผลเมื่อเป็น 'รอแก้ไข' หรือ 'กำลังดำเนินการ' */}
        {(selectedStatus === "รอแก้ไข" || selectedStatus === "กำลังดำเนินการ") && (
          <div
            style={{
              background: selectedStatus === "รอแก้ไข" ? "#FFFBEB" : "#EFF6FF",
              border: `1px solid ${selectedStatus === "รอแก้ไข" ? "#FCD34D" : "#BFDBFE"}`,
              borderRadius: "8px",
              padding: "12px",
              marginBottom: "14px",
            }}
          >
            <label
              style={{
                display: "block",
                fontSize: "12px",
                fontWeight: "bold",
                color: selectedStatus === "รอแก้ไข" ? "#B45309" : "#1D4ED8",
                marginBottom: "6px",
              }}
            >
              {selectedStatus === "รอแก้ไข"
                ? "⏳ ระบุสาเหตุที่รอแก้ไข:"
                : "⚙️ ระบุความคืบหน้าการทำงาน:"}
            </label>

            <select
              value={isCustomReason ? "custom" : selectedReason}
              onChange={(e) => {
                if (e.target.value === "custom") {
                  setIsCustomReason(true);
                } else {
                  setIsCustomReason(false);
                  setSelectedReason(e.target.value);
                }
              }}
              style={{
                width: "100%",
                padding: "8px 10px",
                fontSize: "13px",
                borderRadius: "6px",
                border: "1px solid #CBD5E1",
                marginBottom: isCustomReason ? "8px" : "10px",
                background: "#FFFFFF",
              }}
            >
              {(selectedStatus === "รอแก้ไข" ? waitFixPresetReasons : inProgressPresetReasons).map(
                (opt) => (
                  <option key={opt} value={opt}>
                    {opt}
                  </option>
                )
              )}
              <option value="custom">✍️ พิมพ์เหตุผลอื่นเอง...</option>
            </select>

            {isCustomReason && (
              <input
                type="text"
                placeholder={
                  selectedStatus === "รอแก้ไข"
                    ? "เช่น รองบประมาณจัดซื้อท่อ..."
                    : "เช่น เจ้าหน้าที่กำลังเดินทางเข้าพื้นที่..."
                }
                value={customReasonText}
                onChange={(e) => setCustomReasonText(e.target.value)}
                style={{
                  width: "100%",
                  padding: "8px 10px",
                  fontSize: "13px",
                  borderRadius: "6px",
                  border: "1px solid #CBD5E1",
                  marginBottom: "10px",
                  background: "#FFFFFF",
                  boxSizing: "border-box",
                }}
              />
            )}

            <button
              type="button"
              onClick={handleSaveStatusWithReason}
              style={{
                width: "100%",
                padding: "8px 12px",
                fontSize: "13px",
                fontWeight: "bold",
                color: "#FFFFFF",
                backgroundColor: selectedStatus === "รอแก้ไข" ? "#D97706" : "#2563EB",
                border: "none",
                borderRadius: "6px",
                cursor: "pointer",
                transition: "opacity 0.2s",
              }}
            >
              💾 บันทึกสถานะ ({selectedStatus})
            </button>
          </div>
        )}

        {/* เส้นคั่น */}
        <hr className="detail-divider" />

        {/* ข้อมูลรายละเอียดเพิ่มเติม */}
        <p className="detail-info">
          <strong>รายละเอียด: </strong>{selectedReport.description}
        </p>
        <p className="detail-info">
          <strong>สถานะ: </strong>{selectedReport.status}
        </p>
        {selectedReport.status === "รอแก้ไข" ? (
          <p className="detail-info">
            <strong>สาเหตุ: </strong>
            <span style={{ color: "#d97706", fontWeight: "bold" }}>
              {selectedReport.status_reason || "-"}
            </span>
          </p>
        ) : (selectedReport.status === "กำลังดำเนินการ" || selectedReport.status === "กำลังทำ") ? (
          <p className="detail-info">
            <strong>ความคืบหน้า: </strong>
            <span style={{ color: "#2563eb", fontWeight: "bold" }}>
              {selectedReport.status_reason || "-"}
            </span>
          </p>
        ) : selectedReport.status === "ยกเลิก" ? (
          <p className="detail-info">
            <strong>สาเหตุ: </strong>
            <span style={{ color: "#dc2626", fontWeight: "bold" }}>
              {selectedReport.status_reason || "-"}
            </span>
          </p>
        ) : (
          <p className="detail-info">
            <strong>สาเหตุ: </strong>
            <span style={{ color: "var(--text-secondary)" }}>-</span>
          </p>
        )}
        <p className="detail-info">
          <strong>อัปเดตล่าสุด: </strong>{selectedReport.updated_at}
        </p>

        {/* Google Maps */}
        <div className="detail-map">
          <iframe
            title="ตำแหน่งปัญหา"
            src={`https://www.google.com/maps?q=${selectedReport.latitude},${selectedReport.longitude}&output=embed`}
            width="100%"
            height="200"
            style={{ border: 0 }}
            allowFullScreen=""
            loading="lazy"
          ></iframe>
        </div>

        {/* ข้อมูลพิกัด GPS */}
        <p className="detail-coords">
          📍 {selectedReport.latitude}, {selectedReport.longitude}
        </p>

        {/* ลิงก์เปิด Google Maps ในแท็บใหม่ */}
        <a
          className="detail-map-link"
          href={`https://www.google.com/maps?q=${selectedReport.latitude},${selectedReport.longitude}`}
          target="_blank"
          rel="noreferrer"
        >
          🗺️ เปิดตำแหน่งใน Google Maps
        </a>
      </div>
    </div>
  );
}
// จบแผงรายละเอียดตั๋ว

export default ReportDetailDrawer;
