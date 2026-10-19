import SwiftUI

/// Rückmeldung oben, optional mit Aktion („8 Artikel hinzugefügt“ – „Verschieben“). Verschwindet von selbst,
/// darum kümmert sich die App (DESIGN.md, „Muster“).
public struct Banner: Identifiable, Equatable {
    public let id = UUID()
    public var text: String
    public var isWarning: Bool
    /// Eigenes Symbol statt Haken bzw. Ausrufezeichen.
    public var symbol: String?
    /// Zeigt einen Pfeil: Antippen öffnet mehr (Kaufo: „Was wurde gelesen?“).
    public var showsDetail: Bool
    public var actionTitle: String?
    public var action: (() -> Void)?

    public init(
        text: String,
        isWarning: Bool = false,
        symbol: String? = nil,
        showsDetail: Bool = false,
        actionTitle: String? = nil,
        action: (() -> Void)? = nil
    ) {
        self.text = text
        self.isWarning = isWarning
        self.symbol = symbol
        self.showsDetail = showsDetail
        self.actionTitle = actionTitle
        self.action = action
    }

    public static func == (lhs: Banner, rhs: Banner) -> Bool { lhs.id == rhs.id }
}

public struct BannerView: View {
    let banner: Banner
    /// Antippen des Textes (nur wenn gesetzt, sonst bleibt der Text ohne Tipp-Geste).
    var onTap: (() -> Void)?
    @Environment(\.theme) private var theme

    public init(banner: Banner, onTap: (() -> Void)? = nil) {
        self.banner = banner
        self.onTap = onTap
    }

    public var body: some View {
        HStack(spacing: 10) {
            message
            if let title = banner.actionTitle, let action = banner.action {
                Button(title, action: action)
                    .appFont(.subheadline, weight: .semibold)
                    .buttonStyle(.borderedProminent)
                    .buttonBorderShape(.capsule)
                    .tint(theme.accent)
            }
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 10)
        .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 22, style: .continuous))
        .shadow(color: .black.opacity(0.08), radius: 10, y: 4)
        .padding(.horizontal)
        .accessibilityElement(children: .combine)
    }

    @ViewBuilder
    private var message: some View {
        let content = HStack(spacing: 8) {
            Image(systemName: banner.symbol ?? (banner.isWarning ? "exclamationmark.circle.fill" : "checkmark.circle.fill"))
                .foregroundStyle(banner.isWarning ? theme.partner : theme.accent)
            Text(banner.text)
                .appFont(.subheadline, weight: .medium)
                .fixedSize(horizontal: false, vertical: true)
            if banner.showsDetail {
                Image(systemName: "chevron.right")
                    .appFont(.caption, weight: .semibold)
                    .foregroundStyle(.secondary)
            }
        }
        if let onTap {
            content
                .contentShape(Rectangle())
                .onTapGesture(perform: onTap)
        } else {
            content
        }
    }
}
