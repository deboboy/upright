import AVFAudio
import CoreMotion
import Foundation

final class HeadphoneMotionAdapter {
    private let manager = CMHeadphoneMotionManager()
    private let queue = OperationQueue()
    private var motionHandler: ((MotionSample) -> Void)?
    private var errorHandler: ((BridgeError) -> Void)?
    private var recentSamples: [MotionSample] = []
    private var currentSampleRateHz: Int = 25

    var authorizationStatus: CMAuthorizationStatus {
        CMHeadphoneMotionManager.authorizationStatus()
    }

    var isDeviceMotionAvailable: Bool {
        manager.isDeviceMotionAvailable
    }

    var isDeviceMotionActive: Bool {
        manager.isDeviceMotionActive
    }

    var isConnectionStatusActive: Bool {
        if #available(iOS 15.0, *) {
            return manager.isConnectionStatusActive
        }
        return false
    }

    var sampleRateHz: Int? {
        isDeviceMotionActive ? currentSampleRateHz : nil
    }

    func requestPermission(completion: @escaping (CMAuthorizationStatus) -> Void) {
        guard authorizationStatus == .notDetermined else {
            completion(authorizationStatus)
            return
        }

        let timeout = DispatchWorkItem { [weak self] in
            self?.manager.stopDeviceMotionUpdates()
            completion(CMHeadphoneMotionManager.authorizationStatus())
        }
        DispatchQueue.main.asyncAfter(deadline: .now() + 5, execute: timeout)

        manager.deviceMotionUpdateInterval = 1.0
        manager.startDeviceMotionUpdates(to: queue) { [weak self] _, _ in
            timeout.cancel()
            self?.manager.stopDeviceMotionUpdates()
            completion(CMHeadphoneMotionManager.authorizationStatus())
        }
    }

    func startUpdates(
        sampleRateHz: Int = 25,
        onMotion: @escaping (MotionSample) -> Void,
        onError: @escaping (BridgeError) -> Void
    ) {
        guard authorizationStatus == .authorized else {
            onError(.permissionDenied)
            return
        }
        guard manager.isDeviceMotionAvailable else {
            onError(.motionUnavailable)
            return
        }

        motionHandler = onMotion
        errorHandler = onError
        currentSampleRateHz = max(1, sampleRateHz)
        manager.deviceMotionUpdateInterval = 1.0 / Double(currentSampleRateHz)

        manager.startDeviceMotionUpdates(to: queue) { [weak self] motion, error in
            guard let self else { return }
            if let error {
                onError(.unknown(error.localizedDescription))
                return
            }
            guard let motion else { return }
            let sample = MotionSample.from(motion)
            self.recentSamples.append(sample)
            if self.recentSamples.count > 80 {
                self.recentSamples.removeFirst(self.recentSamples.count - 80)
            }
            onMotion(sample)
        }
    }

    func stopUpdates() {
        manager.stopDeviceMotionUpdates()
        motionHandler = nil
        errorHandler = nil
    }

    func calibrateNeutral() -> BridgeError.Result<[String: Double]> {
        let usable = recentSamples.suffix(40)
        guard !usable.isEmpty else {
            return .success(["pitch": 0, "roll": 0, "yaw": 0])
        }
        var pitch = 0.0
        var roll = 0.0
        var yaw = 0.0
        for sample in usable {
            pitch += sample.attitude.pitch
            roll += sample.attitude.roll
            yaw += sample.attitude.yaw
        }
        let count = Double(usable.count)
        return .success(["pitch": pitch / count, "roll": roll / count, "yaw": yaw / count])
    }
}

extension HeadphoneMotionAdapter {
    enum Result<Value> {
        case success(Value)
        case failure(BridgeError)
    }
}
