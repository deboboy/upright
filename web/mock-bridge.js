import { radiansToDegrees } from './posture-core.js';

const fallbackSamples = Array.from({ length: 40 }, (_, index) => {
  const t = index / 39;
  return {
    ts: Date.now() + index * 250,
    source: 'airpods-mock',
    attitude: {
      pitch: 0.02 + Math.sin(t * Math.PI * 2) * 0.025 + t * 0.16,
      roll: -0.01 + Math.cos(t * Math.PI * 2) * 0.018,
      yaw: 0.03 + Math.sin(t * Math.PI) * 0.02,
    },
    gravity: { x: 0, y: Math.sin(t), z: -1 },
  };
});

export class UprightMockBridge {
  constructor(traces = fallbackSamples) {
    this.listeners = new Map();
    this.traces = Array.isArray(traces) ? traces : fallbackSamples;
    this.index = 0;
    this.timer = null;
    this.active = false;
    this.status = {
      platform: 'browser-mock',
      apiVersion: '1',
      supported: true,
      permission: 'granted',
      connection: 'connected',
      deviceMotionAvailable: true,
      deviceName: 'Mock AirPods Trace',
      sampleRateHz: 25,
    };
  }

  get isNative() { return false; }

  async ready() { return { platform: 'browser-mock', apiVersion: '1' }; }

  async call(module, method, params = {}) {
    if (module === 'headphones' && method === 'getStatus') return this.status;
    if (module === 'headphones' && method === 'requestPermission') return this.status.permission;
    if (module === 'headphones' && method === 'startUpdates') return this.startUpdates(params);
    if (module === 'headphones' && method === 'stopUpdates') return this.stopUpdates();
    if (module === 'headphones' && method === 'calibrateNeutral') return { ok: true, neutral: { pitch: 0.02, roll: -0.01, yaw: 0.03 } };
    if (module === 'app' && method === 'ready') return this.ready();
    if (module === 'app' && method === 'haptic') return navigator.vibrate?.(18);
    if (module === 'app' && method === 'speak') return undefined;
    if (module === 'app' && method === 'openSettings') return undefined;
    if (module === 'app' && method === 'log') return undefined;
    throw new Error(`Mock bridge does not implement ${module}.${method}`);
  }

  get headphones() {
    return {
      getStatus: () => this.call('headphones', 'getStatus'),
      requestPermission: () => this.call('headphones', 'requestPermission'),
      startUpdates: (opts = {}) => this.call('headphones', 'startUpdates', opts),
      stopUpdates: () => this.call('headphones', 'stopUpdates'),
      calibrateNeutral: () => this.call('headphones', 'calibrateNeutral'),
    };
  }

  get app() {
    return {
      haptic: (kind = 'subtle') => this.call('app', 'haptic', { kind }),
      speak: (text) => this.call('app', 'speak', { text }),
      openSettings: () => this.call('app', 'openSettings'),
      log: (event, payload = {}) => this.call('app', 'log', { event, payload }),
    };
  }

  on(event, callback) {
    if (!this.listeners.has(event)) this.listeners.set(event, new Set());
    this.listeners.get(event).add(callback);
    return () => this.listeners.get(event)?.delete(callback);
  }

  _emit(event, payload) {
    this.listeners.get(event)?.forEach((callback) => callback(payload));
    window.dispatchEvent(new CustomEvent(`upright:${event}`, { detail: payload }));
  }

  async startUpdates(opts = {}) {
    if (this.active) return;
    this.active = true;
    this.status.connection = 'active';
    this.status.sampleRateHz = opts.sampleRateHz || 25;
    this._emit('status', this.status);
    const interval = Math.max(40, Math.round(1000 / this.status.sampleRateHz));
    this.timer = setInterval(() => this.tick(), interval);
    this.tick();
  }

  stopUpdates() {
    this.active = false;
    if (this.timer) clearInterval(this.timer);
    this.timer = null;
    this.status.connection = 'connected';
    this._emit('status', this.status);
  }

  tick() {
    const sample = this.traces[this.index % this.traces.length];
    this.index += 1;
    this._emit('motion', { ...sample, ts: Date.now() });
  }
}

export async function createMockBridge() {
  try {
    const response = await fetch('./mock-traces.json', { cache: 'no-store' });
    if (!response.ok) throw new Error('mock trace fetch failed');
    const json = await response.json();
    return new UprightMockBridge(json.samples || json);
  } catch (error) {
    console.warn('Using embedded mock motion trace.', error);
    return new UprightMockBridge();
  }
}
