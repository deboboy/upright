# Bridge Contract

API version: `1`

## Request schema

```json
{ "id": "req_123", "module": "headphones", "method": "startUpdates", "params": { "sampleRateHz": 25 } }
```

## Response shape

Promise resolves to the method result, or rejects/returns an error string from native.

## Status

```ts
type PermissionState = 'unknown' | 'granted' | 'denied' | 'restricted';
type ConnectionState = 'unavailable' | 'disconnected' | 'connected' | 'active';

type HeadphoneStatus = {
  platform: 'ios-native-shell';
  apiVersion: '1';
  supported: boolean;
  permission: PermissionState;
  connection: ConnectionState;
  deviceMotionAvailable: boolean;
  deviceName?: string;
  sampleRateHz?: number;
};
```

## Motion sample

```ts
type MotionSample = {
  ts: number;
  source: 'airpods';
  attitude: { pitch: number; roll: number; yaw: number };
  quaternion?: { x: number; y: number; z: number; w: number };
  rotationRate?: { x: number; y: number; z: number };
  gravity?: { x: number; y: number; z: number };
  userAcceleration?: { x: number; y: number; z: number };
};
```

## Events

```json
{ "type": "status", "payload": { "connection": "connected", "permission": "granted" } }
{ "type": "motion", "payload": { "ts": 1718910000000, "source": "airpods", "attitude": { "pitch": 0.08, "roll": -0.03, "yaw": 0.11 } } }
{ "type": "interruption", "payload": { "reason": "airpods_disconnected" } }
{ "type": "error", "payload": { "code": "permission_denied", "message": "Headphone motion permission denied" } }
```
