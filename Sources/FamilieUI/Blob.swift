import SwiftUI

/// Organische, langsam "atmende" Form – Haupt-Button und App-Logo (DESIGN.md, „Der Blob“).
public struct BlobShape: Shape {
    /// Zeit in Sekunden; treibt die Verformung.
    public var time: Double
    /// Stärke der Verformung (0 = Kreis).
    public var wobble: Double

    public init(time: Double, wobble: Double = 1) {
        self.time = time
        self.wobble = wobble
    }

    public var animatableData: AnimatablePair<Double, Double> {
        get { AnimatablePair(time, wobble) }
        set { time = newValue.first; wobble = newValue.second }
    }

    public func path(in rect: CGRect) -> Path {
        let center = CGPoint(x: rect.midX, y: rect.midY)
        let baseRadius = min(rect.width, rect.height) / 2 * 0.88
        let count = 9
        var points: [CGPoint] = []
        for index in 0..<count {
            let angle = Double(index) / Double(count) * 2 * .pi
            let offset = wobble * (
                0.055 * sin(3 * angle + time * 0.9)
                + 0.035 * sin(5 * angle - time * 1.3)
                + 0.025 * sin(2 * angle + time * 0.55)
            )
            let radius = baseRadius * (1 + offset)
            points.append(CGPoint(x: center.x + cos(angle) * radius, y: center.y + sin(angle) * radius))
        }
        return Self.smoothClosedPath(through: points)
    }

    /// Catmull-Rom-Spline als kubische Bézierkurven.
    public static func smoothClosedPath(through points: [CGPoint]) -> Path {
        var path = Path()
        guard points.count > 2 else { return path }
        let count = points.count
        path.move(to: points[0])
        for index in 0..<count {
            let p0 = points[(index - 1 + count) % count]
            let p1 = points[index]
            let p2 = points[(index + 1) % count]
            let p3 = points[(index + 2) % count]
            let control1 = CGPoint(x: p1.x + (p2.x - p0.x) / 6, y: p1.y + (p2.y - p0.y) / 6)
            let control2 = CGPoint(x: p2.x - (p3.x - p1.x) / 6, y: p2.y - (p3.y - p1.y) / 6)
            path.addCurve(to: p2, control1: control1, control2: control2)
        }
        path.closeSubpath()
        return path
    }
}

/// Der große Haupt-Button unten rechts: Tippen = Fächer-Menü, Halten = Hauptaktion der App
/// (Kaufo und Schreibo: Spracheingabe, solange gehalten; Scanno: sofort scannen).
/// Die Texte für VoiceOver sagt die App, was Halten tut.
public struct BlobButton: View {
    var size: CGFloat
    var isExpanded: Bool
    var isListening: Bool
    var isBusy: Bool
    /// Lautstärke 0…1 während der Spracheingabe – lässt den Blob mitschwingen.
    var audioLevel: Double
    /// VoiceOver: Name im Ruhezustand, z. B. „Hinzufügen“.
    var title: String
    /// VoiceOver: was Halten tut, z. B. „Spracheingabe starten“.
    var holdTitle: String
    /// VoiceOver: Hinweis zum Halten.
    var holdHint: String
    /// VoiceOver: Name beim Zuhören, z. B. „Spracheingabe beenden“.
    var stopTitle: String
    /// Ob Halten auch wirkt, während die App arbeitet (`isBusy`).
    var holdsWhileBusy: Bool
    let onTap: () -> Void
    let onHoldStart: () -> Void
    let onHoldEnd: () -> Void

    @Environment(\.theme) private var theme
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @State private var pressStarted = false
    @State private var isHolding = false
    @State private var holdTask: Task<Void, Never>?
    @State private var isPressed = false

    public init(
        size: CGFloat = 84,
        isExpanded: Bool = false,
        isListening: Bool = false,
        isBusy: Bool = false,
        audioLevel: Double = 0,
        title: String = "Hinzufügen",
        holdTitle: String = "Spracheingabe starten",
        holdHint: String = "Gedrückt halten für Spracheingabe",
        stopTitle: String = "Spracheingabe beenden",
        holdsWhileBusy: Bool = true,
        onTap: @escaping () -> Void,
        onHoldStart: @escaping () -> Void,
        onHoldEnd: @escaping () -> Void = {}
    ) {
        self.size = size
        self.isExpanded = isExpanded
        self.isListening = isListening
        self.isBusy = isBusy
        self.audioLevel = audioLevel
        self.title = title
        self.holdTitle = holdTitle
        self.holdHint = holdHint
        self.stopTitle = stopTitle
        self.holdsWhileBusy = holdsWhileBusy
        self.onTap = onTap
        self.onHoldStart = onHoldStart
        self.onHoldEnd = onHoldEnd
    }

    public var body: some View {
        TimelineView(.animation(minimumInterval: 1 / 30, paused: reduceMotion)) { context in
            let time = context.date.timeIntervalSinceReferenceDate * (isListening ? 2.4 : (isBusy ? 1.8 : 1))
            let wobble = reduceMotion ? 0.3 : (isListening ? 1.6 + audioLevel * 2.5 : 1)
            ZStack {
                // Weicher Schatten in Akzentfarbe
                BlobShape(time: time + 1.7, wobble: wobble)
                    .fill(theme.accent.opacity(0.28))
                    .blur(radius: 10)
                    .offset(y: 6)
                BlobShape(time: time, wobble: wobble)
                    .fill(theme.blobGradient)
                // Glanzlicht
                BlobShape(time: time * 0.8 + 3, wobble: wobble * 0.7)
                    .fill(
                        RadialGradient(
                            colors: [.white.opacity(0.35), .clear],
                            center: UnitPoint(x: 0.3, y: 0.25),
                            startRadius: 0,
                            endRadius: size * 0.55
                        )
                    )
                    .scaleEffect(0.86)
                icon
                    .font(.system(size: size * 0.34, weight: .semibold))
                    .foregroundStyle(.white)
                    .contentTransition(.symbolEffect(.replace))
            }
        }
        .frame(width: size, height: size)
        .scaleEffect(isPressed ? 0.92 : (isListening ? 1.12 : 1))
        .animation(.spring(response: 0.3, dampingFraction: 0.6), value: isPressed)
        .animation(.spring(response: 0.4, dampingFraction: 0.7), value: isListening)
        .contentShape(Circle())
        .gesture(pressGesture)
        .sensoryFeedback(.impact(weight: .medium), trigger: isHolding)
        .accessibilityElement()
        .accessibilityLabel(isListening ? stopTitle : (isExpanded ? "Menü schließen" : title))
        .accessibilityHint(holdHint)
        .accessibilityAddTraits(.isButton)
        .accessibilityAction { onTap() }
        .accessibilityAction(named: isListening ? stopTitle : holdTitle) {
            if isListening { onHoldEnd() } else { onHoldStart() }
        }
    }

    @ViewBuilder
    private var icon: some View {
        if isBusy {
            ProgressView()
                .progressViewStyle(.circular)
                .tint(.white)
                .controlSize(.large)
        } else if isListening {
            Image(systemName: "waveform")
                .symbolEffect(.variableColor.iterative, isActive: true)
        } else {
            Image(systemName: "plus")
                .fontWeight(.bold)
                .rotationEffect(.degrees(isExpanded ? 45 : 0))
                .animation(.spring(response: 0.3, dampingFraction: 0.6), value: isExpanded)
        }
    }

    private var pressGesture: some Gesture {
        DragGesture(minimumDistance: 0)
            .onChanged { _ in
                guard !pressStarted else { return }
                pressStarted = true
                isPressed = true
                holdTask = Task {
                    try? await Task.sleep(for: .milliseconds(350))
                    guard !Task.isCancelled, holdsWhileBusy || !isBusy else { return }
                    isHolding = true
                    onHoldStart()
                }
            }
            .onEnded { _ in
                holdTask?.cancel()
                holdTask = nil
                isPressed = false
                pressStarted = false
                if isHolding {
                    isHolding = false
                    onHoldEnd()
                } else if !isBusy {
                    onTap()
                }
            }
    }
}

/// Das weiße Zeichen im Blob-Logo: ein SF Symbol mit Größe (Anteil am Logo), Stärke und Schriftdesign.
/// Ein String-Literal ergibt ein Symbol im Stil von Kaufos Haken, z. B. `BlobLogo(symbol: "sparkles")`.
public struct BlobSymbol: ExpressibleByStringLiteral {
    public var name: String
    public var scale: CGFloat
    public var weight: Font.Weight
    public var design: Font.Design

    public init(_ name: String, scale: CGFloat = 0.38, weight: Font.Weight = .bold, design: Font.Design = .rounded) {
        self.name = name
        self.scale = scale
        self.weight = weight
        self.design = design
    }

    public init(stringLiteral value: String) {
        self.init(value)
    }

    /// Kaufo
    public static let checkmark = BlobSymbol("checkmark")
    /// Scanno
    public static let document = BlobSymbol("doc.text.fill", scale: 0.4, weight: .regular, design: .default)
    /// Schreibo
    public static let pencil = BlobSymbol("pencil")
}

/// Das App-Logo: der Blob mit weißem Zeichen – ruhend. In leeren Zuständen, Ladeanzeigen und im Onboarding.
public struct BlobLogo: View {
    var size: CGFloat
    var symbol: BlobSymbol
    @Environment(\.theme) private var theme

    public init(size: CGFloat = 120, symbol: BlobSymbol = .checkmark) {
        self.size = size
        self.symbol = symbol
    }

    public var body: some View {
        ZStack {
            BlobShape(time: 2.2)
                .fill(theme.blobGradient)
            Image(systemName: symbol.name)
                .font(.system(size: size * symbol.scale, weight: symbol.weight, design: symbol.design))
                .foregroundStyle(.white)
        }
        .frame(width: size, height: size)
        .accessibilityHidden(true)
    }
}

#Preview {
    VStack(spacing: 40) {
        BlobButton(onTap: {}, onHoldStart: {}, onHoldEnd: {})
        BlobButton(isListening: true, audioLevel: 0.5, onTap: {}, onHoldStart: {}, onHoldEnd: {})
        BlobLogo()
        BlobLogo(size: 80, symbol: .document)
    }
}
