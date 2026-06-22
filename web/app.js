const { PostureEngine, radiansToDegrees } = window.UprightPosture;

const LANDING_KEY = 'upright.landingSeen';

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
let lastStatus = null;
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
  if (!status || typeof status !== 'object') return;
  lastStatus = status;
  els.modeValue.textContent = status.platform || '—';
  els.permissionValue.textContent = status.permission || '—';
  els.connectionValue.textContent = status.connection || '—';
  els.deviceValue.textContent = status.deviceName || '—';
  els.rateValue.textContent = status.sampleRateHz ? `${status.sampleRateHz} Hz` : '—';
}

function withTimeout(promise, ms, label) {
  return Promise.race([
    promise,
    new Promise((_, reject) => {
      setTimeout(() => reject(new Error(`${label} timed out after ${ms / 1000}s`)), ms);
    }),
  ]);
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
  ctx.fillStyle = '#f4f4f5';
  ctx.fillRect(0, 0, width, height);

  const data = samples.slice(-90);
  if (data.length < 2) {
    ctx.fillStyle = '#71717a';
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

  ctx.strokeStyle = 'rgba(24, 24, 27, 0.1)';
  ctx.lineWidth = 1 * dpr;
  ctx.beginPath();
  ctx.moveTo(0, height / 2);
  ctx.lineTo(width, height / 2);
  ctx.stroke();

  plot('pitch', '#0d9488');
  plot('roll', '#d97706');

  ctx.fillStyle = '#0d9488';
  ctx.font = `${12 * dpr}px system-ui`;
  ctx.fillText('pitch', 18 * dpr, 24 * dpr);
  ctx.fillStyle = '#d97706';
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
  log('Starting session…');
  try {
    let status = lastStatus;
    if (!status) {
      status = await withTimeout(bridge.headphones.getStatus(), 5000, 'getStatus');
      setStatus(status);
    }
    if (status.permission !== 'granted') {
      log('Requesting motion permission…');
      const permission = await withTimeout(bridge.headphones.requestPermission(), 10000, 'requestPermission');
      log(`Permission result: ${permission}`);
    }
    await withTimeout(bridge.headphones.startUpdates({ sampleRateHz: 25 }), 5000, 'startUpdates');
    sessionActive = true;
    $('#startBtn').disabled = true;
    $('#stopBtn').disabled = false;
    $('#permissionBtn').disabled = true;
    $('#calibrateBtn').disabled = false;
    timerRemaining = 25 * 60;
    updateTimerLabel();
    startTimer();
    log('Session started.');
  } catch (error) {
    log(`Start failed: ${error.message}`);
  }
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
    const status = await withTimeout(bridge.headphones.getStatus(), 5000, 'getStatus');
    setStatus(status);
  } catch (error) {
    if (lastStatus) setStatus(lastStatus);
    log(`Status failed: ${error.message}`);
  }
}

function attachBridgeListeners() {
  bridge.on('motion', handleMotion);
  bridge.on('status', (status) => {
    setStatus(status);
    log(`Status: ${status.connection} / ${status.permission}`);
  });
  bridge.on('interruption', (payload) => log(`Interruption: ${payload.reason}`));
  bridge.on('error', (payload) => log(`Error: ${payload.code} — ${payload.message}`));
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
    bridge = new window.UprightBridge();
    window.__uprightBridgeInstance = bridge;
    attachBridgeListeners();
    const readyPromise = bridge.ready();
    const timeoutPromise = new Promise((_, reject) => {
      setTimeout(() => reject(new Error('Native bridge timed out after 5s')), 5000);
    });
    await Promise.race([readyPromise, timeoutPromise]);
    if (!bridge.isNative) {
      bridge = await window.createMockBridge();
      window.__uprightBridgeInstance = bridge;
      attachBridgeListeners();
    }
    els.modeBadge.textContent = bridge.isNative ? 'Native shell' : 'Browser mock';
    els.modeBadge.classList.toggle('mock', !bridge.isNative);
    await refreshStatus();
    drawChart();
    log(bridge.isNative ? 'Native bridge ready.' : 'Mock bridge ready.');
  } catch (error) {
    els.modeBadge.textContent = 'Boot failed';
    els.modeBadge.classList.add('mock');
    log(`Boot failed: ${error.message}`);
    try {
      bridge = await window.createMockBridge();
      window.__uprightBridgeInstance = bridge;
      attachBridgeListeners();
      els.modeBadge.textContent = 'Browser mock';
      await refreshStatus();
      drawChart();
      log('Fell back to mock bridge.');
    } catch (fallbackError) {
      log(`Fallback failed: ${fallbackError.message}`);
    }
  }
}

$('#startBtn').addEventListener('click', startSession);
$('#stopBtn').addEventListener('click', stopSession);
$('#permissionBtn').addEventListener('click', async () => {
  try {
    log('Requesting motion permission…');
    const permission = await withTimeout(bridge.headphones.requestPermission(), 10000, 'requestPermission');
    log(`Permission result: ${permission}`);
    await refreshStatus();
  } catch (error) {
    log(`Permission failed: ${error.message}`);
  }
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

function showApp() {
  $('#landingView')?.classList.add('hidden');
  $('#appView')?.classList.remove('hidden');
  boot();
}

function dismissLanding() {
  const landing = $('#landingView');
  landing?.classList.add('landing-dismiss');
  setTimeout(() => {
    try {
      localStorage.setItem(LANDING_KEY, '1');
    } catch (_) {
      /* private browsing */
    }
    showApp();
  }, 280);
}

function init() {
  let seen = false;
  try {
    seen = localStorage.getItem(LANDING_KEY) === '1';
  } catch (_) {
    seen = false;
  }

  if (seen) {
    showApp();
    return;
  }

  const landing = $('#landingView');
  landing?.classList.remove('hidden');
  $('#landingStartBtn')?.addEventListener('click', dismissLanding);
}

init();
