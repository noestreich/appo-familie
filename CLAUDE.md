# App-Familie – Hinweise für die Arbeit am Code

Gemeinsame Regeln (`DESIGN.md`), wiederverwendbare Workflows (`.github/workflows/`), Skripte (`scripts/`) und das Swift-Paket `AppoFamilie` (`Sources/`) für Kaufo ([noestreich/einkauf](https://github.com/noestreich/einkauf)), Scanno ([noestreich/scanno](https://github.com/noestreich/scanno)) und Schreibo ([noestreich/schreibo](https://github.com/noestreich/schreibo)). Einbinden und Versionen: `README.md`.

## Arbeitsweise

- Kommentare, Commit-Nachrichten und Doku auf Deutsch, du-Form. Keine Emojis.
- `DESIGN.md` ist die einzige Quelle der Familienregeln. Die Apps verweisen nur hierher; Regeln werden hier geändert und nicht in die Apps kopiert.
- **Erst in einer App erproben, dann hierher verschieben.** Ein Baustein kommt ins Paket oder in einen Workflow, wenn er in einer App läuft und mindestens eine zweite ihn braucht. Dann in derselben Sitzung alle Apps umstellen, damit keine auf einer Kopie sitzen bleibt.
- Ins Paket gehört nur, was in allen Apps gleich aussieht und sich gleich verhält. Unterschiede werden Parameter, keine Abzweigungen nach App-Namen.
- Bei Unklarheit nach der Absicht fragen. Offensichtliche Entscheidungen selbst treffen und kurz erwähnen.

## Versionen

- `v1` ist ein **Branch**, dem Workflows (`@v1`) und Swift-Paket (`branch: v1`) folgen. Gearbeitet wird auf `main`.
- Änderungen zuerst in einer App mit `@main` bzw. `branch: main` prüfen, dann `v1` per Fast-Forward nachziehen: `git push origin main:v1`. Nie mit Force auf `v1` pushen.
- In `v1` nur Verträgliches (neue Angaben optional, Ordner und Namen bleiben). Sonst `v2` als neuer Branch, Apps nacheinander umstellen.
- Tags kann die Cloud-Sitzung nicht pushen (der Git-Proxy lässt nur Branches durch). Feste Versionen legt bei Bedarf der Nutzer als Release auf GitHub an.

## Bauen und prüfen

- In der Cloud-Sitzung gibt es kein Xcode und kein Swift. Der eigene Workflow `Prüfen` (`check.yml`) prüft die Workflows mit `actionlint`, die Skripte mit Python und baut das Paket für macOS und den iOS-Simulator. Ob die Workflows wirklich tun, was sie sollen, zeigt erst die CI einer App, die sie aufruft.
- Das Paket ist für Oberflächenbausteine da (SwiftUI) und muss nicht unter Linux bauen. Plattformunabhängige Logik bleibt im eigenen Core-Paket jeder App. UIKit und StoreKit hinter `#if canImport(UIKit)`, damit der macOS-Build durchläuft.
- macOS-Jobs laufen auf `xcode-27` mit `DEVELOPER_DIR=/Applications/Xcode_27.1.app/Contents/Developer`. Warum jeder Schritt in den Screenshot-Workflows so ist, wie er ist, steht in `DESIGN.md` („Rezept: Duo-Build und Duo-Screenshots …“). Daran nichts „vereinfachen“, ohne es in einer App zu prüfen.
- CI sparsam nutzen: Ein Screenshot-Lauf kostet 15–25 Minuten, ein App-Store-Lauf 20–50. Änderungen an den Bild-Workflows in einer App prüfen und dabei mehrere Änderungen in einem Lauf sammeln.
- Skripte lokal prüfen: `python3 scripts/appstore_frames.py --config <app>/docs/appstore/frames.json --root <kopie von docs/appstore>` und mit den Bildern der App vergleichen.

## Nicht vergessen

- Neue Bausteine in `README.md` (Tabelle und Einbinden) und in `DESIGN.md` („Bausteine“) eintragen.
- Webseiten immer gemeinsam ändern: neuer Abschnitt oder neue Gestaltung in allen Apps zugleich (`DESIGN.md`, „Webseite“).
- Keine Markennamen in App-Store-Schlüsselwörtern, keine fremden Logos.
