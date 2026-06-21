import AVFAudio
import Foundation
import UIKit
import WebKit

final class NativeBridge: NSObject {
    weak var webView: WKWebView?
    private let adapter: HeadphoneMotionAdapter
    private var observers: [NSObjectProtocol] = []
    private var active = false

    init(adapter: HeadphoneMotionAdapter) {
        self.adapter = adapter
        super.init()
        installObservers()
    }

    deinit {
        observers.forEach { NotificationCenter.default.removeObserver($0) }
        adapter.stopUpdates()
    }

    func install(in configuration: WKWebViewConfiguration) {
        configuration.preferences.javaScriptEnabled = true
        if #available(iOS 14.0, *) {
            configuration.userContentController.add(self, contentWorld: .page, name: "nativeBridgeWithReply")
        } else {
            configuration.userContentController.add(self, name: "nativeBridge")
        }
    }

    func handle(_ request: BridgeRequest, replyHandler: @escaping (Any?, String?) -> Void) {
        switch (request.module, request.method) {
        case ("app", "ready"):
            reply(["platform": "ios-native-shell", "apiVersion": "1"], replyHandler)
        case ("headphones", "getStatus"):
            reply(statusDictionary(), replyHandler)
        case ("headphones", "requestPermission"):
            requestPermission(replyHandler)
        case ("headphones", "startUpdates"):
            startUpdates(request.params, replyHandler)
        case ("headphones", "stopUpdates"):
            adapter.stopUpdates()
            active = false
            dispatchStatus()
            reply(NSNull(), replyHandler)
        case ("headphones", "calibrateNeutral"):
            switch adapter.calibrateNeutral() {
            case .success(let neutral): reply(["ok": true, "neutral": neutral], replyHandler)
            case .failure(let error): reply(error, replyHandler)
            }
        case ("app", "haptic"):
            haptic(request.params)
            reply(NSNull(), replyHandler)
        case ("app", "speak"):
            speak(request.params)
            reply(NSNull(), replyHandler)
        case ("app", "openSettings"):
            openSettings()
            reply(NSNull(), replyHandler)
        case ("app", "log"):
            if let event = request.params["event"] { print("Upright event:", event) }
            reply(NSNull(), replyHandler)
        default:
            reply(BridgeError.invalidRequest("Unknown bridge method \(request.module).\(request.method)"), replyHandler)
        }
    }

    private func requestPermission(_ replyHandler: @escaping (Any?, String?) -> Void) {
        adapter.requestPermission { [weak self] status in
            guard let self else {
                replyHandler(nil, "Bridge deallocated")
                return
            }
            self.dispatchStatus()
            replyHandler(self.permissionString(for: status), nil)
        }
    }

    private func startUpdates(_ params: [String: Any], _ replyHandler: @escaping (Any?, String?) -> Void) {
        guard !active else {
            reply(BridgeError.alreadyActive, replyHandler)
            return
        }
        let sampleRate = params["sampleRateHz"] as? Int ?? 25
        adapter.startUpdates(sampleRateHz: sampleRate) { [weak self] sample in
            self?.dispatch(BridgeEvent(type: "motion", payload: sample.dictionary()))
        } onError: { [weak self] error in
            self?.active = false
            self?.dispatch(BridgeEvent(type: "error", payload: ["code": error.code, "message": error.localizedDescription ?? error.code]))
            reply(error, replyHandler)
        }
        active = true
        dispatchStatus()
        reply(NSNull(), replyHandler)
    }

    private func statusDictionary() -> [String: Any] {
        [
            "platform": "ios-native-shell",
            "apiVersion": "1",
            "supported": adapter.isDeviceMotionAvailable,
            "permission": permissionString(for: adapter.authorizationStatus),
            "connection": connectionState(),
            "deviceMotionAvailable": adapter.isDeviceMotionAvailable,
            "deviceName": deviceName(),
            "sampleRateHz": adapter.sampleRateHz ?? NSNull()
        ]
    }

    private func dispatchStatus() {
        dispatch(BridgeEvent(type: "status", payload: statusDictionary()))
    }

    private func dispatch(_ event: BridgeEvent) {
        guard let typeJSON = try? JSONSerialization.data(withJSONObject: event.type),
              let typeString = String(data: typeJSON, encoding: .utf8),
              let payloadJSON = try? JSONSerialization.data(withJSONObject: event.payload),
              let payloadString = String(data: payloadJSON, encoding: .utf8) else {
            return
        }
        webView?.evaluateJavaScript("window.__dispatchNativeEvent(\(typeString), \(payloadString))", completionHandler: nil)
    }

    private func reply(_ value: Any?, _ replyHandler: @escaping (Any?, String?) -> Void) {
        replyHandler(value, nil)
    }

    private func reply(_ error: BridgeError, _ replyHandler: @escaping (Any?, String?) -> Void) {
        replyHandler(nil, error.localizedDescription ?? error.code)
    }

    private func permissionString(for status: CMAuthorizationStatus) -> String {
        switch status {
        case .notDetermined: return "unknown"
        case .authorized: return "granted"
        case .denied: return "denied"
        case .restricted: return "restricted"
        @unknown default: return "unknown"
        }
    }

    private func connectionState() -> String {
        let hasBluetoothOutput = AVAudioSession.sharedInstance().currentRoute.outputs.contains { output in
            output.portType == .bluetoothA2DP || output.portType == .bluetoothLE
        }
        if active && adapter.isDeviceMotionActive && (hasBluetoothOutput || managerIsConnectionActive()) { return "active" }
        if hasBluetoothOutput || managerIsConnectionActive() { return "connected" }
        return "disconnected"
    }

    private func managerIsConnectionActive() -> Bool {
        if #available(iOS 15.0, *) {
            return adapter.isConnectionStatusActive
        }
        return false
    }

    private func deviceName() -> String? {
        let outputs = AVAudioSession.sharedInstance().currentRoute.outputs
        if let airPods = outputs.first(where: { $0.portName.lowercased().contains("airpods") }) {
            return airPods.portName
        }
        if let bluetooth = outputs.first(where: { $0.portType == .bluetoothA2DP || $0.portType == .bluetoothLE }) {
            return bluetooth.portName.isEmpty ? bluetooth.portType.rawValue : bluetooth.portName
        }
        return nil
    }

    private func haptic(_ params: [String: Any]) {
        let kind = params["kind"] as? String ?? "subtle"
        let style: UIImpactFeedbackGenerator.FeedbackStyle = kind == "alert" ? .heavy : .light
        UIImpactFeedbackGenerator(style: style).impactOccurred()
    }

    private func speak(_ params: [String: Any]) {
        guard let text = params["text"] as? String, !text.isEmpty else { return }
        let synthesizer = AVSpeechSynthesizer()
        let utterance = AVSpeechUtterance(string: text)
        utterance.rate = AVSpeechUtteranceDefaultSpeechRate
        synthesizer.speak(utterance)
    }

    private func openSettings() {
        guard let url = URL(string: UIApplication.openSettingsURLString) else { return }
        UIApplication.shared.open(url)
    }

    private func installObservers() {
        observers.append(NotificationCenter.default.addObserver(forName: AVAudioSession.routeChangeNotification, object: nil, queue: .main) { [weak self] _ in
            guard let self else { return }
            if self.connectionState() == "disconnected" && self.active {
                self.adapter.stopUpdates()
                self.active = false
                self.dispatch(BridgeEvent(type: "interruption", payload: ["reason": "airpods_disconnected"]))
            }
            self.dispatchStatus()
        })
        observers.append(NotificationCenter.default.addObserver(forName: UIApplication.willResignActiveNotification, object: nil, queue: .main) { [weak self] _ in
            guard let self, self.active else { return }
            self.adapter.stopUpdates()
            self.active = false
            self.dispatch(BridgeEvent(type: "interruption", payload: ["reason": "app_backgrounded"]))
            self.dispatchStatus()
        })
        observers.append(NotificationCenter.default.addObserver(forName: UIApplication.didBecomeActiveNotification, object: nil, queue: .main) { [weak self] _ in
            self?.dispatchStatus()
        })
    }
}

extension NativeBridge: WKScriptMessageHandlerWithReply {
    func userContentController(_ userContentController: WKUserContentController, didReceive message: WKScriptMessage) {
        guard let request = BridgeRequest(body: message.body) else {
            replyHandlerForLegacy(message)
            return
        }
        handle(request) { value, error in
            if let error {
                self.dispatch(BridgeEvent(type: "error", payload: ["code": "native_error", "message": error]))
            }
        }
    }

    @available(iOS 14.0, *)
    func userContentController(
        _ userContentController: WKUserContentController,
        didReceive message: WKScriptMessage,
        replyHandler: @escaping (Any?, String?) -> Void
    ) {
        guard let request = BridgeRequest(body: message.body) else {
            replyHandler(nil, "Invalid bridge request")
            return
        }
        handle(request, replyHandler: replyHandler)
    }

    private func replyHandlerForLegacy(_ message: WKScriptMessage) {
        dispatch(BridgeEvent(type: "error", payload: ["code": "invalid_request", "message": "Invalid bridge request"]))
    }
}
