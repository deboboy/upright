(function () {
  const STORAGE_KEY = 'upright.sessions';
  const MAX_SESSIONS = 40;

  function loadSessions() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      const parsed = raw ? JSON.parse(raw) : [];
      return Array.isArray(parsed) ? parsed : [];
    } catch (_) {
      return [];
    }
  }

  function saveSessions(sessions) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(sessions.slice(0, MAX_SESSIONS)));
    } catch (_) {
      /* storage full or private mode */
    }
  }

  function formatDuration(seconds) {
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return `${m}:${s.toString().padStart(2, '0')}`;
  }

  function formatWhen(iso) {
    const date = new Date(iso);
    const today = new Date();
    const sameDay = date.toDateString() === today.toDateString();
    const time = date.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
    if (sameDay) return `Today · ${time}`;
    return `${date.toLocaleDateString([], { month: 'short', day: 'numeric' })} · ${time}`;
  }

  function summarizeSession(stats) {
    const scores = stats.scores || [];
    const count = scores.length;
    const avgScore = count ? Math.round(scores.reduce((a, b) => a + b, 0) / count) : 0;
    const peakScore = count ? Math.max(...scores) : 0;
    const states = stats.states || {};
    const stateTotal = (states.good || 0) + (states.warning || 0) + (states.slouch || 0);
    const pct = (key) => (stateTotal ? Math.round(((states[key] || 0) / stateTotal) * 100) : 0);

    return {
      id: `sess_${stats.startTime}`,
      startedAt: new Date(stats.startTime).toISOString(),
      endedAt: new Date(stats.endTime || Date.now()).toISOString(),
      durationSec: Math.max(0, Math.round((stats.durationSec || 0))),
      sampleCount: stats.sampleCount || count,
      avgScore,
      peakScore,
      goodPct: pct('good'),
      warningPct: pct('warning'),
      slouchPct: pct('slouch'),
    };
  }

  function addSession(stats) {
    const session = summarizeSession(stats);
    const sessions = loadSessions().filter((item) => item.id !== session.id);
    sessions.unshift(session);
    saveSessions(sessions);
    return session;
  }

  function clearSessions() {
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch (_) {
      /* ignore */
    }
  }

  window.UprightSessions = {
    loadSessions,
    addSession,
    clearSessions,
    formatDuration,
    formatWhen,
  };
})();
