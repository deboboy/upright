import CoreMotion
import Foundation

struct Vector3: Codable {
    let x: Double
    let y: Double
    let z: Double

    func dictionary() -> [String: Any] {
        ["x": x, "y": y, "z": z]
    }
}

struct Attitude: Codable {
    let pitch: Double
    let roll: Double
    let yaw: Double

    func dictionary() -> [String: Any] {
        ["pitch": pitch, "roll": roll, "yaw": yaw]
    }
}

struct Quaternion: Codable {
    let x: Double
    let y: Double
    let z: Double
    let w: Double

    func dictionary() -> [String: Any] {
        ["x": x, "y": y, "z": z, "w": w]
    }
}

struct MotionSample: Codable {
    let ts: TimeInterval
    let source: String
    let attitude: Attitude
    let quaternion: Quaternion?
    let rotationRate: Vector3?
    let gravity: Vector3?
    let userAcceleration: Vector3?

    func dictionary() -> [String: Any] {
        var result: [String: Any] = [
            "ts": ts,
            "source": source,
            "attitude": attitude.dictionary()
        ]
        if let quaternion { result["quaternion"] = quaternion.dictionary() }
        if let rotationRate { result["rotationRate"] = rotationRate.dictionary() }
        if let gravity { result["gravity"] = gravity.dictionary() }
        if let userAcceleration { result["userAcceleration"] = userAcceleration.dictionary() }
        return result
    }

    static func from(_ motion: CMDeviceMotion) -> MotionSample {
        let attitude = motion.attitude
        let rotation = motion.rotationRate
        let gravity = motion.gravity
        let acceleration = motion.userAcceleration
        return MotionSample(
            ts: Date().timeIntervalSince1970 * 1000,
            source: "airpods",
            attitude: Attitude(pitch: attitude.pitch, roll: attitude.roll, yaw: attitude.yaw),
            quaternion: Quaternion(x: motion.attitude.quaternion.x, y: motion.attitude.quaternion.y, z: motion.attitude.quaternion.z, w: motion.attitude.quaternion.w),
            rotationRate: Vector3(x: rotation.x, y: rotation.y, z: rotation.z),
            gravity: Vector3(x: gravity.x, y: gravity.y, z: gravity.z),
            userAcceleration: Vector3(x: acceleration.x, y: acceleration.y, z: acceleration.z)
        )
    }
}
