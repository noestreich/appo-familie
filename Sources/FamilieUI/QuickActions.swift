#if canImport(UIKit)
import UIKit

/// Quick Actions beim langen Druck aufs App-Symbol (iOS zeigt höchstens vier eigene).
///
/// Die App trägt ihre Einträge in `UIApplicationShortcutItems` ein, setzt `QuickActions.handler` im `init` ihrer
/// `App` und gibt in ihrem AppDelegate `QuickActions.sceneConfiguration(for:options:)` zurück. So kommt eine
/// Aktion beim Kaltstart (mit den Verbindungsoptionen der Szene) und bei laufender App (Szenen-Delegate) an.
@MainActor
public enum QuickActions {
    /// Bekommt den Typ (`UIApplicationShortcutItemType`) und liefert `true`, wenn die App ihn kennt.
    public static var handler: @MainActor (String) -> Bool = { _ in false }

    public static func sceneConfiguration(for session: UISceneSession, options: UIScene.ConnectionOptions) -> UISceneConfiguration {
        if let item = options.shortcutItem { perform(item.type) }
        let configuration = UISceneConfiguration(name: nil, sessionRole: session.role)
        configuration.delegateClass = QuickActionSceneDelegate.self
        return configuration
    }

    @discardableResult
    public static func perform(_ type: String) -> Bool {
        handler(type)
    }
}

/// Quick Action, während die App schon läuft.
public final class QuickActionSceneDelegate: NSObject, UIWindowSceneDelegate {
    public func windowScene(_ windowScene: UIWindowScene, performActionFor shortcutItem: UIApplicationShortcutItem, completionHandler: @escaping (Bool) -> Void) {
        completionHandler(QuickActions.perform(shortcutItem.type))
    }
}
#endif
