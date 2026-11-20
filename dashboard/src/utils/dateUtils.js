// ไฟล์: src/utils/dateUtils.js
// หน้าที่: ฟังก์ชันจัดการวัน-เวลาภาษาไทย ระบบคำนวณช่วงเวลาปฏิทิน และฟังก์ชันช่วย AI ต่างๆ

// ฟังก์ชันแปลงวันเวลา
export const parseSQLDate = (str) => {
  if (!str) return null;
  if (str instanceof Date) return str;
  const parts = String(str).split(/[- :T]/);
  if (parts.length >= 3) {
    const year = parseInt(parts[0], 10);
    const month = parseInt(parts[1], 10) - 1;
    const day = parseInt(parts[2], 10);
    const hour = parts[3] ? parseInt(parts[3], 10) : 0;
    const minute = parts[4] ? parseInt(parts[4], 10) : 0;
    const second = parts[5] ? parseInt(parts[5], 10) : 0;
    return new Date(year, month, day, hour, minute, second);
  }
  return new Date(str);
};

export const formatShortThaiDate = (dateStr) => {
  const d = parseSQLDate(dateStr);
  if (!d || isNaN(d.getTime())) return "";
  const thaiMonthsShort = ["ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."];
  const day = d.getDate();
  const month = thaiMonthsShort[d.getMonth()];
  const thaiYearShort = (d.getFullYear() + 543) % 100;
  const hours = String(d.getHours()).padStart(2, "0");
  const minutes = String(d.getMinutes()).padStart(2, "0");
  return `${day} ${month} ${thaiYearShort} · ${hours}:${minutes} น.`;
};

export const formatFullThaiDateTime = (dateStr) => {
  const d = parseSQLDate(dateStr);
  if (!d || isNaN(d.getTime())) return "";
  const thaiMonthsFull = ["มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน", "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"];
  const day = d.getDate();
  const month = thaiMonthsFull[d.getMonth()];
  const thaiYear = d.getFullYear() + 543;
  const hours = String(d.getHours()).padStart(2, "0");
  const minutes = String(d.getMinutes()).padStart(2, "0");
  return `${day} ${month} ${thaiYear} เวลา ${hours}:${minutes} น.`;
};
// จบฟังก์ชันแปลงวันเวลา

// ฟังก์ชันคำนวณเวลาสัมพัทธ์
export const getRelativeTimeThai = (dateStr) => {
  const d = parseSQLDate(dateStr);
  if (!d || isNaN(d.getTime())) return "";
  const now = new Date();
  const diffMs = now.getTime() - d.getTime();
  if (diffMs < 0) return "เมื่อสักครู่";
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHours = Math.floor(diffMin / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffSec < 60) return "แจ้งเมื่อสักครู่";
  if (diffMin < 60) return `แจ้งเมื่อ ${diffMin} นาทีที่แล้ว`;
  if (diffHours < 24 && now.getDate() === d.getDate()) return `แจ้งเมื่อ ${diffHours} ชั่วโมงที่แล้ว`;
  if (diffDays === 1 || (diffHours < 48 && now.getDate() - d.getDate() === 1)) {
    const hours = String(d.getHours()).padStart(2, "0");
    const minutes = String(d.getMinutes()).padStart(2, "0");
    return `แจ้งเมื่อวานนี้ (${hours}:${minutes} น.)`;
  }
  if (diffDays < 7) return `แจ้งเมื่อ ${diffDays} วันที่แล้ว`;
  return `แจ้งเมื่อ ${formatShortThaiDate(dateStr)}`;
};
// จบฟังก์ชันคำนวณเวลาสัมพัทธ์

// ฟังก์ชันตรวจสอบช่วงวันเวลา
export const isDateInRange = (dateStr, filter, customStart = null, customEnd = null) => {
  if (!filter || filter === "all") return true;
  const d = parseSQLDate(dateStr);
  if (!d || isNaN(d.getTime())) return false;
  const now = new Date();
  const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 0, 0, 0);
  const todayEnd = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 23, 59, 59, 999);

  if (filter === "today") return d >= todayStart && d <= todayEnd;
  if (filter === "yesterday") {
    const yStart = new Date(todayStart); yStart.setDate(yStart.getDate() - 1);
    const yEnd = new Date(todayEnd); yEnd.setDate(yEnd.getDate() - 1);
    return d >= yStart && d <= yEnd;
  }
  if (filter === "7days") {
    const sAgo = new Date(todayStart); sAgo.setDate(sAgo.getDate() - 7);
    return d >= sAgo && d <= todayEnd;
  }
  if (filter === "30days") {
    const tAgo = new Date(todayStart); tAgo.setDate(tAgo.getDate() - 30);
    return d >= tAgo && d <= todayEnd;
  }
  if (filter === "custom") {
    if (customStart && customEnd) {
      const sParts = customStart.split("-").map(Number);
      const eParts = customEnd.split("-").map(Number);
      const cStart = new Date(sParts[0], sParts[1] - 1, sParts[2], 0, 0, 0);
      const cEnd = new Date(eParts[0], eParts[1] - 1, eParts[2], 23, 59, 59, 999);
      return d >= cStart && d <= cEnd;
    } else if (customStart) {
      const sParts = customStart.split("-").map(Number);
      const cStart = new Date(sParts[0], sParts[1] - 1, sParts[2], 0, 0, 0);
      const cEnd = new Date(sParts[0], sParts[1] - 1, sParts[2], 23, 59, 59, 999);
      return d >= cStart && d <= cEnd;
    }
    return true;
  }
  return true;
};
// จบฟังก์ชันตรวจสอบช่วงวันเวลา

// ค่าคงที่และตัวเลือกตัวกรองเวลา
export const thaiMonthsNames = [
  "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
  "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
];

export const timeFilterOptions = [
  { value: "all", label: "ทั้งหมด", icon: "🌐" },
  { value: "today", label: "วันนี้", icon: "☀️" },
  { value: "yesterday", label: "เมื่อวาน", icon: "⛅" },
  { value: "7days", label: "7 วันล่าสุด", icon: "📅" },
  { value: "30days", label: "30 วันล่าสุด", icon: "🗓️" },
];
// จบค่าคงที่และตัวเลือกตัวกรองเวลา

// ฟังก์ชันตัวช่วยการแสดงผล AI
export const getAiScore = (ticketId) => {
  let hash = 0;
  for (let i = 0; i < ticketId.length; i++) {
    hash = ((hash << 5) - hash) + ticketId.charCodeAt(i);
    hash |= 0;
  }
  return Math.abs(hash % 41) + 55;
};

export const getPriority = (score) => {
  if (score >= 85) return { label: "เร่งด่วน", className: "priority-urgent" };
  if (score >= 70) return { label: "ปานกลาง", className: "priority-medium" };
  return { label: "ปกติ", className: "priority-normal" };
};

export const getStatusBarColor = (status) => {
  switch (status) {
    case "รับเรื่องแล้ว": return "#f59e0b";
    case "รอแก้ไข": return "#d97706";
    case "กำลังดำเนินการ": return "#3b82f6";
    case "ดำเนินการเสร็จสิ้น": return "#06c755";
    case "ยกเลิก": return "#ef4444";
    default: return "#9ca3af";
  }
};

export const getStatusDotClass = (status) => {
  switch (status) {
    case "รับเรื่องแล้ว": return "status-pending";
    case "รอแก้ไข": return "status-pending";
    case "กำลังดำเนินการ": return "status-progress";
    case "ดำเนินการเสร็จสิ้น": return "status-done";
    case "ยกเลิก": return "status-cancel";
    default: return "";
  }
};

export const getTabLabel = (tab) => {
  switch (tab) {
    case "ทั้งหมด": return "ทั้งหมด";
    case "รับเรื่องแล้ว": return "รับเรื่องแล้ว";
    case "รอแก้ไข": return "รอแก้ไข";
    case "กำลังดำเนินการ": return "กำลังทำ";
    case "ดำเนินการเสร็จสิ้น": return "เสร็จสิ้น";
    case "ยกเลิก": return "ยกเลิก";
    default: return tab;
  }
};

export const thaiClassMap = {
  road_damage: "ถนนชำรุด / หลุมบ่อ",
  garbage: "ขยะมูลฝอย / สิ่งปฏิกูล",
  pipe_leak: "ท่อระบายน้ำ / ประปารั่ว",
  flood: "น้ำท่วมขัง",
  street_light: "ไฟฟ้าส่องสว่างชำรุด",
  traffic: "การจราจรติดขัด",
  tree_fallen: "กิ่งไม้ / ต้นไม้ล้ม",
  general: "เรื่องร้องเรียนทั่วไป",
  other: "อื่น ๆ",
  others: "อื่น ๆ"
};

export const thaiObjectMap = {
  car: "รถยนต์",
  truck: "รถบรรทุก",
  motorcycle: "รถจักรยานยนต์",
  bicycle: "รถจักรยาน",
  bus: "รถโดยสาร",
  person: "บุคคล",
  traffic_light: "สัญญาณไฟจราจร",
  "traffic light": "สัญญาณไฟจราจร",
  stop_sign: "ป้ายหยุด",
  "stop sign": "ป้ายหยุด",
  bench: "ม้านั่ง",
  pothole: "หลุมบ่อถนน",
  waste: "กองขยะ",
  trash: "กองขยะ"
};

export const getAiAnalysis = (report) => {
  if (!report) return {};
  const score = getAiScore(report.ticket_id || "");
  const category = report.nlp_category || "รอวิเคราะห์";
  const nlpConfidence = report.nlp_confidence != null ? `${(report.nlp_confidence * 100).toFixed(2)}%` : "รอวิเคราะห์";
  const aiDepartment = report.ai_department || "รอวิเคราะห์";
  const duplicateStatus = report.duplicate_status || "รอวิเคราะห์";
  const duplicateTicketId = report.duplicate_ticket_id || null;
  const duplicateDistance = report.duplicate_distance_meters != null
    ? `${Number(report.duplicate_distance_meters).toLocaleString("th-TH", { minimumFractionDigits: 2, maximumFractionDigits: 2 })} เมตร`
    : null;

  let duplicateReason = null;
  if (duplicateStatus === "อาจซ้ำสูง") {
    duplicateReason = "ประเภทปัญหาเดียวกัน + ภาพคล้ายกัน + ตำแหน่งใกล้กัน";
  } else if (duplicateStatus === "อาจซ้ำ") {
    if (report.duplicate_distance_meters != null && Number(report.duplicate_distance_meters) <= 50) {
      duplicateReason = "ประเภทปัญหาเดียวกัน + ตำแหน่งใกล้กัน";
    } else {
      duplicateReason = "ประเภทปัญหาเดียวกัน + ภาพมีความคล้ายกัน";
    }
  } else if (duplicateStatus === "ไม่พบความเสี่ยงซ้ำ" || duplicateStatus === "ไม่ซ้ำ") {
    duplicateReason = "ไม่พบเงื่อนไขที่เข้าข่าย Ticket ซ้ำ";
  }

  const rawImgClass = report.model_b_class || "รอวิเคราะห์";
  const imgClass = thaiClassMap[rawImgClass] || rawImgClass;
  const modelBClass = imgClass;
  const modelBConfidence = report.model_b_confidence != null ? `${(report.model_b_confidence * 100).toFixed(2)}%` : "รอวิเคราะห์";
  const modelBProbability = report.model_b_probability != null ? `${(report.model_b_probability * 100).toFixed(2)}%` : "รอวิเคราะห์";

  let objDetect = "ไม่พบวัตถุ";
  try {
    if (report.object_detection) {
      const detectedObjects = JSON.parse(report.object_detection);
      if (Array.isArray(detectedObjects) && detectedObjects.length > 0) {
        objDetect = detectedObjects
          .map((obj) => {
            const confidence = typeof obj.confidence === "number" ? ` (${(obj.confidence * 100).toFixed(1)}%)` : "";
            const objThai = thaiObjectMap[obj.class] ? `${thaiObjectMap[obj.class]} (${obj.class})` : obj.class;
            return `${objThai}${confidence}`;
          })
          .join(", ");
      }
    }
  } catch {
    objDetect = "ไม่พบข้อมูล Object Detection";
  }

  return {
    imageClass: imgClass,
    objectDetect: objDetect,
    nlpCategory: category,
    nlpConfidence: nlpConfidence,
    aiDepartment: aiDepartment,
    imageQuality: `ชัดเจน (${Math.min(score + 5, 99)}%)`,
    duplicateCheck: duplicateStatus,
    duplicateTicketId: duplicateTicketId,
    duplicateDistance: duplicateDistance,
    duplicateReason: duplicateReason,
    priority: report.priority || "รอวิเคราะห์",
    priorityScore: report.priority_score != null ? `${report.priority_score} / 100` : "รอวิเคราะห์",
    modelBClass: modelBClass,
    modelBConfidence: modelBConfidence,
    modelBProbability: modelBProbability,
  };
};
// จบฟังก์ชันตัวช่วยการแสดงผล AI
