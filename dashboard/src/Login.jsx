import { useState } from "react";
import "./Login.css";

function Login({ onLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    if (!username || !password) {
      alert("กรุณากรอกชื่อผู้ใช้และรหัสผ่าน");
      return;
    }

    try {
      setLoading(true);

      const response = await fetch("http://localhost:8000/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: username,
          password: password,
        }),
      });

      if (!response.ok) {
        throw new Error("ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง");
      }

      localStorage.setItem("loggedIn", "true");
      onLogin(true);
    } catch (err) {
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") handleLogin();
  };

  return (
    <div className="lp-wrap">
      <div className="lp-card">
        <div className="lp-side">
          <div>
            <div className="lp-eyebrow">
              <span className="lp-dot" />
              ระบบแจ้งเตือนออนไลน์
            </div>

            <div className="lp-bubble-art">
              <svg width="72" height="72" viewBox="0 0 72 72" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect x="4" y="10" width="52" height="38" rx="12" fill="#1f3350" />
                <path d="M14 48 L14 60 L26 48 Z" fill="#1f3350" />
                <circle cx="20" cy="29" r="3.4" fill="#eef3f6" opacity="0.85" />
                <circle cx="32" cy="29" r="3.4" fill="#eef3f6" opacity="0.85" />
                <circle cx="44" cy="29" r="3.4" fill="#06c755" />
              </svg>
            </div>

            <h1 className="lp-headline">
              ระบบรับแจ้งปัญหา<br />ผ่าน <span>LINE</span> พร้อม AI วิเคราะห์อัตโนมัติ
            </h1>
            <p className="lp-subtext">
              เจ้าหน้าที่เข้าสู่ระบบเพื่อดู ติดตาม และตอบกลับเรื่องแจ้งปัญหาจากประชาชนที่ส่งเข้ามาทาง LINE
            </p>
          </div>

          <div className="lp-footnote">
            สำหรับเจ้าหน้าที่ที่ได้รับสิทธิ์เข้าใช้งานเท่านั้น
          </div>
        </div>

        <div className="lp-form-side">
          <h2 className="lp-title">เข้าสู่ระบบเจ้าหน้าที่</h2>
          <p className="lp-desc">กรอกข้อมูลบัญชีของคุณเพื่อเข้าใช้งาน</p>

          <div className="lp-field">
            <label className="lp-label" htmlFor="lp-username">ชื่อผู้ใช้</label>
            <input
              id="lp-username"
              className="lp-input"
              type="text"
              placeholder="กรอกชื่อผู้ใช้"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              onKeyDown={handleKeyDown}
            />
          </div>

          <div className="lp-field">
            <label className="lp-label" htmlFor="lp-password">รหัสผ่าน</label>
            <input
              id="lp-password"
              className="lp-input"
              type="password"
              placeholder="กรอกรหัสผ่าน"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              onKeyDown={handleKeyDown}
            />
          </div>

          <button className="lp-btn" onClick={handleLogin} disabled={loading}>
            {loading ? "กำลังเข้าสู่ระบบ..." : "เข้าสู่ระบบ"}
          </button>
        </div>
      </div>
    </div>
  );
}

export default Login;