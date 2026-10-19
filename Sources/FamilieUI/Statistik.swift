import SwiftUI

/// Karte für einen Abschnitt der Statistik: Kopf in Akzentfarbe mit Symbol, darunter der Inhalt.
public struct StatCard<Content: View>: View {
    let title: String
    let symbol: String
    let content: Content
    @Environment(\.theme) private var theme

    public init(title: String, symbol: String, @ViewBuilder content: () -> Content) {
        self.title = title
        self.symbol = symbol
        self.content = content()
    }

    public var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            Label(title, systemImage: symbol)
                .appFont(.subheadline, weight: .semibold, heading: true)
                .foregroundStyle(theme.accent)
            content
        }
        .padding(18)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(theme.card, in: RoundedRectangle(cornerRadius: 22, style: .continuous))
    }
}

/// Kennzahl als große Zahl mit Beschriftung darunter.
public struct StatTile: View {
    let value: String
    let label: String

    public init(value: String, label: String) {
        self.value = value
        self.label = label
    }

    public var body: some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(value)
                .appFont(.title2, weight: .bold, heading: true)
                .monospacedDigit()
                .lineLimit(1)
                .minimumScaleFactor(0.7)
            Text(label)
                .appFont(.caption)
                .foregroundStyle(.secondary)
        }
        .accessibilityElement(children: .combine)
    }
}

/// Waagerechte Balken mit Beschriftung – lesbarer als ein Tortendiagramm.
public struct RankedBars: View {
    /// Eine Zeile: Name, Wert, optional Symbol und eigene Farbe (sonst `color`).
    public struct Row: Identifiable {
        public var id: String { name }
        public let name: String
        public let value: Int
        public var symbol: String?
        public var color: Color?

        public init(name: String, value: Int, symbol: String? = nil, color: Color? = nil) {
            self.name = name
            self.value = value
            self.symbol = symbol
            self.color = color
        }
    }

    let rows: [Row]
    let color: Color
    var showsShare: Bool
    var format: (Int) -> String

    public init(rows: [Row], color: Color, showsShare: Bool = false, format: @escaping (Int) -> String = { "\($0)" }) {
        self.rows = rows
        self.color = color
        self.showsShare = showsShare
        self.format = format
    }

    public var body: some View {
        let maximum = max(1, rows.map(\.value).max() ?? 1)
        let total = max(1, rows.map(\.value).reduce(0, +))
        VStack(spacing: 10) {
            ForEach(rows) { row in
                VStack(alignment: .leading, spacing: 4) {
                    HStack(spacing: 6) {
                        if let symbol = row.symbol {
                            Image(systemName: symbol)
                                .appFont(.caption)
                                .foregroundStyle(.secondary)
                                .frame(width: 18)
                        }
                        Text(row.name)
                            .appFont(.subheadline)
                            .lineLimit(1)
                        Spacer(minLength: 8)
                        Text(format(row.value))
                            .appFont(.subheadline, weight: .semibold)
                            .monospacedDigit()
                        if showsShare {
                            Text("\(Int((Double(row.value) / Double(total) * 100).rounded())) %")
                                .appFont(.caption)
                                .foregroundStyle(.secondary)
                                .monospacedDigit()
                                .frame(width: 40, alignment: .trailing)
                        }
                    }
                    GeometryReader { proxy in
                        Capsule()
                            .fill(row.color ?? color)
                            .frame(width: max(6, proxy.size.width * Double(row.value) / Double(maximum)))
                    }
                    .frame(height: 6)
                }
                .accessibilityElement(children: .ignore)
                .accessibilityLabel(row.name)
                .accessibilityValue(format(row.value))
            }
        }
    }
}
