import SwiftUI

/// Schriftarten zur Auswahl in den Einstellungen – nur Schriften, die iOS mitbringt.
/// Alle skalieren mit der dynamischen Textgröße.
public enum Typeface: String, CaseIterable, Identifiable, Sendable {
    case clear
    case rounded
    case serif
    case handwriting
    case marker
    case chalk
    case typewriter

    public static let storageKey = "typeface"

    public var id: String { rawValue }

    public var title: String {
        switch self {
        case .clear: "Klar"
        case .rounded: "Rund"
        case .serif: "Klassisch"
        case .handwriting: "Handschrift"
        case .marker: "Filzstift"
        case .chalk: "Kreide"
        case .typewriter: "Schreibmaschine"
        }
    }

    public var subtitle: String {
        switch self {
        case .clear: "SF Pro, Überschriften gerundet"
        case .rounded: "SF Rounded"
        case .serif: "New York"
        case .handwriting: "Noteworthy"
        case .marker: "Marker Felt"
        case .chalk: "Chalkboard SE"
        case .typewriter: "American Typewriter"
        }
    }

    /// Schrift für einen Textstil. `heading` = Überschriften, Titel, große Zahlen.
    public func font(_ style: Font.TextStyle, weight: Font.Weight = .regular, heading: Bool = false) -> Font {
        switch self {
        case .clear:
            return .system(style, design: heading ? .rounded : .default).weight(weight)
        case .rounded:
            return .system(style, design: .rounded).weight(weight)
        case .serif:
            return .system(style, design: .serif).weight(weight)
        case .handwriting, .marker, .chalk, .typewriter:
            let size = Self.baseSize(style) * scale
            return .custom(fontName(for: weight), size: size, relativeTo: style)
        }
    }

    /// Die eigenen Schriften wirken unterschiedlich groß – angleichen an SF Pro.
    private var scale: CGFloat {
        switch self {
        case .handwriting: 1.08
        case .marker: 1.08
        case .chalk: 0.96
        case .typewriter: 0.95
        default: 1
        }
    }

    private func fontName(for weight: Font.Weight) -> String {
        let bold = weight == .semibold || weight == .bold || weight == .heavy || weight == .black
        let medium = weight == .medium
        switch self {
        case .handwriting: return bold || medium ? "Noteworthy-Bold" : "Noteworthy-Light"
        case .marker: return bold ? "MarkerFelt-Wide" : "MarkerFelt-Thin"
        case .chalk: return bold ? "ChalkboardSE-Bold" : (medium ? "ChalkboardSE-Regular" : "ChalkboardSE-Light")
        case .typewriter: return bold ? "AmericanTypewriter-Semibold" : (medium ? "AmericanTypewriter" : "AmericanTypewriter-Light")
        default: return ""
        }
    }

    /// Standardgrößen der Textstile bei normaler Textgröße.
    private static func baseSize(_ style: Font.TextStyle) -> CGFloat {
        switch style {
        case .largeTitle: 34
        case .title: 28
        case .title2: 22
        case .title3: 20
        case .headline: 17
        case .body: 17
        case .callout: 16
        case .subheadline: 15
        case .footnote: 13
        case .caption: 12
        case .caption2: 11
        @unknown default: 17
        }
    }
}

extension EnvironmentValues {
    @Entry public var typeface: Typeface = .clear
}

private struct AppFontModifier: ViewModifier {
    @Environment(\.typeface) private var typeface
    let style: Font.TextStyle
    let weight: Font.Weight
    let heading: Bool

    func body(content: Content) -> some View {
        content.font(typeface.font(style, weight: weight, heading: heading))
    }
}

extension View {
    /// Schrift in der gewählten Schriftart der App.
    public func appFont(_ style: Font.TextStyle, weight: Font.Weight = .regular, heading: Bool = false) -> some View {
        modifier(AppFontModifier(style: style, weight: weight, heading: heading))
    }
}
