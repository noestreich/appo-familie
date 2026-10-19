import SwiftUI
#if canImport(UIKit)
import UIKit
#elseif canImport(AppKit)
import AppKit
#endif

/// Die fünf Farbwelten der App-Familie, wählbar in den Einstellungen (DESIGN.md, „Farbe“).
/// Jede App startet mit ihrer eigenen Standard-Farbwelt (Kaufo Tomatenrot, Scanno Himbeere, Schreibo Ultramarin).
/// Die Einstellungen zeigen in allen Apps dieselbe Reihenfolge: `AppTheme.allCases`.
public enum AppTheme: String, CaseIterable, Identifiable, Sendable {
    case tomato
    case raspberry
    case ultramarine
    case herb
    case aubergine

    /// Schlüssel in den Einstellungen (App Group der App, damit Widget und Erweiterungen mitlesen).
    public static let storageKey = "theme"

    public var id: String { rawValue }

    public var title: String {
        switch self {
        case .raspberry: "Himbeere & Koralle"
        case .tomato: "Tomatenrot & Creme"
        case .herb: "Kräutergrün & Zitrone"
        case .ultramarine: "Ultramarin & Koralle"
        case .aubergine: "Aubergine & Minze"
        }
    }

    /// Hauptakzent: Haken, Buttons, Tint.
    public var accent: Color {
        switch self {
        case .raspberry: Color(light: 0xD63862, dark: 0xFF6B8F)
        case .tomato: Color(light: 0xE0442E, dark: 0xFF5F47)
        case .herb: Color(light: 0x23864F, dark: 0x3FBF72)
        case .ultramarine: Color(light: 0x2A3FD6, dark: 0x6B7CFF)
        case .aubergine: Color(light: 0x5E2B73, dark: 0xB27AD0)
        }
    }

    /// Zweitfarbe für den Blob-Verlauf und Hervorhebungen.
    public var partner: Color {
        switch self {
        case .raspberry: Color(light: 0xFF8A66, dark: 0xFF9A7A)
        case .tomato: Color(light: 0xFF8A3D, dark: 0xFF9A55)
        case .herb: Color(light: 0xF2CF2E, dark: 0xF5D84A)
        case .ultramarine: Color(light: 0xFF6B5B, dark: 0xFF7F70)
        case .aubergine: Color(light: 0x4FD1A5, dark: 0x6FE0B8)
        }
    }

    /// Hintergrund-Tönung (Creme, Zitronenhauch …). Im Dunkelmodus fast schwarz mit Farbstich.
    public var surface: Color {
        switch self {
        case .raspberry: Color(light: 0xFCF2EF, dark: 0x1C1214)
        case .tomato: Color(light: 0xFBF4E6, dark: 0x1A1513)
        case .herb: Color(light: 0xF6F8EC, dark: 0x121812)
        case .ultramarine: Color(light: 0xF3F4FC, dark: 0x111324)
        case .aubergine: Color(light: 0xF6F1F7, dark: 0x18121B)
        }
    }

    /// Karten / Zeilen auf der Tönung.
    public var card: Color {
        Color(light: 0xFFFFFF, dark: 0x24201E)
    }

    public var blobGradient: LinearGradient {
        LinearGradient(colors: [accent, partner], startPoint: .topLeading, endPoint: .bottomTrailing)
    }

    /// Früher stand die Standard-Farbwelt der App vorn. Jetzt zeigen alle Apps dieselbe Reihenfolge.
    @available(*, deprecated, message: "AppTheme.allCases nehmen – alle Apps zeigen dieselbe Reihenfolge")
    public static func choices(standard: AppTheme) -> [AppTheme] {
        allCases
    }

    /// Name des alternativen App-Icons im Asset-Katalog (`AppIcon-<farbwelt>`), `nil` für das Haupt-Icon.
    public func appIconName(standard: AppTheme) -> String? {
        self == standard ? nil : "AppIcon-\(rawValue)"
    }
}

extension Color {
    /// Farbe mit eigener Variante für hellen und dunklen Modus.
    public init(light: UInt32, dark: UInt32) {
        #if canImport(UIKit)
        self.init(uiColor: UIColor { traits in
            UIColor(hex: traits.userInterfaceStyle == .dark ? dark : light)
        })
        #else
        self.init(nsColor: NSColor(name: nil) { appearance in
            NSColor(hex: appearance.bestMatch(from: [.darkAqua, .aqua]) == .darkAqua ? dark : light)
        })
        #endif
    }
}

#if canImport(UIKit)
extension UIColor {
    public convenience init(hex: UInt32) {
        self.init(
            red: CGFloat((hex >> 16) & 0xFF) / 255,
            green: CGFloat((hex >> 8) & 0xFF) / 255,
            blue: CGFloat(hex & 0xFF) / 255,
            alpha: 1
        )
    }
}
#else
extension NSColor {
    convenience init(hex: UInt32) {
        self.init(
            srgbRed: CGFloat((hex >> 16) & 0xFF) / 255,
            green: CGFloat((hex >> 8) & 0xFF) / 255,
            blue: CGFloat(hex & 0xFF) / 255,
            alpha: 1
        )
    }
}
#endif

extension EnvironmentValues {
    /// Die gewählte Farbwelt. Jede App setzt sie an der Wurzel (App, Teilen-Erweiterung) aus ihren Einstellungen.
    @Entry public var theme: AppTheme = .tomato
}
