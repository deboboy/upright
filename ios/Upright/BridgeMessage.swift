import Foundation

struct BridgeRequest {
    let id: String
    let module: String
    let method: String
    let params: [String: Any]

    init?(body: Any) {
        guard let dict = body as? [String: Any],
              let id = dict["id"] as? String,
              let module = dict["module"] as? String,
              let method = dict["method"] as? String else {
            return nil
        }
        self.id = id
        self.module = module
        self.method = method
        self.params = dict["params"] as? [String: Any] ?? [:]
    }
}

struct BridgeEvent {
    let type: String
    let payload: [String: Any]
}
