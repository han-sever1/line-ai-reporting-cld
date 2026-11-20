// ไฟล์: src/utils/sound.js
// หน้าที่: ฟังก์ชันเล่นเสียงแจ้งเตือนสังเคราะห์ผ่าน Web Audio API

// เสียงแจ้งเตือนกระดิ่ง
export const playNotificationSound = () => {
  try {
    const AudioCtx = window.AudioContext || window.webkitAudioContext;
    if (!AudioCtx) return;
    const ctx = new AudioCtx();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.type = "sine";
    osc.frequency.setValueAtTime(659.25, ctx.currentTime);
    osc.frequency.setValueAtTime(880, ctx.currentTime + 0.12);
    gain.gain.setValueAtTime(0.2, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.45);
    osc.start(ctx.currentTime);
    osc.stop(ctx.currentTime + 0.45);
  } catch {
    // AudioContext may be blocked until user interacts
  }
};
// จบเสียงแจ้งเตือนกระดิ่ง
