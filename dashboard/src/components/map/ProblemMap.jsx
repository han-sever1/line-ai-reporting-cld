// ไฟล์: src/components/map/ProblemMap.jsx
// หน้าที่: แสดงแผนที่ Leaflet และหมุดแสดงตำแหน่งพิกัดปัญหาตามสีสถานะ พร้อมพิกัดและปุ่มนำทาง Google Maps

import React, { useEffect } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { MapContainer, TileLayer, Marker, Popup, useMap } from "react-leaflet";

// ไอคอนหมุดแผนที่
const getMarkerIcon = (status) => {
  let color = "#f59e0b"; // ส้ม: รับเรื่องแล้ว
  if (status === "กำลังดำเนินการ") {
    color = "#3b82f6"; // ฟ้า: กำลังดำเนินการ
  } else if (status === "ดำเนินการเสร็จสิ้น" || status === "เสร็จสิ้น" || status === "แก้ไขแล้ว") {
    color = "#06c755"; // เขียว: ดำเนินการเสร็จสิ้น
  } else if (status === "ยกเลิก") {
    color = "#ef4444"; // แดง: ยกเลิก
  }

  const svgHtml = `
    <div style="position: relative; width: 34px; height: 44px; display: flex; align-items: center; justify-content: center; filter: drop-shadow(0 4px 8px rgba(0,0,0,0.35)); transition: transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);">
      <svg width="34" height="44" viewBox="0 0 34 44" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M17 0C7.611 0 0 7.611 0 17c0 12.5 15.3 26.2 16.1 26.9.5.4 1.3.4 1.8 0C18.7 43.2 34 29.5 34 17 34 7.611 26.389 0 17 0z" fill="${color}" stroke="#ffffff" stroke-width="2.5"/>
        <circle cx="17" cy="16" r="6.5" fill="#ffffff"/>
        <circle cx="17" cy="16" r="3.5" fill="${color}"/>
      </svg>
    </div>
  `;

  return L.divIcon({
    html: svgHtml,
    className: "custom-leaflet-marker",
    iconSize: [34, 44],
    iconAnchor: [17, 44],
    popupAnchor: [0, -42],
  });
};
// จบไอคอนหมุดแผนที่

// ตัวควบคุมมุมมองแผนที่
function MapController({ selectedReport, reports }) {
  const map = useMap();

  useEffect(() => {
    if (selectedReport && selectedReport.latitude && selectedReport.longitude) {
      const lat = Number(selectedReport.latitude);
      const lng = Number(selectedReport.longitude);
      if (!isNaN(lat) && !isNaN(lng)) {
        map.flyTo([lat, lng], 15, { duration: 1.0 });
      }
    } else if (reports && reports.length === 1) {
      const single = reports[0];
      if (single.latitude && single.longitude) {
        const lat = Number(single.latitude);
        const lng = Number(single.longitude);
        if (!isNaN(lat) && !isNaN(lng)) {
          map.flyTo([lat, lng], 13, { duration: 0.8 });
        }
      }
    }
  }, [selectedReport, reports, map]);

  return null;
}
// จบตัวควบคุมมุมมองแผนที่

// แผนที่ปัญหา
function ProblemMap({ reports, selectedReport, onSelectReport }) {
  return (
    <MapContainer
      center={[6.5421, 101.2803]}
      zoom={10}
      scrollWheelZoom={true}
      style={{
        width: "100%",
        height: "100%",
        minHeight: "500px"
      }}
    >
      <MapController selectedReport={selectedReport} reports={reports} />

      <TileLayer
        attribution='&copy; OpenStreetMap contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {reports.map((item) => {
        if (
          item.latitude === null ||
          item.longitude === null ||
          item.latitude === undefined ||
          item.longitude === undefined
        ) {
          return null;
        }

        const latitude = Number(item.latitude);
        const longitude = Number(item.longitude);

        if (Number.isNaN(latitude) || Number.isNaN(longitude)) {
          return null;
        }

        const googleMapUrl = `https://www.google.com/maps?q=${latitude},${longitude}`;

        return (
          <Marker
            key={item.id || item.ticket_id}
            position={[latitude, longitude]}
            icon={getMarkerIcon(item.status)}
            eventHandlers={{
              click: () => onSelectReport(item)
            }}
          >
            <Popup className="custom-leaflet-popup">
              <div className="custom-popup-content">
                {item.image_path ? (
                  <div className="custom-popup-img-wrapper">
                    <img 
                      src={`http://localhost:8000${item.image_path.startsWith('/') ? '' : '/'}${item.image_path}?v=${encodeURIComponent(item.created_at || '')}`} 
                      alt="ปัญหา" 
                      className="custom-popup-img" 
                    />
                  </div>
                ) : (
                  <div className="custom-popup-no-img">
                    📷
                  </div>
                )}
                
                <div className="custom-popup-body">
                  <div className="custom-popup-header">
                    <span className="custom-popup-ticket">#{item.ticket_ref || item.ticket_id || "-"}</span>
                    <span className={`custom-popup-status status-${(item.status || "รับเรื่องแล้ว").toLowerCase()}`}>
                      {item.status || "รับเรื่องแล้ว"}
                    </span>
                  </div>
                  
                  <p className="custom-popup-desc">
                    {item.description || item.problem_type || "ไม่ระบุรายละเอียด"}
                  </p>
                  
                  <div className="custom-popup-meta">
                    🏢 {item.agency_name || item.department || item.agency || "ยังไม่ได้กำหนด"}
                  </div>

                  <div className="custom-popup-meta" style={{ color: "#0284c7", fontWeight: "500" }}>
                    📍 พิกัด: {latitude.toFixed(6)}, {longitude.toFixed(6)}
                  </div>
                  
                  <div className="custom-popup-actions">
                    <a
                      href={googleMapUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="custom-popup-btn-nav"
                      title="เปิดนำทางผ่าน Google Maps"
                    >
                      🧭 นำทาง
                    </a>
                    <button
                      onClick={() => onSelectReport(item)}
                      className="custom-popup-btn"
                      style={{ flex: 1, marginTop: 0 }}
                    >
                      ดูรายละเอียด
                    </button>
                  </div>
                </div>
              </div>
            </Popup>
          </Marker>
        );
      })}
    </MapContainer>
  );
}
// จบแผนที่ปัญหา

export default ProblemMap;
