import AVFAudio
import CoreMotion
import Foundation
import UIKit
@preconcurrency import WebKit

final class NativeBridge: NSObject {
    weak var webView: WKWebView?
    private let adapter: HeadphoneMotionAdapter
    private var observers: [NSObjectProtocol] = []
    private var active = false

    init(adapter: HeadphoneMotionAdapter) {
        self.adapter = adapter
        super.init()
        adapter.onConnectionChange = { [weak self] in
            self?.dispatchStatus()
        }
        installObservers()
    }

    deinit {
        observers.forEach { NotificationCenter.default.removeObserver($0) }
        adapter.stopUpdates()
    }

    func install(in configuration: WKWebViewConfiguration) {
        if #available(iOS 14.0, *) {
            configuration.defaultWebpagePreferences.allowsContentJavaScript = true
            configuration.userContentController.add(self, contentWorld: .page, name: "nativeBridgeWithReply")
        } else {
            configuration.preferences.javaScriptEnabled = true
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
                let respond = { replyHandler(nil, "Bridge deallocated") }
                if Thread.isMainThread {
                    respond()
                } else {
                    DispatchQueue.main.async(execute: respond)
                }
                return
            }
            self.dispatchStatus()
            let permission = self.permissionString(for: status)
            self.deliverReply(["permission": permission], error: nil, to: replyHandler)
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
            self?.dispatch(BridgeEvent(type: "error", payload: ["code": error.code, "message": error.errorDescription ?? error.code]))
            self?.reply(error, replyHandler)
        }
        active = true
        dispatchStatus()
        reply(NSNull(), replyHandler)
    }

    private func statusDictionary() -> [String: Any] {
        adapter.refreshConnectionEstimate()
        var status: [String: Any] = [
            "platform": "ios-native-shell",
            "apiVersion": "1",
            "supported": adapter.isDeviceMotionAvailable,
            "permission": permissionString(for: adapter.authorizationStatus),
            "connection": connectionState(),
            "deviceMotionAvailable": adapter.isDeviceMotionAvailable,
        ]
        if let name = deviceName() {
            status["deviceName"] = name
        }
        if let rate = adapter.sampleRateHz {
            status["sampleRateHz"] = rate
        }
        return status
    }

    private func dispatchStatus() {
        dispatch(BridgeEvent(type: "status", payload: statusDictionary()))
    }

    func pushInitialStatus() {
        dispatchStatus()
    }

    private func dispatch(_ event: BridgeEvent) {
        let emit = { [weak self] in
            guard let self,
                  let typeString = self.jsonStringLiteral(event.type),
                  let payloadString = self.jsonObjectLiteral(event.payload) else {
                return
            }
            self.webView?.evaluateJavaScript(
                "window.__dispatchNativeEvent(\(typeString), \(payloadString))",
                completionHandler: nil
            )
        }
        if Thread.isMainThread {
            emit()
        } else {
            DispatchQueue.main.async(execute: emit)
        }
    }

    private func jsonStringLiteral(_ string: String) -> String? {
        guard let data = try? JSONEncoder().encode(string) else { return nil }
        return String(data: data, encoding: .utf8)
    }

    private func jsonObjectLiteral(_ object: Any) -> String? {
        guard JSONSerialization.isValidJSONObject(object),
              let data = try? JSONSerialization.data(withJSONObject: object) else {
            return nil
        }
        return String(data: data, encoding: .utf8)
    }

    private func reply(_ value: Any?, _ replyHandler: @escaping (Any?, String?) -> Void) {
        deliverReply(value, error: nil, to: replyHandler)
    }

    private func reply(_ error: BridgeError, _ replyHandler: @escaping (Any?, String?) -> Void) {
        deliverReply(nil, error: error.errorDescription ?? error.code, to: replyHandler)
    }

    private func deliverReply(_ value: Any?, error: String?, to replyHandler: @escaping (Any?, String?) -> Void) {
        let respond = { replyHandler(value, error) }
        if Thread.isMainThread {
            respond()
        } else {
            DispatchQueue.main.async(execute: respond)
        }
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
        if active && adapter.isDeviceMotionActive {
            return "active"
        }
        if adapter.isHeadphonesConnected {
            return "connected"
        }
        return "disconnected"
    }

    private func deviceName() -> String? {
        adapter.connectedDeviceName
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

@available(iOS 14.0, *)
extension NativeBridge: WKScriptMessageHandlerWithReply {
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
}

extension NativeBridge: WKScriptMessageHandler {
    func userContentController(_ userContentController: WKUserContentController, didReceive message: WKScriptMessage) {
        guard let request = BridgeRequest(body: message.body) else {
            dispatch(BridgeEvent(type: "error", payload: ["code": "invalid_request", "message": "Invalid bridge request"]))
            return
        }
        handle(request) { _, error in
            if let error {
                self.dispatch(BridgeEvent(type: "error", payload: ["code": "native_error", "message": error]))
            }
        }
    }
}
