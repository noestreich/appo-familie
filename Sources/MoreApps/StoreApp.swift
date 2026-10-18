import Foundation

/// Eine App aus dem App Store, wie sie Apples Suchschnittstelle liefert.
public struct StoreApp: Codable, Identifiable, Hashable, Sendable {
    public let id: Int
    public let name: String
    public let bundleID: String?
    public let genre: String?
    public let description: String?
    public let iconURL: URL?
    public let screenshotURLs: [URL]
    public let rating: Double?
    public let ratingCount: Int?
    public let price: Double?
    public let formattedPrice: String?
    public let storeURL: URL?

    enum CodingKeys: String, CodingKey {
        case id = "trackId"
        case name = "trackName"
        case bundleID = "bundleId"
        case genre = "primaryGenreName"
        case description
        case iconURL = "artworkUrl512"
        case iconURL100 = "artworkUrl100"
        case screenshotURLs = "screenshotUrls"
        case rating = "averageUserRating"
        case ratingCount = "userRatingCount"
        case price
        case formattedPrice
        case storeURL = "trackViewUrl"
    }

    public init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        id = try container.decode(Int.self, forKey: .id)
        name = try container.decode(String.self, forKey: .name)
        bundleID = try container.decodeIfPresent(String.self, forKey: .bundleID)
        genre = try container.decodeIfPresent(String.self, forKey: .genre)
        description = try container.decodeIfPresent(String.self, forKey: .description)
        iconURL = try container.decodeIfPresent(URL.self, forKey: .iconURL)
            ?? container.decodeIfPresent(URL.self, forKey: .iconURL100)
        screenshotURLs = try container.decodeIfPresent([URL].self, forKey: .screenshotURLs) ?? []
        rating = try container.decodeIfPresent(Double.self, forKey: .rating)
        ratingCount = try container.decodeIfPresent(Int.self, forKey: .ratingCount)
        price = try container.decodeIfPresent(Double.self, forKey: .price)
        formattedPrice = try container.decodeIfPresent(String.self, forKey: .formattedPrice)
        storeURL = try container.decodeIfPresent(URL.self, forKey: .storeURL)
    }

    public func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(id, forKey: .id)
        try container.encode(name, forKey: .name)
        try container.encodeIfPresent(bundleID, forKey: .bundleID)
        try container.encodeIfPresent(genre, forKey: .genre)
        try container.encodeIfPresent(description, forKey: .description)
        try container.encodeIfPresent(iconURL, forKey: .iconURL)
        try container.encode(screenshotURLs, forKey: .screenshotURLs)
        try container.encodeIfPresent(rating, forKey: .rating)
        try container.encodeIfPresent(ratingCount, forKey: .ratingCount)
        try container.encodeIfPresent(price, forKey: .price)
        try container.encodeIfPresent(formattedPrice, forKey: .formattedPrice)
        try container.encodeIfPresent(storeURL, forKey: .storeURL)
    }

    /// Zweite Zeile wie im App Store: kurze erste Zeile der Beschreibung, sonst die Kategorie.
    public var subtitle: String {
        if let first = description?.split(whereSeparator: \.isNewline).first.map(String.init)?
            .trimmingCharacters(in: .whitespaces), !first.isEmpty, first.count <= 42 {
            return first
        }
        return genre ?? ""
    }

    /// "Laden" für kostenlose Apps, sonst der Preis.
    public var buttonTitle: String {
        guard let price, price > 0, let formattedPrice else { return "Laden" }
        return formattedPrice
    }

    /// Hochformat-Screenshots zeigt der App Store zu dritt, Querformat einzeln.
    public var screenshotsArePortrait: Bool {
        guard let size = screenshotURLs.first.flatMap(Self.pixelSize(in:)) else { return true }
        return size.height >= size.width
    }

    /// Bildgröße steckt in Apples Bild-URLs, z. B. ".../392x696bb.jpg".
    static func pixelSize(in url: URL) -> CGSize? {
        let name = url.lastPathComponent
        guard let range = name.range(of: #"^\d+x\d+"#, options: .regularExpression) else { return nil }
        let parts = name[range].split(separator: "x").compactMap { Double($0) }
        return parts.count == 2 ? CGSize(width: parts[0], height: parts[1]) : nil
    }
}

struct LookupResponse: Decodable {
    struct Entry: Decodable {
        let wrapperType: String?
        let kind: String?
    }

    let results: [StoreApp]

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        // Der erste Eintrag ist der Entwickler selbst – nur Apps übernehmen.
        var raw = try container.nestedUnkeyedContainer(forKey: .results)
        var apps: [StoreApp] = []
        while !raw.isAtEnd {
            let entryDecoder = try raw.superDecoder()
            let entry = try Entry(from: entryDecoder)
            if entry.wrapperType == "software", let app = try? StoreApp(from: entryDecoder) {
                apps.append(app)
            }
        }
        results = apps
    }

    enum CodingKeys: String, CodingKey {
        case results
    }
}
