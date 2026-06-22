(function () {
  function clamp(value, min, max) {
    return Math.min(max, Math.max(min, value));
  }

  function radiansToDegrees(value) {
    return value * 180 / Math.PI;
  }

  class PostureEngine {
    constructor() {
      this.neutral = { pitch: 0, roll: 0, yaw: 0 };
      this.samples = [];
      this.state = 'unknown';
      this.score = 0;
      this.warningHigh = 55;
      this.slouchHigh = 72;
      this.warningLow = 35;
    }

    calibrate(samples = this.samples) {
      const usable = samples.slice(-40);
      if (!usable.length) return this.neutral;
      const avg = usable.reduce((acc, sample) => {
        acc.pitch += sample.attitude.pitch;
        acc.roll += sample.attitude.roll;
        acc.yaw += sample.attitude.yaw;
        return acc;
      }, { pitch: 0, roll: 0, yaw: 0 });
      const count = usable.length;
      this.neutral = {
        pitch: avg.pitch / count,
        roll: avg.roll / count,
        yaw: avg.yaw / count,
      };
      return this.neutral;
    }

    update(sample) {
      this.samples.push(sample);
      if (this.samples.length > 180) this.samples.shift();

      const pitchDelta = sample.attitude.pitch - this.neutral.pitch;
      const rollDelta = sample.attitude.roll - this.neutral.roll;
      const pitchPenalty = Math.abs(pitchDelta) * 160;
      const rollPenalty = Math.abs(rollDelta) * 80;
      const nextScore = clamp(pitchPenalty + rollPenalty, 0, 100);
      this.score = Math.round(nextScore);

      if (this.state === 'unknown') {
        this.state = nextScore >= this.slouchHigh ? 'slouch' : nextScore >= this.warningHigh ? 'warning' : 'good';
      } else if (this.state === 'good' && nextScore >= this.warningHigh) {
        this.state = 'warning';
      } else if (this.state === 'warning' && nextScore >= this.slouchHigh) {
        this.state = 'slouch';
      } else if (this.state === 'slouch' && nextScore < this.warningLow) {
        this.state = 'warning';
      } else if (this.state === 'warning' && nextScore < this.warningLow) {
        this.state = 'good';
      }

      return {
        state: this.state,
        score: this.score,
        neutral: this.neutral,
        pitchDegrees: radiansToDegrees(sample.attitude.pitch),
        rollDegrees: radiansToDegrees(sample.attitude.roll),
        yawDegrees: radiansToDegrees(sample.attitude.yaw),
      };
    }

    recent(count = 80) {
      return this.samples.slice(-count);
    }
  }

  window.UprightPosture = { clamp, radiansToDegrees, PostureEngine };
})();
