const { PostureEngine, radiansToDegrees } = window.UprightPosture;

const LANDING_KEY = 'upright.landingSeen';

const $ = (selector) => document.querySelector(selector);

const els = {
  modeBadge: $('#modeBadge'),
  modeValue: $('#modeValue'),
  permissionValue: $('#permissionValue'),
  connectionValue: $('#connectionValue'),
  motionReadyValue: $('#motionReadyValue'),
  deviceValue: $('#deviceValue'),
  rateValue: $('#rateValue'),
  posturePill: $('#posturePill'),
  scoreValue: $('#scoreValue'),
  postureCopy: $('#postureCopy'),
  timerLabel: $('#timerLabel'),
  sampleCount: $('#sampleCount'),
  gaugeFill: $('#gaugeFill'),
  canvas: $('#motionChart'),
  motionPitch: $('#motionPitch'),
  motionRoll: $('#motionRoll'),
  motionWindow: $('#motionWindow'),
  sessionHistory: $('#sessionHistory'),
  historyEmpty: $('#historyEmpty'),
  log: $('#eventLog'),
};

const engine = new PostureEngine();
let bridge = null;
let lastStatus = null;
let sessionActive = false;
let timerRemaining = 25 * 60;
let timerId = null;
let samples = [];
let sessionStats = null;
let bootPromise = null;
let booted = false;
let lastLoggedConnection = null;
let statusPollId = null;

function startStatusPolling() {
  if (statusPollId) return;
  statusPollId = setInterval(() => {
    if (!bridge || sessionActive) return;
    refreshStatus().catch(() => {});
  }, 2500);
}

function stopStatusPolling() {
  if (!statusPollId) return;
  clearInterval(statusPollId);
  statusPollId = null;
}

function log(message) {
  if (!els.log) return;
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
  els.motionReadyValue.textContent = status.deviceMotionAvailable ? 'yes' : 'no';
  els.deviceValue.textContent = status.deviceName || '—';
  els.rateValue.textContent = status.sampleRateHz ? `${status.sampleRateHz} Hz` : '—';

  const permissionBtn = $('#permissionBtn');
  if (permissionBtn) {
    const granted = status.permission === 'granted';
    permissionBtn.disabled = granted;
    permissionBtn.textContent = granted ? 'Permission Granted' : 'Request Permission';
  }

  if (status.connection === 'connected' || status.connection === 'active') {
    stopStatusPolling();
  } else if (booted) {
    startStatusPolling();
  }
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

function motionDeltas(sample) {
  const pitchDelta = sample.pitch - engine.neutral.pitch;
  const rollDelta = sample.roll - engine.neutral.roll;
  return {
    pitchDeg: radiansToDegrees(pitchDelta),
    rollDeg: radiansToDegrees(rollDelta),
  };
}

function updateMotionReadouts(sample) {
  if (!els.motionPitch || !els.motionRoll || !els.motionWindow) return;
  if (!sample) {
    els.motionPitch.textContent = '—';
    els.motionRoll.textContent = '—';
    els.motionWindow.textContent = '—';
    return;
  }
  const { pitchDeg, rollDeg } = motionDeltas(sample);
  const fmt = (value) => `${value >= 0 ? '+' : ''}${value.toFixed(1)}°`;
  els.motionPitch.textContent = fmt(pitchDeg);
  els.motionRoll.textContent = fmt(rollDeg);
  const windowCount = Math.min(samples.length, 90);
  const hz = lastStatus?.sampleRateHz || 25;
  const seconds = windowCount / hz;
  els.motionWindow.textContent = `${windowCount} · ~${seconds.toFixed(1)}s`;
}

function beginSessionStats() {
  sessionStats = {
    startTime: Date.now(),
    endTime: null,
    durationSec: 0,
    sampleCount: 0,
    scores: [],
    states: { good: 0, warning: 0, slouch: 0 },
  };
}

function recordSessionSample(result) {
  if (!sessionStats || !result) return;
  sessionStats.sampleCount += 1;
  sessionStats.scores.push(result.score);
  if (result.state && result.state !== 'unknown') {
    sessionStats.states[result.state] = (sessionStats.states[result.state] || 0) + 1;
  }
}

function finalizeSessionStats() {
  if (!sessionStats) return null;
  sessionStats.endTime = Date.now();
  sessionStats.durationSec = (sessionStats.endTime - sessionStats.startTime) / 1000;
  const stats = sessionStats;
  sessionStats = null;
  return stats;
}

function renderHistory() {
  const store = window.UprightSessions;
  if (!store || !els.sessionHistory) return;

  const sessions = store.loadSessions();
  els.sessionHistory.replaceChildren();

  if (!sessions.length) {
    els.historyEmpty?.classList.remove('history-hidden');
    return;
  }

  els.historyEmpty?.classList.add('history-hidden');

  sessions.slice(0, 12).forEach((session) => {
    const li = document.createElement('li');
    li.className = 'session-item';
    const goodFlex = session.goodPct || 0;
    const warnFlex = session.warningPct || 0;
    const slouchFlex = session.slouchPct || 0;
    const barTotal = goodFlex + warnFlex + slouchFlex || 1;

    li.innerHTML = `
      <div class="session-item-head">
        <span class="session-item-when">${store.formatWhen(session.startedAt)}</span>
        <span class="session-item-duration">${store.formatDuration(session.durationSec)}</span>
      </div>
      <div class="session-item-stats">
        <span>Avg score</span><strong>${session.avgScore}</strong>
        <span>Samples</span><strong>${session.sampleCount}</strong>
        <span>Good</span><strong>${session.goodPct}%</strong>
        <span>Slouch</span><strong>${session.slouchPct}%</strong>
      </div>
      <div class="session-bar" aria-hidden="true">
        <span class="session-bar-good" style="flex:${goodFlex / barTotal}"></span>
        <span class="session-bar-warning" style="flex:${warnFlex / barTotal}"></span>
        <span class="session-bar-slouch" style="flex:${slouchFlex / barTotal || 0.001}"></span>
      </div>
    `;
    els.sessionHistory.appendChild(li);
  });
}

function safeDrawChart() {
  try {
    drawChart();
  } catch (error) {
    log(`Chart error: ${error.message}`);
  }
}

let chartFrameId = null;

function scheduleDrawChart() {
  if (chartFrameId != null) return;
  chartFrameId = requestAnimationFrame(() => {
    chartFrameId = null;
    safeDrawChart();
  });
}

function drawChart() {
  if (!els.canvas) return;
  const ctx = els.canvas.getContext('2d');
  if (!ctx) return;
  const rect = els.canvas.getBoundingClientRect();
  const dpr = window.devicePixelRatio || 1;
  const width = Math.max(300, Math.floor(rect.width * dpr));
  const height = Math.floor(240 * dpr);
  if (els.canvas.width !== width || els.canvas.height !== height) {
    els.canvas.width = width;
    els.canvas.height = height;
  }
  ctx.clearRect(0, 0, width, height);
  ctx.fillStyle = '#f4f4f5';
  ctx.fillRect(0, 0, width, height);

  const data = samples.slice(-90).map((sample) => motionDeltas(sample));
  if (data.length < 2) {
    ctx.fillStyle = '#71717a';
    ctx.font = `${14 * dpr}px system-ui`;
    ctx.fillText('Start a session to stream motion.', 20 * dpr, height / 2);
    updateMotionReadouts(samples[samples.length - 1] || null);
    return;
  }

  let maxAbs = 6;
  data.forEach((point) => {
    maxAbs = Math.max(maxAbs, Math.abs(point.pitchDeg), Math.abs(point.rollDeg));
  });
  const scale = maxAbs * 1.12;
  const midY = height / 2;
  const plotHeight = height * 0.42;

  const plot = (key, color) => {
    ctx.beginPath();
    ctx.strokeStyle = color;
    ctx.lineWidth = 2.5 * dpr;
    data.forEach((point, index) => {
      const x = (index / Math.max(1, data.length - 1)) * width;
      const y = midY - (point[key] / scale) * plotHeight;
      if (index === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.stroke();
  };

  ctx.strokeStyle = 'rgba(24, 24, 27, 0.12)';
  ctx.lineWidth = 1 * dpr;
  ctx.setLineDash([6 * dpr, 6 * dpr]);
  ctx.beginPath();
  ctx.moveTo(0, midY);
  ctx.lineTo(width, midY);
  ctx.stroke();
  ctx.setLineDash([]);

  plot('pitchDeg', '#0d9488');
  plot('rollDeg', '#d97706');

  ctx.fillStyle = '#a1a1aa';
  ctx.font = `${10 * dpr}px system-ui`;
  ctx.fillText(`+${scale.toFixed(0)}°`, 8 * dpr, 14 * dpr);
  ctx.fillText('0°', 8 * dpr, midY - 4 * dpr);
  ctx.fillText(`−${scale.toFixed(0)}°`, 8 * dpr, height - 6 * dpr);

  ctx.fillStyle = '#0d9488';
  ctx.font = `${11 * dpr}px system-ui`;
  ctx.fillText('Pitch Δ', 56 * dpr, 14 * dpr);
  ctx.fillStyle = '#d97706';
  ctx.fillText('Roll Δ', 120 * dpr, 14 * dpr);

  updateMotionReadouts(samples[samples.length - 1]);
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
    await refreshStatus();
    let status = lastStatus;
    if (!status) {
      status = await withTimeout(bridge.headphones.getStatus(), 5000, 'getStatus');
      setStatus(status);
    }
    if (status.permission !== 'granted') {
      log('Requesting motion permission…');
      const permission = await withTimeout(bridge.headphones.requestPermission(), 10000, 'requestPermission');
      log(`Permission result: ${permission || 'unknown'}`);
      await refreshStatus();
      status = lastStatus || status;
    }
    if (status.connection === 'disconnected') {
      if (status.deviceMotionAvailable) {
        log('Headphones detected. Tap Start Session to begin tracking.');
      } else {
        log('Wear supported AirPods in your ears, then tap Start Session.');
      }
    }
    await withTimeout(bridge.headphones.startUpdates({ sampleRateHz: 25 }), 5000, 'startUpdates');
    sessionActive = true;
    beginSessionStats();
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

  const stats = finalizeSessionStats();
  if (stats && stats.sampleCount >= 5) {
    window.UprightSessions?.addSession(stats);
    renderHistory();
    log(`Session saved · ${stats.sampleCount} samples · avg ${Math.round(stats.scores.reduce((a, b) => a + b, 0) / stats.scores.length)}`);
  } else {
    log('Session stopped.');
  }
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
    const connection = status.connection || 'unknown';
    if (connection !== lastLoggedConnection) {
      lastLoggedConnection = connection;
      log(`Status: ${connection} / ${status.permission || 'unknown'}`);
    }
  });
  bridge.on('interruption', (payload) => log(`Interruption: ${payload.reason}`));
  bridge.on('error', (payload) => log(`Error: ${payload.code} — ${payload.message}`));
}

async function handleMotion(sample) {
  samples.push({ pitch: sample.attitude.pitch, roll: sample.attitude.roll, ts: sample.ts });
  if (samples.length > 240) samples.shift();
  const result = engine.update(sample);
  recordSessionSample(result);
  setPosture(result);
  els.sampleCount.textContent = `${samples.length} samples`;
  scheduleDrawChart();
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
  safeDrawChart();
}

async function boot() {
  if (bootPromise) return bootPromise;
  bootPromise = bootInternal();
  return bootPromise;
}

async function bootInternal() {
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
    if (lastStatus) {
      const ready = lastStatus.deviceMotionAvailable ? 'yes' : 'no';
      log(`Motion ready: ${ready}`);
    }
    log(bridge.isNative ? 'Native bridge ready.' : 'Mock bridge ready.');
    booted = true;
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
      log('Fell back to mock bridge.');
    } catch (fallbackError) {
      log(`Fallback failed: ${fallbackError.message}`);
    }
  } finally {
    safeDrawChart();
    renderHistory();
  }
}

$('#startBtn').addEventListener('click', startSession);
$('#stopBtn').addEventListener('click', stopSession);
$('#permissionBtn').addEventListener('click', async () => {
  if (lastStatus?.permission === 'granted') {
    log('Motion permission already granted.');
    return;
  }
  try {
    log('Requesting motion permission…');
    const permission = await withTimeout(bridge.headphones.requestPermission(), 10000, 'requestPermission');
    await refreshStatus();
    log(`Permission result: ${permission || lastStatus?.permission || 'unknown'}`);
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
  updateMotionReadouts(null);
  safeDrawChart();
});
$('#clearLogBtn').addEventListener('click', () => els.log?.replaceChildren());
$('#clearHistoryBtn')?.addEventListener('click', () => {
  window.UprightSessions?.clearSessions();
  renderHistory();
  log('Session history cleared.');
});
document.addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'visible' && bridge) {
    refreshStatus().catch(() => {});
  }
});
window.addEventListener('resize', safeDrawChart);

async function showApp() {
  $('#landingView')?.classList.add('hidden');
  $('#appView')?.classList.remove('hidden');
  await boot();
  requestAnimationFrame(safeDrawChart);
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
