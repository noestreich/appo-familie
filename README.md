# App-Familie

Gemeinsame Regeln und Bausteine für die iOS-Apps [Kaufo](https://github.com/noestreich/einkauf), [Scanno](https://github.com/noestreich/scanno) und [Schreibo](https://github.com/noestreich/schreibo). Jede App bleibt ein eigenes Repo. Was alle gleich brauchen, steht hier und wird mit fester Version eingebunden.

| Was | Wo | Eingebunden über |
| --- | --- | --- |
| Gestaltung, Sprache, Grundsätze, Duo-Rezept, App-Store-Stolpersteine | `DESIGN.md` | Verweis im Repo der App |
| „Weitere Apps von uns“ | Swift-Paket `AppoFamilie`, Produkt `MoreApps` (`Sources/MoreApps`) | Paket-URL, `branch: v1` |
| Farbwelten, Schriften, Blob, Banner, Fächer-Menü, Statistik-Bausteine | Swift-Paket `AppoFamilie`, Produkt `FamilieUI` (`Sources/FamilieUI`) | Paket-URL, `branch: v1` |
| Paket-Tests (Linux) | `.github/workflows/swift-tests.yml` | `uses: …@v1` |
| iOS-Build mit Xcode 27.1 | `.github/workflows/ios-build.yml` | `uses: …@v1` |
| Screenshots iPhone und iPhone Duo | `.github/workflows/screenshots.yml` | `uses: …@v1` |
| App-Store-Bilder (6,9", Duo innen und außen, Watch) | `.github/workflows/appstore.yml` | `uses: …@v1` |
| App-Icon | `scripts/make_icon.py` | lokal aufrufen |
| App-Store-Rahmen | `scripts/appstore_frames.py` + `docs/appstore/frames.json` der App | lokal aufrufen |
| Webseite (Vorlage, Gestaltung, Skript) | `website/` + `docs/website/site.json` der App | lokal aufrufen, schreibt `docs/website/index.html` |

## Versionen

- **`v1` ist ein Branch**, kein Tag: Workflows (`@v1`) und Swift-Paket (`branch: v1`) folgen ihm. Gearbeitet wird auf `main`; ist eine Änderung in einer App erprobt, wird `v1` per Fast-Forward nachgezogen (`git push origin main:v1`, kein Force-Push). Die Cloud-Sitzungen dürfen keine Tags pushen, Branches schon – deshalb so.
- **In `v1` nur Verträgliches:** Neue Angaben sind optional, Ordner und Namen bleiben. Muss eine App ihren Aufruf ändern (neue Pflichtangabe, andere Ordner, umbenannte Typen), entsteht `v2`, und die Apps ziehen nacheinander um.
- **Neues ausprobieren:** in einer App `@main` bzw. `branch: main` (oder ein eigener Branch) statt `v1` eintragen, prüfen, `v1` nachziehen und die App zurück auf `v1` stellen.
- **Feste Versionen** (`1.0.0` …) gibt es nur, wenn sie jemand auf GitHub als Release anlegt. Nötig sind sie nicht.

## Einbinden in eine App

### Swift-Paket (`project.yml`)

```yaml
packages:
  AppoFamilie:
    url: https://github.com/noestreich/appo-familie
    branch: v1
targets:
  MeineApp:
    dependencies:
      - package: AppoFamilie
        product: MoreApps
```

In den Einstellungen ganz unten `MoreAppsSection(developerID: 776255936)`. Optionen: `additionalAppIDs`, `title`, `country`, `excludingBundleID`, `showsScreenshots`. Der „Laden“-Knopf nimmt die Akzentfarbe (`tint`) der App.

`FamilieUI` kommt genauso dazu (`product: FamilieUI`), und zwar an jedes Target, das Farbe oder Schrift braucht – auch Widget und Teilen-Erweiterung. Jede Datei, die die Bausteine nutzt, braucht `import FamilieUI`. Was in der App bleibt:

```swift
import FamilieUI

extension AppTheme {
    /// Standard-Farbwelt der App
    static let standard: AppTheme = .ultramarine
}
```

- An der Wurzel (App und Teilen-Erweiterung) `.environment(\.theme, theme)` und `.environment(\.typeface, typeface)` setzen. Gelesen wird aus der App Group der App (`AppTheme.storageKey`, `Typeface.storageKey`), damit Widget und Erweiterungen mitlesen.
- Einstellungen: `ForEach(AppTheme.choices(standard: .standard))` – die eigene Farbwelt zuerst.
- App-Icon: `theme.appIconName(standard: .standard)` ergibt `AppIcon-<farbwelt>` (Kaufo hat eigene Namen).
- Blob mit Fächer: `BlobMenu(isExpanded:items:…, onHoldStart:onHoldEnd:)`, die Einträge als `FanItem(title:symbol:action:)`. Was Halten tut und die VoiceOver-Texte (`title`, `holdTitle`, `holdHint`, `stopTitle`, `holdsWhileBusy`) sind Angaben der App. Wer den Blob selbst anordnet, nimmt `BlobFan` und `BlobButton`.
- Logo: `BlobLogo(size:symbol:)` mit `.checkmark` (Kaufo), `.document` (Scanno), `.pencil` (Schreibo) oder einem SF-Symbol-Namen.
- Banner: `BannerView(banner:onTap:)`, `Banner(text:isWarning:symbol:showsDetail:actionTitle:action:)`.
- Statistik: `StatCard(title:symbol:) { … }`, `StatTile(value:label:)`, `RankedBars(rows:color:showsShare:format:)` mit `RankedBars.Row`.

### CI (`.github/workflows/ci.yml`)

```yaml
name: CI
on:
  push:
  pull_request:
concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true
jobs:
  core:
    uses: noestreich/appo-familie/.github/workflows/swift-tests.yml@v1
    with:
      package-path: Packages/SchreiboCore
  ios:
    uses: noestreich/appo-familie/.github/workflows/ios-build.yml@v1
    with:
      project: Schreibo.xcodeproj
      scheme: Schreibo
      product-prefix: Schreibo
    secrets: inherit
```

### Screenshots (`.github/workflows/screenshots.yml`)

Szenen: eine Zeile pro Bild, `<szene> <sekunden> <dateiname> [weitere Startargumente]`, gestartet mit `-demo -demoScene <szene>`. `appearance dark` bzw. `appearance light` schaltet um, Zeilen mit `#` werden übersprungen. `copy <pfad im container> <dateiname>` holt eine Datei aus dem Datencontainer der App zu den Bildern (Kaufo: das Protokoll „Was wurde gelesen?“), sie wird mit committet. Erst die Szenen fürs Außendisplay (zugeklappt), dann die inneren (aufgeklappt quer).

```yaml
name: Screenshots
# Nur per Hand starten (Actions → Screenshots → Run workflow): vor einer neuen Version wie 1.4,
# nicht für Korrekturen wie 1.4.1. Ein Lauf kostet 15–25 Minuten und ändert die Bilder im Repo.
on:
  workflow_dispatch:
concurrency:
  group: screenshots-${{ github.ref }}
  cancel-in-progress: true
jobs:
  screenshots:
    uses: noestreich/appo-familie/.github/workflows/screenshots.yml@v1
    permissions:
      contents: write
    with:
      project: Schreibo.xcodeproj
      scheme: Schreibo
      app-name: Schreibo
      bundle-id: de.ncls.schreibo
      iphone-scenes: |
        today 10 01-heute
        menu 8 02-menue
        appearance dark
        today 10 19-heute-dunkel
      duo-outer-scenes: |
        today 10 34-duo-aussen
      duo-inner-scenes: |
        today 10 30-duo-doppelseite
        note 10 31-duo-notiz
    secrets: inherit
```

Weitere Angaben: `warmup-scene` (Standard `today`), `warmup-seconds` (Standard 60), `app-files` (Dateien aus dem Repo in den Datencontainer der App, eine Zeile `<pfad im repo> <pfad im container>`, z. B. `docs/testdata/einkaufszettel.jpg Documents/demo-note.jpg`), `iphone-types`, `location` (leer = keiner), `output-dir` (Standard `docs/screenshots`), `max-size` (Standard 1100), `commit`.

### App-Store-Bilder (`.github/workflows/appstore.yml`)

```yaml
name: App-Store-Screenshots
# Nur per Hand starten: Ein Lauf kostet 20–50 Minuten und ändert die Bilder im Repo.
on:
  workflow_dispatch:
concurrency:
  group: appstore-${{ github.ref }}
  cancel-in-progress: true
jobs:
  appstore:
    uses: noestreich/appo-familie/.github/workflows/appstore.yml@v1
    permissions:
      contents: write
    with:
      project: Schreibo.xcodeproj
      scheme: Schreibo
      app-name: Schreibo
      bundle-id: de.ncls.schreibo
      iphone-scenes: |
        today 10 01-heute
        appearance dark
        today 10 10-dunkel
      duo-outer-scenes: |
        today 10 01-aussen
      duo-inner-scenes: |
        today 10 01-doppelseite
        appearance dark
        today 10 04-dunkel
      watch-app: SchreiboWatch
      watch-bundle-id: de.ncls.schreibo.watchkitapp
      watch-scenes: |
        10 watch-1-heute
    secrets: inherit
```

`warmup-scene`, `warmup-seconds`, `app-files`, `iphone-types` und `location` wie bei den Screenshots. Ergebnis in `docs/appstore/raw/`, `raw-duo/`, `raw-duo-aussen/` und `watch/`. Ersetzt wird nur, was der Lauf neu aufgenommen hat. Watch-Szenen: `<sekunden> <dateiname> [Startargumente nach -demo]`.

### Rahmen und Icon (lokal)

```bash
git clone https://github.com/noestreich/appo-familie ../appo-familie   # einmal
python3 ../appo-familie/scripts/appstore_frames.py                     # liest docs/appstore/frames.json
python3 ../appo-familie/scripts/make_icon.py AppIcon.png 2A3FD6 FF6B5B FBF4E6 stift
```

`frames.json` enthält die Farben der Standard-Farbwelt und die Überschriften je Bild (Aufbau oben im Skript). Bilder, deren Name auf „dunkel“ endet, bekommen den dunklen Hintergrund. Python 3 mit Pillow.

### Webseite (lokal)

```bash
python3 ../appo-familie/website/make_website.py   # liest docs/website/site.json, schreibt docs/website/index.html
```

Aufbau und Gestaltung stehen in `website/vorlage.html` und `website/stil.css`, die Symbole der Funktionskarten in `website/symbole.json`. Die App bringt in `docs/website/site.json` nur ihre Standard-Farbwelt (hell und dunkel), ihr Zeichen (`haken`, `blatt`, `stift`), ihre Texte und die Pfade ihrer Bilder mit (Aufbau oben im Skript). Die Bilder kommen aus `docs/appstore/raw…/`, das Skript verkleinert sie auf JPEG mit 660 Pixel Breite und bettet sie per base64 ein. Impressum, Kontakt und die gemeinsamen Teile der Datenschutzerklärung (Verantwortlicher, „Weitere Apps von uns“, „Diese Webseite“) stehen in der Vorlage. Adresse und Veröffentlichung der Seite bleiben, wie sie sind: Die Datei liegt weiter im Repo der App.

Ändert sich die Vorlage, werden alle drei Seiten in derselben Sitzung neu erzeugt und committet.

## Öffentlich oder privat

Das Repo ist öffentlich gedacht: Es enthält nichts Geheimes, und öffentliche wiederverwendbare Workflows und Pakete brauchen weder Token noch Freigaben. Wird es doch privat:

1. In appo-familie unter *Settings → Actions → General → Access* „Accessible from repositories owned by the user“ wählen.
2. In jeder App ein Secret `FAMILIE_TOKEN` anlegen (Fine-grained Token, nur appo-familie, *Contents: Read*). Die Workflows tragen es per `git config url.insteadOf` ein, damit auch der Swift Package Manager das Paket laden kann. Deshalb `secrets: inherit` in jedem Aufruf.
