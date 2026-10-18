import SwiftUI
#if canImport(StoreKit) && canImport(UIKit)
import StoreKit
import UIKit
#endif

/// Abschnitt "Weitere Apps von uns" für ein `Form`/`List` – Einträge wie in den App-Store-Suchergebnissen.
///
/// ```swift
/// MoreAppsSection(developerID: 776255936)
/// ```
/// Die eigene App wird anhand der Bundle-ID ausgelassen. Ohne Netz und ohne gespeicherte Liste bleibt der Abschnitt leer.
public struct MoreAppsSection: View {
    @State private var loader: MoreAppsLoader
    private let title: String
    private let showsScreenshots: Bool

    public init(
        developerID: Int,
        additionalAppIDs: [Int] = [],
        title: String = "Weitere Apps von uns",
        country: String = Locale.current.region?.identifier.lowercased() ?? "de",
        excludingBundleID: String? = Bundle.main.bundleIdentifier,
        showsScreenshots: Bool = true
    ) {
        _loader = State(initialValue: MoreAppsLoader(
            developerID: developerID,
            additionalAppIDs: additionalAppIDs,
            country: country,
            excludingBundleID: excludingBundleID
        ))
        self.title = title
        self.showsScreenshots = showsScreenshots
    }

    public var body: some View {
        Group {
            switch loader.phase {
            case .loading:
                Section(title) {
                    ProgressView()
                        .frame(maxWidth: .infinity)
                }
            case .loaded where !loader.apps.isEmpty:
                Section(title) {
                    ForEach(loader.apps) { app in
                        StoreAppRow(app: app, showsScreenshots: showsScreenshots)
                    }
                }
            default:
                EmptyView()
            }
        }
        .task { await loader.load() }
    }
}

/// Eine App wie in den Suchergebnissen: Icon, Name, Untertitel, Sterne, "Laden"-Knopf, darunter Screenshots.
public struct StoreAppRow: View {
    let app: StoreApp
    var showsScreenshots = true

    public init(app: StoreApp, showsScreenshots: Bool = true) {
        self.app = app
        self.showsScreenshots = showsScreenshots
    }

    public var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack(spacing: 12) {
                AppIcon(url: app.iconURL, size: 62)
                VStack(alignment: .leading, spacing: 2) {
                    Text(app.name)
                        .font(.body.weight(.semibold))
                        .foregroundStyle(.primary)
                        .lineLimit(1)
                    if !app.subtitle.isEmpty {
                        Text(app.subtitle)
                            .font(.subheadline)
                            .foregroundStyle(.secondary)
                            .lineLimit(1)
                    }
                    if let rating = app.rating, let count = app.ratingCount, count > 0 {
                        RatingView(rating: rating, count: count)
                    }
                }
                Spacer(minLength: 8)
                Button(app.buttonTitle) { StoreProductPresenter.present(app) }
                    .buttonStyle(GetButtonStyle())
                    .accessibilityLabel("\(app.name) \(app.buttonTitle)")
            }
            if showsScreenshots, !app.screenshotURLs.isEmpty {
                Screenshots(urls: app.screenshotURLs, portrait: app.screenshotsArePortrait)
            }
        }
        .padding(.vertical, 6)
        .contentShape(Rectangle())
        .onTapGesture { StoreProductPresenter.present(app) }
        .accessibilityElement(children: .combine)
        .accessibilityAddTraits(.isButton)
    }
}

private struct AppIcon: View {
    let url: URL?
    let size: CGFloat

    var body: some View {
        let shape = RoundedRectangle(cornerRadius: size * 0.225, style: .continuous)
        AsyncImage(url: url) { image in
            image.resizable().scaledToFill()
        } placeholder: {
            Color.secondary.opacity(0.12)
        }
        .frame(width: size, height: size)
        .clipShape(shape)
        .overlay(shape.strokeBorder(Color.primary.opacity(0.1), lineWidth: 0.5))
        .accessibilityHidden(true)
    }
}

private struct RatingView: View {
    let rating: Double
    let count: Int

    var body: some View {
        HStack(spacing: 4) {
            HStack(spacing: 1) {
                ForEach(0..<5, id: \.self) { index in
                    let fill = min(1, max(0, rating - Double(index)))
                    Image(systemName: fill >= 0.75 ? "star.fill" : fill >= 0.25 ? "star.leadinghalf.filled" : "star")
                }
            }
            .font(.system(size: 10))
            Text(count, format: .number.notation(.compactName))
                .font(.caption)
        }
        .foregroundStyle(.secondary)
        .accessibilityLabel(String(format: "%.1f von 5 Sternen, %d Bewertungen", rating, count))
    }
}

private struct Screenshots: View {
    let urls: [URL]
    let portrait: Bool

    var body: some View {
        HStack(spacing: 8) {
            ForEach(Array(urls.prefix(portrait ? 3 : 1)), id: \.self) { url in
                let shape = RoundedRectangle(cornerRadius: 10, style: .continuous)
                AsyncImage(url: url) { image in
                    image.resizable().scaledToFill()
                } placeholder: {
                    Color.secondary.opacity(0.12)
                }
                .aspectRatio(portrait ? 392.0 / 696.0 : 696.0 / 392.0, contentMode: .fit)
                .frame(maxWidth: .infinity)
                .clipShape(shape)
                .overlay(shape.strokeBorder(Color.primary.opacity(0.1), lineWidth: 0.5))
            }
        }
        .accessibilityHidden(true)
    }
}

/// Grauer Kapselknopf mit Text in der Akzentfarbe – wie "Laden" im App Store.
private struct GetButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .font(.subheadline.weight(.bold))
            .foregroundStyle(.tint)
            .padding(.horizontal, 18)
            .padding(.vertical, 6)
            .background(Capsule().fill(Color.secondary.opacity(0.15)))
            .opacity(configuration.isPressed ? 0.5 : 1)
    }
}

/// Öffnet die App-Store-Seite direkt in der App; ohne StoreKit über den Link.
@MainActor
enum StoreProductPresenter {
    #if canImport(StoreKit) && canImport(UIKit)
    private final class Delegate: NSObject, SKStoreProductViewControllerDelegate {
        func productViewControllerDidFinish(_ viewController: SKStoreProductViewController) {
            // StoreKit ruft auf dem Hauptthread
            MainActor.assumeIsolated {
                viewController.presentingViewController?.dismiss(animated: true)
            }
        }
    }

    private static let delegate = Delegate()
    #endif

    static func present(_ app: StoreApp) {
        #if canImport(StoreKit) && canImport(UIKit)
        guard let top = topViewController() else { return openLink(app) }
        let controller = SKStoreProductViewController()
        controller.delegate = delegate
        controller.loadProduct(withParameters: [SKStoreProductParameterITunesItemIdentifier: NSNumber(value: app.id)]) { loaded, _ in
            if !loaded {
                Task { @MainActor in
                    controller.dismiss(animated: true)
                    openLink(app)
                }
            }
        }
        top.present(controller, animated: true)
        #else
        openLink(app)
        #endif
    }

    private static func openLink(_ app: StoreApp) {
        #if canImport(UIKit)
        if let url = app.storeURL ?? URL(string: "https://apps.apple.com/app/id\(app.id)") {
            UIApplication.shared.open(url)
        }
        #endif
    }

    #if canImport(UIKit)
    private static func topViewController() -> UIViewController? {
        let scene = UIApplication.shared.connectedScenes
            .compactMap { $0 as? UIWindowScene }
            .first { $0.activationState == .foregroundActive }
        var top = scene?.keyWindow?.rootViewController
        while let presented = top?.presentedViewController { top = presented }
        return top
    }
    #endif
}
