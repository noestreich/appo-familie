import Foundation
import Observation

/// Lädt die Apps eines Entwicklers aus dem App Store und merkt sie sich für unterwegs ohne Netz.
@MainActor
@Observable
public final class MoreAppsLoader {
    public enum Phase: Equatable {
        case loading
        case loaded
        case unavailable
    }

    public private(set) var apps: [StoreApp] = []
    public private(set) var phase: Phase = .loading

    private let developerID: Int
    private let additionalAppIDs: [Int]
    private let country: String
    private let excludedBundleID: String?
    /// So lange gilt die gespeicherte Liste als frisch.
    private let maxAge: TimeInterval = 24 * 3600

    public init(developerID: Int, additionalAppIDs: [Int] = [], country: String, excludingBundleID: String?) {
        self.developerID = developerID
        self.additionalAppIDs = additionalAppIDs
        self.country = country
        self.excludedBundleID = excludingBundleID
        if let cached = Self.readCache(cacheURL) {
            apps = filtered(cached.apps)
            phase = .loaded
        }
    }

    private var cacheURL: URL {
        let folder = FileManager.default.urls(for: .cachesDirectory, in: .userDomainMask)[0]
        return folder.appendingPathComponent("more-apps-\(developerID)-\(country).json")
    }

    /// Zeigt sofort die gespeicherte Liste und holt höchstens einmal am Tag eine neue.
    public func load(force: Bool = false) async {
        if !force, let cached = Self.readCache(cacheURL), Date().timeIntervalSince(cached.date) < maxAge { return }
        do {
            let fetched = try await fetch()
            apps = filtered(fetched)
            phase = .loaded
            Self.writeCache(Cache(date: Date(), apps: fetched), to: cacheURL)
        } catch {
            if apps.isEmpty { phase = .unavailable }
        }
    }

    private func fetch() async throws -> [StoreApp] {
        var result = try await lookup("id=\(developerID)&entity=software&limit=200")
        // Ausdrücklich genannte Apps ergänzen (z. B. unter anderem Anbieter oder gerade erst erschienen).
        let missing = additionalAppIDs.filter { id in !result.contains { $0.id == id } }
        if !missing.isEmpty {
            result += try await lookup("id=" + missing.map(String.init).joined(separator: ","))
        }
        return result
    }

    private func lookup(_ query: String) async throws -> [StoreApp] {
        guard let url = URL(string: "https://itunes.apple.com/lookup?\(query)&country=\(country)") else { return [] }
        let (data, response) = try await URLSession.shared.data(from: url)
        guard (response as? HTTPURLResponse)?.statusCode == 200 else { throw URLError(.badServerResponse) }
        return try JSONDecoder().decode(LookupResponse.self, from: data).results
    }

    /// Ohne die eigene App, beliebteste zuerst.
    private func filtered(_ apps: [StoreApp]) -> [StoreApp] {
        var seen = Set<Int>()
        return apps
            .filter { $0.bundleID != excludedBundleID && seen.insert($0.id).inserted }
            .sorted { ($0.ratingCount ?? 0) > ($1.ratingCount ?? 0) }
    }

    // MARK: Zwischenspeicher

    private struct Cache: Codable {
        var date: Date
        var apps: [StoreApp]
    }

    private static func readCache(_ url: URL) -> Cache? {
        guard let data = try? Data(contentsOf: url) else { return nil }
        return try? JSONDecoder().decode(Cache.self, from: data)
    }

    private static func writeCache(_ cache: Cache, to url: URL) {
        if let data = try? JSONEncoder().encode(cache) { try? data.write(to: url, options: .atomic) }
    }
}
