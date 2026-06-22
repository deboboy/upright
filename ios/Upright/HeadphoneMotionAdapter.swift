import AVFAudio
import CoreMotion
import Foundation

final class HeadphoneMotionAdapter: NSObject, CMHeadphoneMotionManagerDelegate {
    private let manager = CMHeadphoneMotionManager()
    private let queue = OperationQueue()
    private let sampleQueue = DispatchQueue(label: "com.lastmyle.upright.headphone-samples")
    private var motionHandler: ((MotionSample) -> Void)?
    private var errorHandler: ((BridgeError) -> Void)?
    private var recentSamples: [MotionSample] = []
    private var currentSampleRateHz: Int = 25
    private var lastSampleTime: TimeInterval = 0
    private var delegateConnected = false

    var onConnectionChange: (() -> Void)?

    override init() {
        super.init()
        manager.delegate = self
        if #available(iOS 15.0, *) {
            manager.startConnectionStatusUpdates()
        }
        refreshConnectionEstimate()
    }

    deinit {
        if #available(iOS 15.0, *) {
            manager.stopConnectionStatusUpdates()
        }
    }

    func refreshConnectionEstimate() {
        if manager.isDeviceMotionAvailable {
            delegateConnected = true
        }
    }

    var authorizationStatus: CMAuthorizationStatus {
        CMHeadphoneMotionManager.authorizationStatus()
    }

    var isDeviceMotionAvailable: Bool {
        manager.isDeviceMotionAvailable
    }

    var isDeviceMotionActive: Bool {
        manager.isDeviceMotionActive
    }

    var isHeadphonesConnected: Bool {
        refreshConnectionEstimate()
        if delegateConnected { return true }
        if manager.isDeviceMotionAvailable { return true }
        return Self.hasBluetoothHeadphonesInAudioRoute()
    }

    var connectedDeviceName: String? {
        if let name = Self.bluetoothDeviceNameFromAudioRoute() {
            return name
        }
        if manager.isDeviceMotionAvailable {
            return "AirPods"
        }
        return nil
    }

    var sampleRateHz: Int? {
        isDeviceMotionActive ? currentSampleRateHz : nil
    }

    func headphoneMotionManagerDidConnect(_ manager: CMHeadphoneMotionManager) {
        delegateConnected = true
        notifyConnectionChange()
    }

    func headphoneMotionManagerDidDisconnect(_ manager: CMHeadphoneMotionManager) {
        delegateConnected = false
        notifyConnectionChange()
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

        if manager.isDeviceMotionActive {
            manager.stopDeviceMotionUpdates()
        }

        motionHandler = onMotion
        errorHandler = onError
        currentSampleRateHz = max(1, sampleRateHz)
        lastSampleTime = 0

        manager.startDeviceMotionUpdates(to: queue) { [weak self] motion, error in
            guard let self else { return }
            if let error {
                DispatchQueue.main.async {
                    onError(.unknown(error.localizedDescription))
                }
                return
            }
            guard let motion else { return }

            let now = Date().timeIntervalSince1970
            let minInterval = 1.0 / Double(self.currentSampleRateHz)
            if now - self.lastSampleTime < minInterval {
                return
            }
            self.lastSampleTime = now

            let sample = MotionSample.from(motion)
            self.sampleQueue.async {
                self.recentSamples.append(sample)
                if self.recentSamples.count > 80 {
                    self.recentSamples.removeFirst(self.recentSamples.count - 80)
                }
                DispatchQueue.main.async {
                    onMotion(sample)
                }
            }
        }
    }

    func stopUpdates() {
        manager.stopDeviceMotionUpdates()
        motionHandler = nil
        errorHandler = nil
        lastSampleTime = 0
    }

    func calibrateNeutral() -> Result<[String: Double], BridgeError> {
        let usable = sampleQueue.sync {
            Array(recentSamples.suffix(40))
        }
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

    private func notifyConnectionChange() {
        if Thread.isMainThread {
            onConnectionChange?()
        } else {
            DispatchQueue.main.async { [weak self] in
                self?.onConnectionChange?()
            }
        }
    }

    private static func audioPorts() -> [AVAudioSessionPortDescription] {
        let session = AVAudioSession.sharedInstance()
        return session.currentRoute.outputs + session.currentRoute.inputs
    }

    private static func isBluetoothPort(_ port: AVAudioSessionPortDescription) -> Bool {
        switch port.portType {
        case .bluetoothA2DP, .bluetoothLE, .bluetoothHFP, .headphones, .headsetMic:
            return true
        default:
            let name = port.portName.lowercased()
            let type = port.portType.rawValue.lowercased()
            return name.contains("airpods") || name.contains("beats") || type.contains("bluetooth")
        }
    }

    static func hasBluetoothHeadphonesInAudioRoute() -> Bool {
        audioPorts().contains(where: isBluetoothPort)
    }

    static func bluetoothDeviceNameFromAudioRoute() -> String? {
        let ports = audioPorts()
        if let airPods = ports.first(where: { $0.portName.lowercased().contains("airpods") }) {
            return airPods.portName
        }
        if let bluetooth = ports.first(where: isBluetoothPort) {
            return bluetooth.portName.isEmpty ? bluetooth.portType.rawValue : bluetooth.portName
        }
        return nil
    }
}
