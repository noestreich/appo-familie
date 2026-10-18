# App-Familie

Gemeinsame Regeln und Bausteine für die iOS-Apps [Kaufo](https://github.com/noestreich/einkauf), [Scanno](https://github.com/noestreich/scanno) und [Schreibo](https://github.com/noestreich/schreibo). Jede App bleibt ein eigenes Repo. Was alle gleich brauchen, steht hier und wird mit fester Version eingebunden.

| Was | Wo | Eingebunden über |
| --- | --- | --- |
| Gestaltung, Sprache, Grundsätze, Duo-Rezept, App-Store-Stolpersteine | `DESIGN.md` | Verweis im Repo der App |
| „Weitere Apps von uns“ | Swift-Paket `AppoFamilie`, Produkt `MoreApps` (`Sources/MoreApps`) | Paket-URL, `branch: v1` |
| Paket-Tests (Linux) | `.github/workflows/swift-tests.yml` | `uses: …@v1` |
| iOS-Build mit Xcode 27.1 | `.github/workflows/ios-build.yml` | `uses: …@v1` |
| Screenshots iPhone und iPhone Duo | `.github/workflows/screenshots.yml` | `uses: …@v1` |
| App-Store-Bilder (6,9", Duo innen und außen, Watch) | `.github/workflows/appstore.yml` | `uses: …@v1` |
| App-Icon | `scripts/make_icon.py` | lokal aufrufen |
| App-Store-Rahmen | `scripts/appstore_frames.py` + `docs/appstore/frames.json` der App | lokal aufrufen |

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

Szenen: eine Zeile pro Bild, `<szene> <sekunden> <dateiname> [weitere Startargumente]`, gestartet mit `-demo -demoScene <szene>`. `appearance dark` bzw. `appearance light` schaltet um, Zeilen mit `#` werden übersprungen. Erst die Szenen fürs Außendisplay (zugeklappt), dann die inneren (aufgeklappt quer).

```yaml
name: Screenshots
on:
  workflow_dispatch:
  push:
    paths:          # nur wenn sich die App ändert – nicht, wenn sich nur dieser Aufruf ändert
      - "App/**"
      - "Packages/**"
      - "project.yml"
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

Weitere Angaben: `warmup-scene` (Standard `today`), `iphone-types`, `location`, `output-dir` (Standard `docs/screenshots`), `max-size` (Standard 1100), `commit`.

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

Ergebnis in `docs/appstore/raw/`, `raw-duo/`, `raw-duo-aussen/` und `watch/`. Ersetzt wird nur, was der Lauf neu aufgenommen hat. Watch-Szenen: `<sekunden> <dateiname> [Startargumente nach -demo]`.

### Rahmen und Icon (lokal)

```bash
git clone https://github.com/noestreich/appo-familie ../appo-familie   # einmal
python3 ../appo-familie/scripts/appstore_frames.py                     # liest docs/appstore/frames.json
python3 ../appo-familie/scripts/make_icon.py AppIcon.png 2A3FD6 FF6B5B FBF4E6 stift
```

`frames.json` enthält die Farben der Standard-Farbwelt und die Überschriften je Bild (Aufbau oben im Skript). Bilder, deren Name auf „dunkel“ endet, bekommen den dunklen Hintergrund. Python 3 mit Pillow.

## Öffentlich oder privat

Das Repo ist öffentlich gedacht: Es enthält nichts Geheimes, und öffentliche wiederverwendbare Workflows und Pakete brauchen weder Token noch Freigaben. Wird es doch privat:

1. In appo-familie unter *Settings → Actions → General → Access* „Accessible from repositories owned by the user“ wählen.
2. In jeder App ein Secret `FAMILIE_TOKEN` anlegen (Fine-grained Token, nur appo-familie, *Contents: Read*). Die Workflows tragen es per `git config url.insteadOf` ein, damit auch der Swift Package Manager das Paket laden kann. Deshalb `secrets: inherit` in jedem Aufruf.
