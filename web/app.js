import { PostureEngine, radiansToDegrees } from './posture-core.js';
import { UprightBridge } from './bridge-sdk.js';
import { createMockBridge } from './mock-bridge.js';

const $ = (selector) => document.querySelector(selector);

const els = {
  modeBadge: $('#modeBadge'),
  modeValue: $('#modeValue'),
  permissionValue: $('#permissionValue'),
  connectionValue: $('#connectionValue'),
  deviceValue: $('#deviceValue'),
  rateValue: $('#rateValue'),
  posturePill: $('#posturePill'),
  scoreValue: $('#scoreValue'),
  postureCopy: $('#postureCopy'),
  timerLabel: $('#timerLabel'),
  sampleCount: $('#sampleCount'),
  gaugeFill: $('#gaugeFill'),
  canvas: $('#motionChart'),
  log: $('#eventLog'),
};

const engine = new PostureEngine();
let bridge = null;
let sessionActive = false;
let timerRemaining = 25 * 60;
let timerId = null;
let samples = [];

function log(message) {
  const li = document.createElement('li');
  li.textContent = `${new Date().toLocaleTimeString()} — ${message}`;
  els.log.prepend(li);
  while (els.log.children.length > 40) els.log.lastChild.remove();
}

function setStatus(status) {
  els.modeValue.textContent = status?.platform || '—';
  els.permissionValue.textContent = status?.permission || '—';
  els.connectionValue.textContent = status?.connection || '—';
  els.deviceValue.textContent = status?.deviceName || '—';
  els.rateValue.textContent = status?.sampleRateHz ? `${status.sampleRateHz} Hz` : '—';
}

function setPosture(result) {
  if (!result) return;
  els.posturePill.textContent = result.state;
  els.posturePill.className = `pill ${result.state}`;
  els.scoreValue.textContent = result.score;
  els.postureCopy.textContent =
    result.state === 'good' ? 'Nice. Keep your head stacked over your shoulders.' :
    result.state === 'warning' ? 'Small drift detected. Roll shoulders back and reset your neutral.' :
    'Slouch detected. Sit tall and take a quick reset breath.';
  els.gaugeFill.style.setProperty('--score', `${Math.max(4, result.score)}%`);
}

function drawChart() {
  const ctx = els.canvas.getContext('2d');
  const rect = els.canvas.getBoundingClientRect();
  const dpr = window.devicePixelRatio || 1;
  const width = Math.max(300, Math.floor(rect.width * dpr));
  const height = Math.floor(260 * dpr);
  if (els.canvas.width !== width || els.canvas.height !== height) {
    els.canvas.width = width;
    els.canvas.height = height;
  }
  ctx.clearRect(0, 0, width, height);
  ctx.fillStyle = 'rgba(0,0,0,0.16)';
  ctx.fillRect(0, 0, width, height);

  const data = samples.slice(-90);
  if (data.length < 2) {
    ctx.fillStyle = '#9fb4c6';
    ctx.font = `${16 * dpr}px system-ui`;
    ctx.fillText('Start a session to stream motion.', 24 * dpr, 42 * dpr);
    return;
  }

  const plot = (key, color) => {
    ctx.beginPath();
    ctx.strokeStyle = color;
    ctx.lineWidth = 3 * dpr;
    data.forEach((sample, index) => {
      const x = (index / Math.max(1, data.length - 1)) * width;
      const y = height / 2 - sample[key] * 4.2 * dpr;
      if (index === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
    });
    ctx.stroke();
  };

  ctx.strokeStyle = 'rgba(255,255,255,0.16)';
  ctx.lineWidth = 1 * dpr;
  ctx.beginPath();
  ctx.moveTo(0, height / 2);
  ctx.lineTo(width, height / 2);
  ctx.stroke();

  plot('pitch', '#3ee5a4');
  plot('roll', '#ffd166');

  ctx.fillStyle = '#9fb4c6';
  ctx.font = `${12 * dpr}px system-ui`;
  ctx.fillText('pitch', 18 * dpr, 24 * dpr);
  ctx.fillStyle = '#ffd166';
  ctx.fillText('roll', 72 * dpr, 24 * dpr);
}

function updateTimerLabel() {
  const m = Math.floor(timerRemaining / 60).toString().padStart(2, '0');
  const s = Math.floor(timerRemaining % 60).toString().padStart(2, '0');
  els.timerLabel.textContent = `${m}:${s}`;
}

function startTimer() {
  stopTimer();
  timerId = setInterval(() => {
    timerRemaining = Math.max(0, timerRemaining - 1);
    updateTimerLabel();
    if (timerRemaining === 0) {
      bridge?.app.haptic?.('alert');
      bridge?.app.speak?.('Focus interval complete. Take a posture reset.');
      stopSession();
    }
  }, 1000);
}

function stopTimer() {
  if (timerId) clearInterval(timerId);
  timerId = null;
}

async function startSession() {
  if (!bridge) return;
  const status = await bridge.headphones.getStatus();
  setStatus(status);
  if (status.permission !== 'granted') {
    await bridge.headphones.requestPermission();
  }
  await bridge.headphones.startUpdates({ sampleRateHz: 25 });
  sessionActive = true;
  $('#startBtn').disabled = true;
  $('#stopBtn').disabled = false;
  $('#permissionBtn').disabled = true;
  $('#calibrateBtn').disabled = false;
  timerRemaining = 25 * 60;
  updateTimerLabel();
  startTimer();
  log('Session started.');
}

async function stopSession() {
  if (!bridge) return;
  await bridge.headphones.stopUpdates();
  sessionActive = false;
  $('#startBtn').disabled = false;
  $('#stopBtn').disabled = true;
  $('#permissionBtn').disabled = false;
  stopTimer();
  log('Session stopped.');
}

async function refreshStatus() {
  if (!bridge) return;
  try {
    const status = await bridge.headphones.getStatus();
    setStatus(status);
  } catch (error) {
    log(`Status failed: ${error.message}`);
  }
}

async function handleMotion(sample) {
  samples.push({ pitch: sample.attitude.pitch, roll: sample.attitude.roll, ts: sample.ts });
  if (samples.length > 240) samples.shift();
  const result = engine.update(sample);
  setPosture(result);
  els.sampleCount.textContent = `${samples.length} samples`;
  drawChart();
}

async function calibrate() {
  try {
    const result = await bridge.headphones.calibrateNeutral();
    engine.neutral = result.neutral || engine.calibrate();
    log(`Neutral calibrated: pitch ${radiansToDegrees(engine.neutral.pitch).toFixed(1)}°, roll ${radiansToDegrees(engine.neutral.roll).toFixed(1)}°`);
  } catch (error) {
    engine.calibrate();
    log(`Calibration fallback used: ${error.message}`);
  }
}

async function boot() {
  try {
    bridge = new UprightBridge();
    await bridge.ready();
    if (!bridge.isNative) {
      bridge = await createMockBridge();
    }
    els.modeBadge.textContent = bridge.isNative ? 'Native shell' : 'Browser mock';
    els.modeBadge.classList.toggle('mock', !bridge.isNative);
    bridge.on('motion', handleMotion);
    bridge.on('status', (status) => {
      setStatus(status);
      log(`Status: ${status.connection} / ${status.permission}`);
    });
    bridge.on('interruption', (payload) => log(`Interruption: ${payload.reason}`));
    bridge.on('error', (payload) => log(`Error: ${payload.code} — ${payload.message}`));
    await refreshStatus();
    drawChart();
    log(bridge.isNative ? 'Native bridge ready.' : 'Mock bridge ready.');
  } catch (error) {
    log(`Boot failed: ${error.message}`);
    bridge = await createMockBridge();
    els.modeBadge.textContent = 'Browser mock';
    bridge.on('motion', handleMotion);
    bridge.on('status', setStatus);
    await refreshStatus();
  }
}

$('#startBtn').addEventListener('click', startSession);
$('#stopBtn').addEventListener('click', stopSession);
$('#permissionBtn').addEventListener('click', async () => {
  const permission = await bridge.headphones.requestPermission();
  log(`Permission result: ${permission}`);
  await refreshStatus();
});
$('#calibrateBtn').addEventListener('click', calibrate);
$('#settingsBtn').addEventListener('click', () => bridge.app.openSettings());
$('#hapticBtn').addEventListener('click', () => bridge.app.haptic('subtle'));
$('#speakBtn').addEventListener('click', () => bridge.app.speak('Posture check. Roll shoulders back and lengthen your spine.'));
$('#resetBtn').addEventListener('click', () => {
  samples = [];
  engine.samples = [];
  engine.state = 'unknown';
  setPosture({ state: 'unknown', score: 0 });
  els.sampleCount.textContent = '0 samples';
  timerRemaining = 25 * 60;
  updateTimerLabel();
  drawChart();
});
$('#clearLogBtn').addEventListener('click', () => els.log.replaceChildren());
window.addEventListener('resize', drawChart);

boot();
