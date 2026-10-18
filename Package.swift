// swift-tools-version: 6.0
import PackageDescription

/// Gemeinsame Bausteine der App-Familie (Kaufo, Scanno, Schreibo). Jede App bindet das Paket mit fester
/// Version ein (`from: "1.0.0"`), damit eine Änderung hier nicht unbemerkt alle Apps verändert.
let package = Package(
    name: "AppFamilie",
    defaultLocalization: "de",
    platforms: [.iOS(.v17), .macOS(.v14)],
    products: [
        /// „Weitere Apps von uns“ ganz unten in den Einstellungen
        .library(name: "MoreApps", targets: ["MoreApps"])
    ],
    targets: [
        .target(name: "MoreApps", swiftSettings: [.swiftLanguageMode(.v5)])
    ]
)
