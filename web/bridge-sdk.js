const handlers = window.webkit?.messageHandlers;
const nativeHandler = handlers?.nativeBridgeWithReply || handlers?.nativeBridge;

class UprightNativeBridge {
  constructor() {
    this.listeners = new Map();
    this.nativeHandler = nativeHandler || null;
  }

  get isNative() {
    return Boolean(this.nativeHandler);
  }

  async call(module, method, params = {}) {
    if (!this.nativeHandler) {
      throw new Error('Native bridge unavailable; running in browser mock mode.');
    }
    return this.nativeHandler.postMessage({ module, method, params });
  }

  async ready() {
    return this.call('app', 'ready');
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
}

const bridge = new UprightNativeBridge();
window.UprightBridge = bridge;
window.__nativeBridge = bridge;
window.__dispatchNativeEvent = (event, payload) => bridge._emit(event, payload);
