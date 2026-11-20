// ไฟล์: src/pages/MapPage.jsx
// หน้าที่: หน้าแผนที่ปัญหา แสดงพิกัด GPS บน Leaflet พร้อมการ์ดรายการปัญหา และปุ่มนำทาง Google Maps

import React from "react";
import ProblemMap from "../components/map/ProblemMap";

// หน้าแผนที่ปัญหา
function MapPage({
  mapFilteredReports,
  selectedReport,
  setSelectedReport,
  searchText,
  setSearchText,
  fetchReportDetail,
}) {
  return (
    <div className="map-page">
      {/* HEADER: หัวข้อ + ช่องค้นหา */}
      <div className="map-page-header">
        <div>
          <h2>🗺️ แผนที่ปัญหา</h2>
          <p>แสดงตำแหน่งปัญหาจากข้อมูลที่ประชาชนแจ้งเข้ามา</p>
        </div>

        <div className="map-search-box">
          <span>🔍</span>
          <input
            type="text"
            placeholder="ค้นหา Ticket หรือปัญหา..."
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
          />
        </div>
      </div>

      {/* MAIN MAP LAYOUT: ซ้าย = รายการปัญหา / ขวา = แผนที่ */}
      <div className="map-content">
        {/* LEFT PANEL: รายการ Ticket */}
        <div className="map-ticket-panel">
          <div className="map-ticket-header">
            <h3>📋 รายการปัญหา</h3>
            <span>{mapFilteredReports.length} รายการ</span>
          </div>

          <div className="map-ticket-list">
            {mapFilteredReports.length === 0 ? (
              <div className="map-empty">
                📭
                <p>
                  {searchText.trim() ? "ไม่พบข้อมูลที่ตรงกับคำค้นหา" : "ยังไม่มีข้อมูลปัญหา"}
                </p>
              </div>
            ) : (
              mapFilteredReports.map((item) => (
                <div
                  key={item.id || item.ticket_id}
                  className={`map-ticket-card ${
                    selectedReport?.ticket_id === item.ticket_id ? "selected" : ""
                  }`}
                  onClick={() => {
                    setSelectedReport(item);
                    if (item.ticket_id) {
                      fetchReportDetail(item.ticket_id);
                    }
                  }}
                >
                  <div className="map-ticket-top">
                    <strong>#{item.ticket_ref || item.ticket_id}</strong>
                    <span
                      className={`map-status ${
                        item.status === "ดำเนินการเสร็จสิ้น"
                          ? "map-status-done"
                          : item.status === "กำลังดำเนินการ"
                          ? "map-status-progress"
                          : item.status === "ยกเลิก"
                          ? "map-status-cancel"
                          : "map-status-pending"
                      }`}
                    >
                      {item.status || "รับเรื่องแล้ว"}
                    </span>
                  </div>

                  <p className="map-ticket-description">
                    {item.description || item.problem_type || "ไม่ระบุรายละเอียด"}
                  </p>

                  <div className="map-ticket-meta">
                    <span>
                      🏢{" "}
                      {item.agency_name ||
                        item.department ||
                        item.agency ||
                        "ยังไม่ได้กำหนด"}
                    </span>
                  </div>

                  <div className="map-ticket-location">
                    📍{" "}
                    {item.latitude && item.longitude
                      ? `${item.latitude}, ${item.longitude}`
                      : "ไม่มีพิกัด"}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* RIGHT PANEL: พื้นที่แผนที่ */}
        <div className="map-display">
          <div className="map-display-header">
            <div>
              <strong>📍 ตำแหน่งปัญหา</strong>
              <span>{mapFilteredReports.length} จุด</span>
            </div>

            <div className="map-header-legend">
              <span className="legend-badge legend-pending">
                <span className="legend-dot" style={{ backgroundColor: "#f59e0b" }}></span> รับเรื่องแล้ว
              </span>
              <span className="legend-badge legend-progress">
                <span className="legend-dot" style={{ backgroundColor: "#3b82f6" }}></span> กำลังดำเนินการ
              </span>
              <span className="legend-badge legend-done">
                <span className="legend-dot" style={{ backgroundColor: "#06c755" }}></span> ดำเนินการเสร็จสิ้น
              </span>
              <span className="legend-badge legend-cancel">
                <span className="legend-dot" style={{ backgroundColor: "#ef4444" }}></span> ยกเลิก
              </span>
            </div>
          </div>

          <div className="map-real-area" style={{ position: "relative" }}>
            <ProblemMap
              reports={mapFilteredReports}
              selectedReport={selectedReport}
              onSelectReport={(item) => setSelectedReport(item)}
            />

            {/* Overlay รายละเอียดเมื่อเลือก Ticket */}
            {selectedReport && (
              <div className="map-detail-overlay active">
                <button
                  type="button"
                  className="map-detail-close"
                  onClick={() => setSelectedReport(null)}
                >
                  ✕
                </button>

                <div className="map-detail-content">
                  {selectedReport.image_path ? (
                    <img
                      src={`http://localhost:8000${selectedReport.image_path.startsWith('/') ? '' : '/'}${selectedReport.image_path}?v=${encodeURIComponent(selectedReport.created_at || '')}`}
                      alt="ภาพปัญหา"
                      className="map-detail-img"
                    />
                  ) : (
                    <div className="map-detail-no-img">📷 ไม่มีรูปภาพ</div>
                  )}

                  <div className="map-detail-info">
                    <div className="map-detail-header">
                      <h3>#{selectedReport.ticket_ref || selectedReport.ticket_id}</h3>
                      <span
                        className={`map-status ${
                          selectedReport.status === "ดำเนินการเสร็จสิ้น"
                            ? "map-status-done"
                            : selectedReport.status === "กำลังดำเนินการ"
                            ? "map-status-progress"
                            : selectedReport.status === "ยกเลิก"
                            ? "map-status-cancel"
                            : "map-status-pending"
                        }`}
                      >
                        {selectedReport.status || "รับเรื่องแล้ว"}
                      </span>
                    </div>

                    <p className="map-detail-desc">
                      {selectedReport.description ||
                        selectedReport.problem_type ||
                        "ไม่ระบุรายละเอียด"}
                    </p>

                    <div className="map-detail-meta-list">
                      <span>
                        🏢 หน่วยงาน:{" "}
                        {selectedReport.agency_name ||
                          selectedReport.department ||
                          selectedReport.agency ||
                          "ยังไม่ได้กำหนด"}
                      </span>
                      <span>
                        📍 พิกัด GPS: {selectedReport.latitude}, {selectedReport.longitude}
                      </span>
                      <span>📅 วันที่: {selectedReport.created_at || "—"}</span>
                    </div>

                    {selectedReport.latitude && selectedReport.longitude && (
                      <a
                        href={`https://www.google.com/maps?q=${selectedReport.latitude},${selectedReport.longitude}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="map-btn-navigate"
                      >
                        🧭 เปิดนำทางผ่าน Google Maps
                      </a>
                    )}

                    {(selectedReport.model_b_class || selectedReport.nlp_category) && (
                      <div className="map-detail-ai">
                        <strong>🤖 AI วิเคราะห์เบื้องต้น</strong>
                        <div className="map-detail-ai-tags">
                          {selectedReport.model_b_class && (
                            <span>🖼️ {selectedReport.model_b_class}</span>
                          )}
                          {selectedReport.nlp_category && (
                            <span>💬 {selectedReport.nlp_category}</span>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
// จบหน้าแผนที่ปัญหา

export default MapPage;
