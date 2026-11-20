// ไฟล์: src/App.jsx
// หน้าที่: Component หลัก จัดการ State ส่วนกลาง Polling ข้อมูล และ Router สลับหน้าจอ

// ส่วนนำเข้าโมดูล
import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import "./App.css";
import Login from "./Login";

// บริการ API
import {
  fetchReportsApi,
  fetchActivitiesApi,
  fetchReportDetailApi,
  updateStatusApi,
  acceptReportApi,
  updateAssignmentApi,
  deleteReportApi,
  fetchSettingsApi,
  updateSettingApi,
} from "./services/api";

// ฟังก์ชันช่วยเหลือ
import { isDateInRange } from "./utils/dateUtils";
import { playNotificationSound } from "./utils/sound";

// คอมโพเนนต์โครงร่าง
import LiveToast from "./components/common/LiveToast";
import Sidebar from "./components/layout/Sidebar";
import Header from "./components/layout/Header";

// คอมโพเนนต์หน้าจอ
import DashboardPage from "./pages/DashboardPage";
import ReportsPage from "./pages/ReportsPage";
import TrackingPage from "./pages/TrackingPage";
import AiAnalyticsPage from "./pages/AiAnalyticsPage";
import MapPage from "./pages/MapPage";
import UsersPage from "./pages/UsersPage";
import SettingsPage from "./pages/SettingsPage";
// จบส่วนนำเข้าโมดูล

// Component หลัก App
function App() {
  // สถานะหลักของข้อมูล
  const [reports, setReports] = useState([]);
  const [selectedReport, setSelectedReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [loggedIn, setLoggedIn] = useState(
    localStorage.getItem("loggedIn") === "true"
  );
  const [searchText, setSearchText] = useState("");
  const [statusFilter, setStatusFilter] = useState("ทั้งหมด");
  const [darkMode, setDarkMode] = useState(
    localStorage.getItem("darkMode") === "true"
  );

  // สถานะตัวกรองเวลาและปฏิทินส่วนกลาง
  const [globalTimeFilter, setGlobalTimeFilter] = useState("all");
  const [customStartDate, setCustomStartDate] = useState("");
  const [customEndDate, setCustomEndDate] = useState("");
  const [calendarViewDate, setCalendarViewDate] = useState(() => new Date());
  const [showGlobalTimeMenu, setShowGlobalTimeMenu] = useState(false);
  const globalTimeRef = useRef(null);

  // สถานะตัวกรองเวลาเฉพาะตาราง
  const [tableTimeFilter, setTableTimeFilter] = useState("all");
  const [showTableTimeMenu, setShowTableTimeMenu] = useState(false);
  const tableTimeRef = useRef(null);

  // สถานะตัวกรองระดับความเร่งด่วนเฉพาะตาราง
  const [priorityFilter, setPriorityFilter] = useState("all");
  const [showPriorityMenu, setShowPriorityMenu] = useState(false);
  const priorityRef = useRef(null);

  // สถานะการแจ้งเตือนกระดิ่ง
  const [showNotifMenu, setShowNotifMenu] = useState(false);
  const notifRef = useRef(null);
  const [isBellRinging, setIsBellRinging] = useState(false);
  const lastReportTicketRef = useRef(null);

  // การนำทางหน้าจอ
  const [activePage, setActivePage] = useState("dashboard");
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // ประวัติกิจกรรมและการแจ้งเตือนสด
  const [activities, setActivities] = useState([]);
  const [liveToast, setLiveToast] = useState(null);
  const lastActivityIdRef = useRef(null);

  // การตั้งค่าระบบ
  const [systemSettings, setSystemSettings] = useState({
    line_auto_reply: true,
    line_department_notify: true,
    ai_auto_analysis: true,
    database_type: "PostgreSQL",
  });
  const [settingsSaving, setSettingsSaving] = useState(false);
  const [settingsNotice, setSettingsNotice] = useState("");

  // ปิดเมนูดรอปดาวน์เมื่อคลิกนอกพื้นที่
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (globalTimeRef.current && !globalTimeRef.current.contains(e.target)) {
        setShowGlobalTimeMenu(false);
      }
      if (tableTimeRef.current && !tableTimeRef.current.contains(e.target)) {
        setShowTableTimeMenu(false);
      }
      if (priorityRef.current && !priorityRef.current.contains(e.target)) {
        setShowPriorityMenu(false);
      }
      if (notifRef.current && !notifRef.current.contains(e.target)) {
        setShowNotifMenu(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // ฟังก์ชันสลับธีมและออกจากระบบ
  const toggleDarkMode = () => {
    setDarkMode((prev) => {
      const nextVal = !prev;
      localStorage.setItem("darkMode", String(nextVal));
      return nextVal;
    });
  };

  const handleLogout = () => {
    localStorage.removeItem("loggedIn");
    setLoggedIn(false);
  };

  const handleNavClick = (page) => {
    setActivePage(page);
    setMobileMenuOpen(false);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  // เรียก API โหลดข้อมูล
  const fetchReports = useCallback(async (showLoading = false) => {
    try {
      if (showLoading) setLoading(true);
      const data = await fetchReportsApi();
      const updatedList = data.reports || [];
      setReports(updatedList);

      if (updatedList.length > 0) {
        const latestTicket = updatedList[0]?.ticket_id;
        if (lastReportTicketRef.current === null) {
          lastReportTicketRef.current = latestTicket;
        } else if (latestTicket && latestTicket !== lastReportTicketRef.current) {
          lastReportTicketRef.current = latestTicket;
          setIsBellRinging(true);
          playNotificationSound();
          setTimeout(() => setIsBellRinging(false), 5000);
        }
      }

      setSelectedReport((prev) => {
        if (!prev) return null;
        const fresh = updatedList.find((r) => r.ticket_id === prev.ticket_id);
        return fresh ? { ...prev, ...fresh } : prev;
      });

      setError("");
    } catch (err) {
      setError(err.message);
    } finally {
      if (showLoading) setLoading(false);
    }
  }, []);

  const fetchActivities = useCallback(async () => {
    try {
      const data = await fetchActivitiesApi();
      const acts = data.activities || [];
      setActivities(acts);

      if (acts.length > 0) {
        const newest = acts[0];
        if (lastActivityIdRef.current === null) {
          lastActivityIdRef.current = newest.id;
        } else if (newest.id > lastActivityIdRef.current) {
          lastActivityIdRef.current = newest.id;
          setLiveToast(newest);
          setTimeout(() => setLiveToast(null), 7000);
        }
      }
    } catch (err) {
      console.error("Error fetching activities:", err);
    }
  }, []);

  const fetchReportDetail = async (ticketId) => {
    try {
      const data = await fetchReportDetailApi(ticketId);
      setSelectedReport(data);
    } catch (err) {
      alert(err.message);
    }
  };

  const updateStatus = async (ticketId, newStatus, statusReason = null) => {
    try {
      const data = await updateStatusApi(ticketId, newStatus, statusReason);
      alert(`อัปเดตสถานะเป็น: ${data.status}` + (statusReason ? ` (${statusReason})` : ""));
      await fetchReports();
      await fetchReportDetail(ticketId);
    } catch (err) {
      alert(err.message);
    }
  };

  const handleAcceptReport = async (ticketId) => {
    const defaultOfficer = localStorage.getItem("officer_name") || "นายสมชาย ใจดี";
    const officerName = window.prompt("ระบุชื่อเจ้าหน้าที่ผู้รับเรื่อง:", defaultOfficer);
    if (!officerName || !officerName.trim()) return;
    localStorage.setItem("officer_name", officerName.trim());

    try {
      const resData = await acceptReportApi(ticketId, officerName.trim());
      alert(
        `✅ ยืนยันรับเรื่องเรียบร้อยแล้ว\n\n` +
        `🎫 Ticket: ${ticketId}\n` +
        `👤 ผู้รับเรื่อง: ${resData.accepted_by}\n` +
        `🏢 หน่วยงาน: ${resData.department}\n` +
        `🕐 วันที่รับเรื่อง: ${resData.accepted_at}\n\n` +
        `สถานะ: รับเรื่องแล้ว`
      );
      await fetchReports();
      await fetchReportDetail(ticketId);
    } catch (err) {
      alert(err.message);
    }
  };

  const updateAssignment = async (ticketId, category, department) => {
    try {
      await updateAssignmentApi(ticketId, category, department);
      alert("อัปเดตประเภทปัญหาและหน่วยงานสำเร็จ");
      await fetchReports();
      await fetchReportDetail(ticketId);
    } catch (err) {
      alert(err.message);
    }
  };

  const deleteReport = async (ticketId) => {
    const confirmed = window.confirm(`ต้องการลบเรื่อง ${ticketId} ใช่หรือไม่? การลบไม่สามารถย้อนกลับได้`);
    if (!confirmed) return;

    try {
      await deleteReportApi(ticketId);
      if (selectedReport?.ticket_id === ticketId) {
        setSelectedReport(null);
      }
      await fetchReports();
    } catch (err) {
      alert(err.message);
    }
  };

  const fetchSettings = useCallback(async () => {
    try {
      const data = await fetchSettingsApi();
      setSystemSettings(data);
    } catch (err) {
      console.error("fetchSettings error:", err);
    }
  }, []);

  const handleToggleSetting = async (key) => {
    const nextVal = !systemSettings[key];
    setSystemSettings((prev) => ({ ...prev, [key]: nextVal }));
    setSettingsSaving(true);
    try {
      const data = await updateSettingApi(key, nextVal);
      setSystemSettings(data.settings);
      setSettingsNotice("บันทึกการตั้งค่าระบบเรียบร้อยแล้ว");
      setTimeout(() => setSettingsNotice(""), 3000);
    } catch (err) {
      console.error("handleToggleSetting error:", err);
      setSystemSettings((prev) => ({ ...prev, [key]: !nextVal }));
    } finally {
      setSettingsSaving(false);
    }
  };

  // Polling ข้อมูลทุก 4 วินาที
  useEffect(() => {
    fetchReports(true);
    fetchActivities();
    fetchSettings();

    const interval = setInterval(() => {
      fetchReports(false);
      fetchActivities();
    }, 4000);

    return () => clearInterval(interval);
  }, [fetchReports, fetchActivities, fetchSettings]);

  // คำนวณช่วงเวลาและปฏิทิน
  const globalTimeFilteredReports = useMemo(() => {
    return reports.filter((item) =>
      isDateInRange(item.created_at, globalTimeFilter, customStartDate, customEndDate)
    );
  }, [reports, globalTimeFilter, customStartDate, customEndDate]);

  const reportDatesSet = useMemo(() => {
    const s = new Set();
    reports.forEach((r) => {
      if (r.created_at) {
        const dStr = r.created_at.split(" ")[0].split("T")[0];
        if (dStr) s.add(dStr);
      }
    });
    return s;
  }, [reports]);

  const getGlobalTimeFilterLabel = () => {
    if (globalTimeFilter === "all") return "ทั้งหมด";
    if (globalTimeFilter === "today") return "วันนี้";
    if (globalTimeFilter === "yesterday") return "เมื่อวาน";
    if (globalTimeFilter === "7days") return "7 วันล่าสุด";
    if (globalTimeFilter === "30days") return "30 วันล่าสุด";
    if (globalTimeFilter === "custom") {
      if (customStartDate && customEndDate) {
        if (customStartDate === customEndDate) {
          const p = customStartDate.split("-");
          const thaiMonths = ["ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."];
          const m = thaiMonths[Number(p[1]) - 1] || "";
          const y = (Number(p[0]) + 543) % 100;
          return `${Number(p[2])} ${m} ${y}`;
        }
        const sP = customStartDate.split("-");
        const eP = customEndDate.split("-");
        const thaiMonths = ["ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."];
        return `${Number(sP[2])} ${thaiMonths[Number(sP[1]) - 1]} - ${Number(eP[2])} ${thaiMonths[Number(eP[1]) - 1]}`;
      }
      if (customStartDate) {
        const p = customStartDate.split("-");
        const thaiMonths = ["ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."];
        return `${Number(p[2])} ${thaiMonths[Number(p[1]) - 1]} ${(Number(p[0]) + 543) % 100}`;
      }
      return "เลือกวันที่";
    }
    return "ตัวกรองเวลา";
  };

  const calYear = calendarViewDate.getFullYear();
  const calMonth = calendarViewDate.getMonth();
  const daysInCurrentMonth = new Date(calYear, calMonth + 1, 0).getDate();
  const firstDayOfWeek = new Date(calYear, calMonth, 1).getDay();

  const handlePrevMonth = () => setCalendarViewDate(new Date(calYear, calMonth - 1, 1));
  const handleNextMonth = () => setCalendarViewDate(new Date(calYear, calMonth + 1, 1));
  const handleMonthChange = (newMonth) => setCalendarViewDate(new Date(calYear, Number(newMonth), 1));
  const handleYearChange = (newYear) => setCalendarViewDate(new Date(Number(newYear), calMonth, 1));

  const handleCalendarDayClick = (dayNum) => {
    const y = calYear;
    const m = String(calMonth + 1).padStart(2, "0");
    const d = String(dayNum).padStart(2, "0");
    const dateStr = `${y}-${m}-${d}`;
    setCustomStartDate(dateStr);
    setCustomEndDate(dateStr);
    setGlobalTimeFilter("custom");
    setShowGlobalTimeMenu(false);
  };

  // กรองข้อมูลหน้าต่างๆ
  const trackingReports = useMemo(() => {
    if (!searchText.trim()) return globalTimeFilteredReports;
    const keyword = searchText.toLowerCase().trim();
    return globalTimeFilteredReports.filter((item) => {
      const ticketId = String(item.ticket_ref || item.ticket_id || "").toLowerCase();
      const description = String(item.description || item.problem_type || "").toLowerCase();
      const agency = String(item.agency_name || item.department || item.agency || "").toLowerCase();
      return ticketId.includes(keyword) || description.includes(keyword) || agency.includes(keyword);
    });
  }, [globalTimeFilteredReports, searchText]);

  const mapFilteredReports = useMemo(() => {
    if (!searchText.trim()) return globalTimeFilteredReports;
    const keyword = searchText.toLowerCase().trim();
    return globalTimeFilteredReports.filter((item) => {
      const ticketId = String(item.ticket_ref || item.ticket_id || "").toLowerCase();
      const description = String(item.description || item.problem_type || "").toLowerCase();
      const agency = String(item.agency_name || item.department || item.agency || "").toLowerCase();
      return ticketId.includes(keyword) || description.includes(keyword) || agency.includes(keyword);
    });
  }, [globalTimeFilteredReports, searchText]);

  const stats = useMemo(() => {
    const total = globalTimeFilteredReports.length;
    const pending = globalTimeFilteredReports.filter(
      (r) => r.status === "รับเรื่องแล้ว" || r.status === "กำลังดำเนินการ" || r.status === "รอแก้ไข"
    ).length;
    const completed = globalTimeFilteredReports.filter(
      (r) => r.status === "ดำเนินการเสร็จสิ้น"
    ).length;
    const completedPercent = total > 0 ? Math.round((completed / total) * 100) : 0;
    return { total, pending, completed, completedPercent };
  }, [globalTimeFilteredReports]);

  const filteredReports = useMemo(() => {
    return globalTimeFilteredReports.filter((report) => {
      const keyword = searchText.toLowerCase();
      const matchSearch =
        report.ticket_id.toLowerCase().includes(keyword) ||
        report.description.toLowerCase().includes(keyword);
      const matchStatus = statusFilter === "ทั้งหมด" || report.status === statusFilter;
      const matchTime = isDateInRange(report.created_at, tableTimeFilter);
      const matchPriority = priorityFilter === "all" || report.priority === priorityFilter;
      return matchSearch && matchStatus && matchTime && matchPriority;
    });
  }, [globalTimeFilteredReports, searchText, statusFilter, tableTimeFilter, priorityFilter]);

  const chartData = useMemo(() => {
    const days = [];
    for (let i = 6; i >= 0; i--) {
      const d = new Date();
      d.setDate(d.getDate() - i);
      const dateStr = d.toISOString().split("T")[0];
      const dayLabel = `${d.getDate()}/${d.getMonth() + 1}`;
      const dayReports = reports.filter((r) => r.created_at && r.created_at.startsWith(dateStr));
      const dayCompleted = dayReports.filter((r) => r.status === "ดำเนินการเสร็จสิ้น").length;
      days.push({ label: dayLabel, total: dayReports.length, completed: dayCompleted });
    }
    return days;
  }, [reports]);

  const chartMax = useMemo(() => {
    return Math.max(...chartData.map((d) => d.total), 1);
  }, [chartData]);

  const pieData = useMemo(() => {
    const total = reports.length;
    const received = reports.filter((r) => r.status === "รับเรื่องแล้ว" || r.status === "รอแก้ไข").length;
    const inProgress = reports.filter((r) => r.status === "กำลังดำเนินการ").length;
    const completed = reports.filter((r) => r.status === "ดำเนินการเสร็จสิ้น").length;
    const cancelled = reports.filter((r) => r.status === "ยกเลิก").length;
    const toDeg = (count) => (total > 0 ? (count / total) * 360 : 0);
    const a1 = toDeg(received);
    const a2 = a1 + toDeg(inProgress);
    const a3 = a2 + toDeg(completed);
    return { received, inProgress, completed, cancelled, a1, a2, a3 };
  }, [reports]);

  // การคลิกจากกระดิ่งแจ้งเตือน
  const onSelectReportFromNotif = (item) => {
    setSelectedReport(item);
    fetchReportDetail(item.ticket_id);
    setActivePage("reports");
    setShowNotifMenu(false);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const onViewAllReports = () => {
    setActivePage("reports");
    setShowNotifMenu(false);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  // ตรวจสอบล็อกอิน
  if (!loggedIn) {
    return <Login onLogin={setLoggedIn} />;
  }

  return (
    <div className="app-container" data-theme={darkMode ? "dark" : "light"}>
      {/* ป๊อปอัปแจ้งเตือนสด */}
      <LiveToast liveToast={liveToast} onClose={() => setLiveToast(null)} />

      {/* แถบเมนูด้านซ้าย */}
      <Sidebar
        activePage={activePage}
        mobileMenuOpen={mobileMenuOpen}
        setMobileMenuOpen={setMobileMenuOpen}
        handleNavClick={handleNavClick}
        stats={stats}
        handleLogout={handleLogout}
      />

      {/* เนื้อหาหลัก */}
      <main className="main-content">
        {/* แถบส่วนหัวด้านบน */}
        <Header
          activePage={activePage}
          mobileMenuOpen={mobileMenuOpen}
          setMobileMenuOpen={setMobileMenuOpen}
          searchText={searchText}
          setSearchText={setSearchText}
          globalTimeFilter={globalTimeFilter}
          setGlobalTimeFilter={setGlobalTimeFilter}
          customStartDate={customStartDate}
          setCustomStartDate={setCustomStartDate}
          customEndDate={customEndDate}
          setCustomEndDate={setCustomEndDate}
          calendarViewDate={calendarViewDate}
          showGlobalTimeMenu={showGlobalTimeMenu}
          setShowGlobalTimeMenu={setShowGlobalTimeMenu}
          globalTimeRef={globalTimeRef}
          reportDatesSet={reportDatesSet}
          getGlobalTimeFilterLabel={getGlobalTimeFilterLabel}
          handlePrevMonth={handlePrevMonth}
          handleNextMonth={handleNextMonth}
          handleMonthChange={handleMonthChange}
          handleYearChange={handleYearChange}
          handleCalendarDayClick={handleCalendarDayClick}
          daysInCurrentMonth={daysInCurrentMonth}
          firstDayOfWeek={firstDayOfWeek}
          calYear={calYear}
          calMonth={calMonth}
          darkMode={darkMode}
          toggleDarkMode={toggleDarkMode}
          reports={reports}
          isBellRinging={isBellRinging}
          setIsBellRinging={setIsBellRinging}
          showNotifMenu={showNotifMenu}
          setShowNotifMenu={setShowNotifMenu}
          notifRef={notifRef}
          onSelectReportFromNotif={onSelectReportFromNotif}
          onViewAllReports={onViewAllReports}
          handleLogout={handleLogout}
        />

        {/* หน้า 1: Dashboard */}
        {activePage === "dashboard" && (
          <DashboardPage
            stats={stats}
            reports={reports}
            pieData={pieData}
            chartData={chartData}
            chartMax={chartMax}
          />
        )}

        {/* หน้า 2: รายการปัญหา */}
        {activePage === "reports" && (
          <ReportsPage
            filteredReports={filteredReports}
            reports={reports}
            selectedReport={selectedReport}
            loading={loading}
            error={error}
            statusFilter={statusFilter}
            setStatusFilter={setStatusFilter}
            tableTimeFilter={tableTimeFilter}
            setTableTimeFilter={setTableTimeFilter}
            showTableTimeMenu={showTableTimeMenu}
            setShowTableTimeMenu={setShowTableTimeMenu}
            tableTimeRef={tableTimeRef}
            priorityFilter={priorityFilter}
            setPriorityFilter={setPriorityFilter}
            showPriorityMenu={showPriorityMenu}
            setShowPriorityMenu={setShowPriorityMenu}
            priorityRef={priorityRef}
            fetchReportDetail={fetchReportDetail}
            deleteReport={deleteReport}
            updateAssignment={updateAssignment}
            handleAcceptReport={handleAcceptReport}
            updateStatus={updateStatus}
            activities={activities}
            chartData={chartData}
            chartMax={chartMax}
          />
        )}

        {/* หน้า 3: ติดตามสถานะ */}
        {activePage === "tracking" && (
          <TrackingPage
            reports={reports}
            trackingReports={trackingReports}
            searchText={searchText}
            onSelectReport={(ticketId) => {
              fetchReportDetail(ticketId);
              setActivePage("reports");
            }}
          />
        )}

        {/* หน้า 4: ผล AI วิเคราะห์ */}
        {activePage === "ai" && (
          <AiAnalyticsPage
            reports={reports}
            selectedReport={selectedReport}
            setSelectedReport={setSelectedReport}
            fetchReportDetail={fetchReportDetail}
          />
        )}

        {/* หน้า 5: แผนที่ปัญหา */}
        {activePage === "map" && (
          <MapPage
            mapFilteredReports={mapFilteredReports}
            selectedReport={selectedReport}
            setSelectedReport={setSelectedReport}
            searchText={searchText}
            setSearchText={setSearchText}
            fetchReportDetail={fetchReportDetail}
          />
        )}

        {/* หน้า 6: จัดการผู้ใช้ */}
        {activePage === "users" && <UsersPage />}

        {/* หน้า 7: ตั้งค่าระบบ */}
        {activePage === "settings" && (
          <SettingsPage
            systemSettings={systemSettings}
            handleToggleSetting={handleToggleSetting}
            settingsSaving={settingsSaving}
            settingsNotice={settingsNotice}
          />
        )}
      </main>
    </div>
  );
}
// จบComponent หลัก App

export default App;
