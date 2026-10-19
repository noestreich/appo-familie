// swift-tools-version: 6.0
import PackageDescription

/// Gemeinsame Bausteine der App-Familie (Kaufo, Scanno, Schreibo). Die Apps folgen dem Branch `v1`,
/// der erst nach Erprobung in einer App nachgezogen wird (README).
let package = Package(
    name: "AppoFamilie",
    defaultLocalization: "de",
    platforms: [.iOS(.v17), .macOS(.v14)],
    products: [
        /// „Weitere Apps von uns“ ganz unten in den Einstellungen
        .library(name: "MoreApps", targets: ["MoreApps"]),
        /// Farbwelten, Schriften, Blob, Banner, Fächer-Menü, Statistik-Bausteine
        .library(name: "FamilieUI", targets: ["FamilieUI"])
    ],
    targets: [
        .target(name: "MoreApps", swiftSettings: [.swiftLanguageMode(.v5)]),
        .target(name: "FamilieUI", swiftSettings: [.swiftLanguageMode(.v5)])
    ]
)
