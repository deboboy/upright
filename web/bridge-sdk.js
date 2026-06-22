(function () {
  let requestId = 0;

  function getNativeHandler() {
    const handlers = window.webkit?.messageHandlers;
    return handlers?.nativeBridgeWithReply || handlers?.nativeBridge || null;
  }

  class UprightBridge {
    constructor() {
      this.listeners = new Map();
    }

    get nativeHandler() {
      return getNativeHandler();
    }

    get isNative() {
      return Boolean(this.nativeHandler);
    }

    async call(module, method, params = {}) {
      const handler = this.nativeHandler;
      if (!handler) {
        throw new Error('Native bridge unavailable; running in browser mock mode.');
      }
      const result = handler.postMessage({
        id: `req_${++requestId}`,
        module,
        method,
        params,
      });
      if (result && typeof result.then === 'function') {
        return result;
      }
      return result;
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

  window.UprightBridge = UprightBridge;
  window.__uprightBridgeInstance = null;
  window.__dispatchNativeEvent = (event, payload) => {
    window.__uprightBridgeInstance?._emit(event, payload);
  };
})();
