import SwiftUI

/// Ein Eintrag im Fächer-Menü über dem Blob: Kapsel mit Symbol und Text.
public struct FanItem: Identifiable {
    public let title: String
    public let symbol: String
    public let action: () -> Void
    public var id: String { title }

    public init(title: String, symbol: String, action: @escaping () -> Void) {
        self.title = title
        self.symbol = symbol
        self.action = action
    }
}

/// Eine Kapsel im Fächer; erscheint gestaffelt von unten (die unterste zuerst).
struct FanButton: View {
    let item: FanItem
    /// Verzögerung beim Auffächern in Schritten von 0,04 Sekunden.
    let step: Int
    let onSelect: () -> Void
    @Environment(\.theme) private var theme

    var body: some View {
        Button {
            onSelect()
            item.action()
        } label: {
            Label(item.title, systemImage: item.symbol)
                .appFont(.body, weight: .medium)
                .foregroundStyle(.primary)
                .padding(.horizontal, 18)
                .padding(.vertical, 12)
                .background(theme.card, in: Capsule())
                .overlay(Capsule().strokeBorder(theme.accent.opacity(0.3)))
                .shadow(color: .black.opacity(0.08), radius: 8, y: 3)
        }
        .buttonStyle(.plain)
        .transition(
            .asymmetric(
                insertion: .move(edge: .bottom).combined(with: .opacity)
                    .animation(.spring(response: 0.35, dampingFraction: 0.75).delay(Double(step) * 0.04)),
                removal: .opacity
            )
        )
    }
}

/// Nur die Kapseln, die sich beim Tippen auf den Blob auffächern – wenn die App den Blob selbst anordnet
/// (Schreibo). Sonst `BlobMenu`. `alignment` ist `.leading`, wenn der Blob links steht.
public struct BlobFan: View {
    let items: [FanItem]
    let alignment: HorizontalAlignment
    let onSelect: () -> Void

    public init(items: [FanItem], alignment: HorizontalAlignment = .trailing, onSelect: @escaping () -> Void) {
        self.items = items
        self.alignment = alignment
        self.onSelect = onSelect
    }

    public var body: some View {
        VStack(alignment: alignment, spacing: 12) {
            ForEach(Array(items.enumerated()), id: \.element.id) { index, item in
                FanButton(item: item, step: items.count - 1 - index, onSelect: onSelect)
            }
        }
    }
}

/// Der Blob mit Fächer-Menü (Kaufo, Scanno): Tippen fächert die Einträge auf, Halten startet die Hauptaktion.
/// Hört die App gerade zu, beendet ein Tipp das Zuhören.
public struct BlobMenu: View {
    @Binding var isExpanded: Bool
    let items: [FanItem]
    var isListening: Bool
    var isBusy: Bool
    var audioLevel: Double
    var title: String
    var holdTitle: String
    var holdHint: String
    var stopTitle: String
    var holdsWhileBusy: Bool
    let onHoldStart: () -> Void
    let onHoldEnd: () -> Void

    public init(
        isExpanded: Binding<Bool>,
        items: [FanItem],
        isListening: Bool = false,
        isBusy: Bool = false,
        audioLevel: Double = 0,
        title: String = "Hinzufügen",
        holdTitle: String = "Spracheingabe starten",
        holdHint: String = "Gedrückt halten für Spracheingabe",
        stopTitle: String = "Spracheingabe beenden",
        holdsWhileBusy: Bool = true,
        onHoldStart: @escaping () -> Void,
        onHoldEnd: @escaping () -> Void = {}
    ) {
        _isExpanded = isExpanded
        self.items = items
        self.isListening = isListening
        self.isBusy = isBusy
        self.audioLevel = audioLevel
        self.title = title
        self.holdTitle = holdTitle
        self.holdHint = holdHint
        self.stopTitle = stopTitle
        self.holdsWhileBusy = holdsWhileBusy
        self.onHoldStart = onHoldStart
        self.onHoldEnd = onHoldEnd
    }

    public var body: some View {
        VStack(alignment: .trailing, spacing: 12) {
            if isExpanded {
                ForEach(Array(items.enumerated()), id: \.element.id) { index, item in
                    FanButton(item: item, step: items.count - 1 - index) {
                        withAnimation(.spring(response: 0.3, dampingFraction: 0.8)) { isExpanded = false }
                    }
                }
            }
            BlobButton(
                size: 80,
                isExpanded: isExpanded,
                isListening: isListening,
                isBusy: isBusy,
                audioLevel: audioLevel,
                title: title,
                holdTitle: holdTitle,
                holdHint: holdHint,
                stopTitle: stopTitle,
                holdsWhileBusy: holdsWhileBusy,
                onTap: {
                    if isListening {
                        onHoldEnd()
                    } else {
                        withAnimation(.spring(response: 0.35, dampingFraction: 0.75)) { isExpanded.toggle() }
                    }
                },
                onHoldStart: {
                    withAnimation { isExpanded = false }
                    onHoldStart()
                },
                onHoldEnd: onHoldEnd
            )
        }
    }
}
