import Foundation

enum BridgeError: Error, LocalizedError {
    case invalidRequest(String)
    case permissionDenied
    case unsupportedDevice
    case motionUnavailable
    case alreadyActive
    case notStarted
    case unknown(String)

    var code: String {
        switch self {
        case .invalidRequest: return "invalid_request"
        case .permissionDenied: return "permission_denied"
        case .unsupportedDevice: return "unsupported_device"
        case .motionUnavailable: return "motion_unavailable"
        case .alreadyActive: return "already_active"
        case .notStarted: return "not_started"
        case .unknown: return "unknown"
        }
    }

    var errorDescription: String? {
        switch self {
        case .invalidRequest(let message): return message
        case .permissionDenied: return "Headphone motion permission denied"
        case .unsupportedDevice: return "Supported AirPods are not connected"
        case .motionUnavailable: return "Headphone motion is temporarily unavailable"
        case .alreadyActive: return "Motion updates are already active"
        case .notStarted: return "Motion updates have not started"
        case .unknown(let message): return message
        }
    }
}
