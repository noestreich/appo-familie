import Foundation

/// Gerätename für Texte („auf deinem iPhone“ bzw. „auf deinem iPad“). Das Layout entscheidet weiter allein
/// über die Größenklasse (DESIGN.md, „iPad“), das hier ist nur für Wörter.
/// Über die Modellkennung statt `UIDevice`, damit es auch außerhalb des Main Actors und auf dem Mac geht.
public enum Device {
    public static let isPad: Bool = {
        // Im Simulator meldet das System "arm64", die Kennung des simulierten Geräts steht in der Umgebung.
        if let simulated = ProcessInfo.processInfo.environment["SIMULATOR_MODEL_IDENTIFIER"] {
            return simulated.hasPrefix("iPad")
        }
        var info = utsname()
        uname(&info)
        let machine = withUnsafeBytes(of: &info.machine) { bytes in
            String(decoding: bytes.prefix { $0 != 0 }, as: UTF8.self)
        }
        return machine.hasPrefix("iPad")
    }()

    /// „iPhone“ oder „iPad“.
    public static let name = isPad ? "iPad" : "iPhone"
}
