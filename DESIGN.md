# Gestaltung und Grundsätze der App-Familie

Dieses Dokument beschreibt, wie Apps dieser Familie aussehen, klingen und gebaut werden. Zur Familie gehören Kaufo ([noestreich/einkauf](https://github.com/noestreich/einkauf), die erste App und das Referenzbeispiel), Scanno ([noestreich/scanno](https://github.com/noestreich/scanno)) und Schreibo ([noestreich/schreibo](https://github.com/noestreich/schreibo)).

**Diese Datei ist die einzige Quelle.** Sie liegt in [noestreich/appo-familie](https://github.com/noestreich/appo-familie); die Apps haben statt einer eigenen Kopie nur einen kurzen Verweis hierher plus ihr `KONZEPT.md` für das, was nur sie betrifft. Familienregeln werden hier geändert, nicht in den Apps.

Jede App bleibt ein eigenständiges Repo mit eigenem Projekt, eigener CI und eigenen Releases. Was alle gleich brauchen, kommt aus appo-familie, und zwar mit festen Versionen:

- **Workflows** (`.github/workflows/`): als wiederverwendbare Workflows, eingebunden mit `uses: noestreich/appo-familie/.github/workflows/<datei>@v1`.
- **Swift-Paket** `AppoFamilie`: Produkte `MoreApps` und `FamilieUI` (Farbwelten, Schriften, Blob, Banner, Fächer-Menü, Statistik-Bausteine), eingebunden über die Paket-URL mit `branch: v1`.
- **Skripte** (`scripts/`): App-Icon und App-Store-Rahmen, gesteuert über eine Konfigurationsdatei in der App.

Gearbeitet wird in appo-familie auf `main`; die Apps folgen dem Branch `v1`, der nur nach Erprobung in einer App nachgezogen wird. Neue Bausteine werden zuerst in einer App erprobt und erst danach hierher verschoben (siehe `CLAUDE.md` in appo-familie).

## Haltung

- **Vanilla iOS mit kräftigen Akzentfarben.** Systemkomponenten (List, Form, Toolbar, Sheets, Menüs), keine nachgebauten Bedienelemente. Persönlichkeit kommt über Farbe, Typografie und den Blob.
- **Keine Emojis** – weder in der Oberfläche noch in Texten. Symbole sind SF Symbols.
- **Saubere Typografie, freundlicher Ton.** Kurze Sätze, du-Form, keine Ausrufezeichen-Flut.
- **Ein großer, ungewöhnlicher Hauptknopf** pro App (bei Kaufo der Blob). Er ist zugleich Logo und App-Icon.
- **So schlank wie möglich.** Neue Funktionen landen zuerst in vorhandenen Menüs („Mehr“, Einstellungen, Fächer-Menü des Blobs), nicht als neue Knöpfe. Eigene Unterseiten nur, wenn es sich lohnt (z. B. Statistik).
- **Alles auf dem Gerät.** Texterkennung (Vision), Sprache (SFSpeechRecognizer on-device), Sprachmodell (Foundation Models). Kein eigener Server, kein Konto, keine Analyse, keine Werbung.
- **Teilen nur über iCloud** des Nutzers (CloudKit). Gemeinsame Nutzung heißt **„Haushalt“**, nie „Familie“ – passt auch für Paare und WGs und verwechselt sich nicht mit Apples Familienfreigabe.
- **Fehlertolerant und ehrlich.** Was die App korrigiert, bleibt sichtbar (Kaufo: „Tomaten (Tomatn)“, antippen für das Original). Unsicheres wird dezent markiert, nicht versteckt. Ein „Was wurde gelesen?“-Protokoll erklärt, was die Automatik getan hat.
- **Lernt still mit.** Korrekturen, Zuordnungen und Gewohnheiten werden gemerkt und beim nächsten Mal angeboten, ohne nachzufragen.

## Sprache und Begriffe

- Oberfläche komplett Deutsch, du-Form.
- „Einfach diktieren“ statt „sagen“ oder „sprechen“.
- „Haushalt teilen“, „Haushalt verlassen“, „Haushalt von …“.
- „Erledigte ausblenden“, „Alles erledigt“, „Alles im Wagen!“ – freundlich, kurz.
- Fehlermeldungen sagen, was zu tun ist („Bitte erlaube … in den Einstellungen.“), nicht was kaputt ist.
- Commit-Nachrichten, Code-Kommentare und Doku ebenfalls Deutsch.

## Farbe

Fünf Farbwelten, wählbar in den Einstellungen, jede mit Akzent, Partner (zweite Farbe des Blob-Verlaufs), Fläche und Karte. Jede App startet mit ihrer eigenen Farbwelt, damit die Apps auf dem Home-Bildschirm unterscheidbar bleiben: Kaufo mit Tomatenrot & Creme, Scanno mit Himbeere & Koralle, Schreibo mit Ultramarin & Koralle. In dieser Farbwelt sind auch das Haupt-Icon der App und die Einstellung beim ersten Start. Werte als Hex, hell / dunkel (Quelle: `Sources/FamilieUI/Farbwelt.swift`):

| Farbwelt | Akzent | Partner | Fläche |
| --- | --- | --- | --- |
| Tomatenrot & Creme (Standard in Kaufo) | E0442E / FF5F47 | FF8A3D / FF9A55 | FBF4E6 / 1A1513 |
| Himbeere & Koralle (Standard in Scanno) | D63862 / FF6B8F | FF8A66 / FF9A7A | FCF2EF / 1C1214 |
| Ultramarin & Koralle (Standard in Schreibo) | 2A3FD6 / 6B7CFF | FF6B5B / FF7F70 | F3F4FC / 111324 |
| Kräutergrün & Zitrone | 23864F / 3FBF72 | F2CF2E / F5D84A | F6F8EC / 121812 |
| Aubergine & Minze | 5E2B73 / B27AD0 | 4FD1A5 / 6FE0B8 | F6F1F7 / 18121B |

Karten: FFFFFF / 24201E. Dunkelmodus ist eine eigene, gewählte Variante, keine automatische Umkehrung.

Alle Apps bieten alle fünf in derselben Reihenfolge an, der Reihenfolge der Tabelle (`AppTheme.allCases`). Die eigene Standard-Farbwelt rückt dabei nicht nach vorn. Neue Farbwelten kommen ins Paket und damit in alle Apps zugleich, samt Icon je App. Neue Farbwelten brauchen einen Akzent mit mindestens 4:1 Kontrast zu Weiß (wie Tomatenrot), besser 4,5:1.

Regeln:
- Der Akzent färbt Haken, Hauptaktionen, Abschnittsköpfe und `tint`. Text bleibt in Primär-/Sekundärfarbe, nie in Akzentfarbe für Fließtext.
- Farben, die eine Sache kennzeichnen (Listen, Läden), folgen der Sache, nicht ihrem Rang. Sehr helle Farben (Gelb) bekommen eine dunklere „lesbare“ Variante für Schrift (`ListTint.readable`), dunkle eine aufgehellte für den Dunkelmodus (`Color.adaptive`).
- Keine Logos fremder Marken – nur an Markenfarben angelehnte Paletten.

## Typografie

Sieben Schriften, alle in iOS enthalten, alle skalieren mit der dynamischen Textgröße (Quelle: `Sources/FamilieUI/Schrift.swift`):

Klar (SF Pro, Überschriften gerundet, Standard) · Rund (SF Rounded) · Klassisch (New York) · Handschrift (Noteworthy) · Filzstift (Marker Felt) · Kreide (Chalkboard SE) · Schreibmaschine (American Typewriter).

- Alle Texte über `.appFont(_:weight:heading:)`, damit die gewählte Schrift überall gilt (auch in Widgets und Erweiterungen).
- `heading: true` für Titel, Überschriften und große Zahlen.
- Große Zahlen (Zähler, Statistik) mit `.monospacedDigit()` und `.contentTransition(.numericText())`.

## Der Blob

Organische, langsam atmende Form aus 9 Punkten auf einem Kreis, Radius verformt durch drei Sinuswellen, verbunden per Catmull-Rom-Spline (Quelle: `Sources/FamilieUI/Blob.swift`, gleiche Formel in `scripts/make_icon.py`):

```
offset(a, t) = 0.055·sin(3a + 0.9t) + 0.035·sin(5a − 1.3t) + 0.025·sin(2a + 0.55t)
r = 0.88 · halbe Kantenlänge · (1 + wobble · offset)
```

- Füllung: Verlauf Akzent → Partner (oben links nach unten rechts).
- Hauptknopf unten rechts, 80 pt. **Tippen** öffnet ein Fächer-Menü (Kapseln mit Symbol und Text, gestaffelt animiert), **Halten** startet direkt die Hauptaktion (bei Kaufo: Diktat). Während des Zuhörens schwingt der Blob mit der Lautstärke.
- Was Halten tut und die VoiceOver-Texte gibt die App dem `BlobButton` bzw. `BlobMenu` mit.
- Als Logo (`BlobLogo`) mit dem weißen Zeichen der App (`BlobSymbol`: `.checkmark`, `.document`, `.pencil`) in leeren Zuständen, Ladeanzeigen und im Onboarding.
- App-Icon: derselbe Blob auf Creme (FBF4E6) in der Standard-Farbwelt der App, darin ein einziges, kräftiges weißes Zeichen (Kaufo: Haken, Scanno: gefülltes Blatt mit Textzeilen, Schreibo: Stift). Keine dünnen Linien, Rahmen oder Kleinteile. Je Farbwelt ein eigenes Icon mit heller und dunkler Variante (dunkel: aufgehellte Farben auf der dunklen Fläche der Farbwelt), erzeugt per `scripts/make_icon.py --all`. Das Icon wechselt mit der gewählten Farbwelt (`setAlternateIconName`).

## Muster, die jede App mitbringt

- **Onboarding** mit kurzer Begrüßung (drei Merkmale mit Symbol, darunter der wichtigste Bedienhinweis) und einer echten Auswahl, die die App sofort einrichtet (Kaufo: bis zu drei Läden).
- **Leere Zustände** mit BlobLogo, einem Satz Überschrift und einem Satz Anleitung.
- **Banner oben** für Rückmeldungen („8 Artikel hinzugefügt“), optional mit einer Aktion („Verschieben“); verschwindet von selbst.
- **Einstellungen** als `Form`: Inhalte → Statistik → Farbe → Schrift → Optionen → Gedächtnis → iCloud/Haushalt → Apple Intelligence → Zurücksetzen → Weitere Apps von uns (`MoreApps`). Zeilen mit eigenen Buttons immer `.buttonStyle(.plain)` + `contentShape`, sonst färbt iOS 26 sie ein.
- **Haptik** bei Erfolgsmomenten (`.sensoryFeedback`), nicht bei jeder Berührung.
- **Barrierefreiheit:** Bedeutung nie nur über Farbe, `accessibilityLabel`/`Value` an eigenen Bedienelementen, dynamische Textgröße.
- **Systemintegration, wo sie Sinn ergibt:** interaktives Widget im Stil der Erinnerungen-App (Listensymbol in Farbe, große Zahl, Kreise zum Abhaken, Liste wählbar), Live-Aktivität für den „unterwegs“-Moment, Steuerelemente für Kontrollzentrum und Action-Button, Teilen-Erweiterung, Apple-Watch-App für das Nötigste.
- **Statistik als Belohnung:** eigene Unterseite, Kennzahlen als große Zahlen, Diagramme mit Swift Charts, ein freundlicher Satz („Am liebsten kaufst du samstags vormittags ein.“). Ranglisten als waagerechte Balken statt Tortendiagramme.

## Technik

- iOS 26 und neuer, Apple Intelligence wo sinnvoll (mit verständlichem Hinweis, wenn nicht verfügbar).
- SwiftUI, SwiftData, App Group für Widget und Erweiterungen, Swift 5 Sprachmodus in App-Targets.
- Plattformunabhängige Logik in einem lokalen Swift-Paket mit Tests (läuft auch unter Linux).
- iCloud: `CKSyncEngine`, eigene Zone pro Haushalt, Teilen als zonenweiter `CKShare`. Änderungen aus Widget und Erweiterungen werden gesammelt und von der App nachgereicht.
- **XcodeGen** (`project.yml`), das Xcode-Projekt ist nicht eingecheckt.
- **GitHub Actions:** Linux-Tests des Pakets, iOS-Build (zeigt gebaute Produkte und Warnungen), Screenshots im Simulator per Demo-Modus, App-Store-Bilder in 1320 × 2868 mit Überschriften. Die Workflows selbst stehen in appo-familie (`swift-tests.yml`, `ios-build.yml`, `screenshots.yml`, `appstore.yml`, `release.yml`); die App ruft sie mit ihren Szenen auf. `Veröffentlichen` (`release.yml`) archiviert, signiert und lädt zu App Store Connect hoch – ebenfalls nur per Hand, eingereicht wird weiter in App Store Connect. Nach einem Lauf `App-Store-Screenshots` legt `appstore-upload.yml` Rahmen und Überschriften um die Bilder und lädt sie in die bearbeitbare Version in App Store Connect; „Nur gestalten und hochladen“ macht das ohne neue Fotos (etwa nach geänderten Überschriften in `frames.json`). `CI` läuft bei jedem Push. `Screenshots` und `App-Store-Screenshots` starten **nur per Hand** (`workflow_dispatch`, kein `push`): einmal vor jeder neuen Version mit neuen Funktionen (1.4), nicht für Korrekturen (1.4.1, 1.4.2).
- **Demo-Modus** (`-demo -demoScene <szene>`): ersetzt die Daten durch feste Beispieldaten, schaltet iCloud ab, öffnet die gewünschte Ansicht. Grundlage für alle Screenshots.

## iPhone Duo (Stand Oktober 2026)

Das iPhone Duo (seit 23. Oktober 2026 im Handel) ist ein aufklappbares iPhone: außen ein 5,4-Zoll-Display wie bei jedem iPhone, innen ein 7,6-Zoll-Display, das sich in Größenklassen wie ein iPad verhält (regulär × regulär). Unsere Apps laufen dort schon jetzt, weil sie iPhone-Apps sind. Die Punkte unten machen sie dort richtig gut. Was jede App schon umgesetzt hat, steht unter „Je App“; dort wird abgehakt. Quelle sind Apples Tech Talks zum iPhone Duo („Prepare your app for iPhone Duo“, „Raise the bar with iPhone Duo“, „Strike a pose with adaptive layouts on iPhone Duo“, „Leverage multiple displays and scenes on iPhone Duo“). API-Namen vor dem Umsetzen mit den Headern des iOS-27.1-SDK abgleichen.

**Was das Gerät ändert**

- Außen: Größenklassen wie bisher. Mit dem iOS-27.1-SDK wandern Navigationsleiste, Toolbar und Tab-Leiste im Hochformat **senkrecht an die Seite** – mehr Platz für Inhalt, Knöpfe in Daumennähe.
- Innen: regulär × regulär, Platz für Seitenleiste und zwei Spalten. Die erlaubten Ausrichtungen gelten innen nicht, die App wird skaliert. Alle Apps nehmen an **Split View** teil (zwei Apps nebeneinander), die Fensterbreite ändert sich also laufend.
- Halb aufgeklappt (wie ein Buch oder aufgestellt): Der Knick ist eine **Trennregion** (`reservedRegions(kind: .division)`), die Frontkamera innen eine Verdeckungsregion. Systemmenüs, Hinweise und Sheets weichen beidem von selbst aus.
- Auf- und Zuklappen startet die App nicht neu, die Szene ändert nur ihre Größe. Wird dabei eine andere Ansicht gezeigt, geht `@State` in der alten verloren.
- Ohne Neukompilieren läuft die App innen in einem zentrierten Fenster. Gebaut mit dem iOS-27-SDK nutzt sie fast das ganze Display, mit dem iOS-27.1-SDK reicht sie bis an den Rand.

**Grundregeln für alle Apps**

- [ ] **SDK und Simulator:** Mit Xcode 27.1 und dem iOS-27.1-SDK bauen, sobald der CI-Runner es hat. Den Simulator „iPhone Duo“ (Device Hub: auf- und zuklappen, drehen, knicken) in die Workflows `CI` und `Screenshots` aufnehmen.
- [ ] **Größenklassen statt Gerät:** Entscheidungen über `horizontalSizeClass` (SwiftUI-Umgebung) treffen, nie über `userInterfaceIdiom`, Ausrichtung oder `UIScreen.main` (wird abgekündigt). Stand: Keine der drei Apps nutzt `UIScreen.main`, aber auch noch keine Größenklassen.
- [ ] **Zustand oberhalb des Umschaltens halten:** Was beim Auf- und Zuklappen erhalten bleiben muss (Kaufo: Eingabe in der Zeile zum Hinzufügen, Scanno: `ScanSession`, Schreibo: Entwurf und Diktat), liegt nicht in `@State` einer Ansicht, die beim Wechsel der Größenklasse ausgetauscht wird.
- [ ] **Systemleisten statt eigener Leisten:** Knöpfe gehören in `.toolbar` eines `NavigationStack`/`NavigationSplitView`, nur dann werden sie außen senkrecht. Jeder Knopf hat Titel **und** SF Symbol (wie bisher `Button("Suchen", systemImage: …)`), weil reine Symbolknöpfe senkrecht passen und das System den Titel im Überlaufmenü zeigt. Schließen bzw. Zurück als `.cancellationAction`, die wichtigste Aktion als `.topBarPinnedTrailing`.
- [ ] **„Mehr“ wird das Überlaufmenü des Systems:** Apple reserviert das Symbol `ellipsis` für den Überlauf. Unser „Mehr“-Menü zieht deshalb in `ToolbarOverflowMenu` um. Dort landen auch Knöpfe, die außen im Querformat keinen Platz finden – das passt zu „Neues zuerst in vorhandene Menüs“. Vor iOS 27 bleibt es beim bisherigen Menü. Häufige Aktionen bekommen `.visibilityPriority(.high)`, damit sie zuletzt überlaufen.
- [ ] **Blob und eigene Überlagerungen:** Der Blob (unten rechts, 80 pt), Banner und Kaufos Listen-Reiter sind eigene Oberfläche. Sie bleiben im sicheren Bereich und vertragen ungleiche Ränder; Breiten nie als „Breite minus 2 × linker Rand“ rechnen. Mit `@Environment(\.toolbarVerticalEdge)` prüfen, ob die senkrechte Leiste auf der Seite des Blobs liegt. Wenn ja, rückt der Blob nach innen, er wandert nicht auf die andere Seite – der Daumen soll ihn am gewohnten Ort finden. Auf dem halb aufgeklappten Gerät nie über dem Knick.
- [ ] **Innen zwei Spalten, wo es eine Haupt- und eine Detailansicht gibt:** `NavigationSplitView` statt `NavigationStack` bei regulärer Breite – klappt zugeklappt von selbst zu einem Stapel zusammen. Halb aufgeklappt teilt der Knick die Spalten gleichmäßig. Nichts Wichtiges mittig über den Knick legen; lange Texte, Listen und Dokumente nicht verschieben, nur weil sich der Knick bewegt.
- [ ] **Sheets:** Sie erscheinen innen mittig. Feste Höhen und Detents (`.medium`) auf dem großen Display prüfen. Fenster mit eigener Ansicht im Sheet nicht verpacken – das schließt sich sonst gleich wieder (in Schreibo beim Export passiert, jetzt mit `.fileExporter`).
- [ ] **Abgerundete Flächen am Bildschirmrand:** Wo eine Karte oder Leiste bis an den Rand reicht, `ConcentricRectangle` statt fester Eckenradien, damit sie zu den Ecken des jeweiligen Displays passt. Karten mitten im Inhalt behalten 22 pt.
- [ ] **Kamera über Systemkomponenten:** `VNDocumentCameraViewController`, `UIImagePickerController` und `PhotosPicker` wählen die richtige Kamera selbst – auch die Rückkamera, die beim Aufklappen zum Nutzer zeigt. Eigene `AVCaptureSession` vermeiden; falls doch, `AVCaptureDeviceDirectionCoordinator` nutzen.
- [ ] **Screenshots und App Store:** Demo-Szenen auch im Duo-Simulator aufnehmen, außen und innen. App Store Connect hat eigene Fächer: außen 1398 × 2034, innen 2007 × 2853 (jeweils auch quer). Bis April 2027 freiwillig, danach Pflicht für Apps mit iOS-27.1-SDK; mit Bildern zeigt die Produktseite den Hinweis „für iPhone Duo optimiert“. `scripts/appstore_frames.py` bekommt beide Größen, die Webseite ein Bild vom inneren Display.

**Rezept: Duo-Build und Duo-Screenshots, die beim ersten Lauf klappen (erprobt in Schreibo, Oktober 2026)**

Schreibo hat dafür rund 15 Läufe gebraucht. Mit den Schritten unten reicht einer. **Am einfachsten gar nicht selbst bauen:** Die Workflows `ios-build.yml`, `screenshots.yml` und `appstore.yml` in appo-familie enthalten alle Schritte; die App gibt nur Projekt, Schema, Bundle-ID und ihre Szenen an (Beispiele in der README von appo-familie). Die Schritte unten erklären, warum die Workflows so aussehen – wichtig, wenn etwas bricht.

*1. Runner und Xcode.* Das Image `macos-26` hat höchstens Xcode 26.6 – damit gibt es kein iOS-27.1-SDK und keinen Duo-Simulator. GitHub führt Xcode 27 auf einem eigenen Image; dort ist 27.0 Standard, 27.1 liegt daneben. Jeder macOS-Job (auch `CI`):

```yaml
runs-on: xcode-27
env:
  DEVELOPER_DIR: /Applications/Xcode_27.1.app/Contents/Developer
```

Ziel bleibt iOS 26. Das Image bringt keine fertigen Simulatoren mit, also immer `xcrun simctl create`. Mit Xcode 27 neu als Warnung: `GenerationOptions(sampling:)` heißt jetzt `samplingMode:`.

*2. Laufzeiten.* `xcodebuild -downloadPlatform iOS` lädt iOS 27.1 (7,85 GB, rund zwei Minuten). **Diese Laufzeit nimmt nur das iPhone Duo an** – iPhone 16, 17 und 18 Pro brechen mit „Incompatible device“ ab, `supportedDeviceTypes` ist leer. Normale iPhones daher auf der vorinstallierten Laufzeit 27.0 anlegen; die App ist trotzdem mit dem 27.1-SDK gebaut. Bewährt: Laufzeiten und Gerätetypen der Reihe nach probieren und nur eine echte UUID als Ergebnis akzeptieren – `simctl create` schreibt seine Fehlermeldung sonst in die Variable:

```bash
UDID=""
for rt in $(xcrun simctl list runtimes -j | python3 -c "import json,sys; print(' '.join(r['identifier'] for r in reversed(json.load(sys.stdin)['runtimes']) if r['platform']=='iOS' and r['isAvailable']))"); do
  for t in iPhone-18-Pro-Max iPhone-17-Pro-Max; do
    out=$(xcrun simctl create "App Pro Max" "com.apple.CoreSimulator.SimDeviceType.$t" "$rt" 2>&1) || continue
    if echo "$out" | grep -qE '^[0-9A-F-]{36}$'; then UDID="$out"; break 2; fi
  done
done
test -n "$UDID"
DUO=$(xcrun simctl create "App Duo" com.apple.CoreSimulator.SimDeviceType.iPhone-Duo com.apple.CoreSimulator.SimRuntime.iOS-27-1)
```

Einmal bauen (`-destination "id=$UDID"`) und dieselbe `.app` auf beide Simulatoren installieren. Beim Hochfahren meldet das Duo „Data Migration Failed“ – harmlos, deshalb `xcrun simctl bootstatus "$DUO" -b || true`. Die Statusleiste lässt sich wie gewohnt mit `status_bar … override` auf 9:41 setzen.

*3. Auf- und zuklappen.* `simctl` kann das nicht, auch `simctl ui` kennt keine Haltung. Ohne Zutun startet das Duo mal auf-, mal zugeklappt – die Bilder sind dann Glückssache. Den Klappwinkel setzt das Werkzeug `hinge` (MIT, nutzt eine private Schnittstelle des Simulators; nur im Workflow, nie in der App):

```bash
brew install artemnovichkov/tap/hinge
hinge -d "$DUO" close    # Außendisplay (nicht „closed“ – das zeigt nur die Hilfe, ohne dass der Schritt scheitert)
hinge -d "$DUO" open     # inneres Display, flach
hinge -d "$DUO" get      # aktueller Winkel, zum Prüfen im Log
```

Danach fünf Sekunden warten und die App neu starten (`terminate` + `launch`), damit sie im neuen Fenster aufbaut.

*4. Das richtige Display fotografieren.* `simctl io <UDID> screenshot` ohne `--display` nimmt nach dem Klappen oft das gerade **abgeschaltete** Display – das Bild ist dann schwarz (Schreibo zweimal passiert, im App Store unbrauchbar). Immer gezielt wählen, erkannt an der Breite. Das passende Display merken und beim nächsten Bild zuerst probieren: Ein Foto vom abgeschalteten Display kann Minuten hängen (in Schreibo über drei Minuten je Szene). Die Workflows in appo-familie machen das schon; die Kurzform:

```bash
display_shot() {   # $1 Zieldatei, $2 erlaubte Breiten
  for id in $(xcrun simctl io "$DUO" enumerate | awk '/UUID:/{u=$2} /Class: Display/{print u}'); do
    xcrun simctl io "$DUO" screenshot --display="$id" pick.png >/dev/null 2>&1 || continue
    w=$(sips -g pixelWidth pick.png | awk '/pixelWidth/{print $2}')
    case " $2 " in *" $w "*) mv pick.png "$1"; return 0;; esac
  done
  return 1
}
display_shot aussen.png "1398"        # zugeklappt
display_shot innen.png "2853 2007"    # aufgeklappt
```

*5. Maße und Verhältnis.* Was der Simulator liefert, passt ohne Umrechnen in die Fächer von App Store Connect:

| Bild | Pixel | Seitenverhältnis | Hinweis |
| --- | --- | --- | --- |
| iPhone 6,9" (Pro Max) | 1320 × 2868 | 0,46 | wie bisher, Gerät auf Laufzeit 27.0 |
| Duo außen | 1398 × 2034 | 0,69 | hochkant, Leisten stehen rechts senkrecht |
| Duo innen | 2853 × 2007 | 1,42 | **quer** – aufgeklappt liegt das Duo wie ein Buch; App Store Connect nimmt quer und hochkant (2007 × 2853) |
| Apple Watch | 410 × 502 | – | Laufzeit kostet rund 20 Minuten, siehe 7 |

Für `docs/screenshots/` auf 1100 Pixel lange Seite verkleinern (`sips -Z 1100`), wie bisher.

*6. Welche Bilder sich lohnen.* Pro App vier innen und eins außen reicht:

- innen das Herzstück zweispaltig (Kaufo: Seitenleiste mit Listen + Liste, Scanno: Scans + Dokument, Schreibo: Doppelseite), dazu Detail rechts geöffnet, eine zweite Ansicht und dunkel;
- außen die Startansicht – sie zeigt die senkrechte Leiste und dass der Hauptknopf frei bleibt.

Reihenfolge im Workflow: hochfahren, App einmal starten und 60 Sekunden warten (Systemmitteilungen), **zuerst zugeklappt** außen fotografieren, dann aufklappen und die inneren Szenen. Jede Szene per `-demo -demoScene …` frisch starten. Demo-Szenen, die Detail oder Kalender öffnen, müssen im Demo-Code über dieselbe Funktion gehen wie ein Tipp (Schreibo: `open(_:)`), sonst landet innen ein Sheet statt der rechten Spalte. Breit prüfen geht mit dem Duo-Simulator direkt; ein Schalter wie Kaufos `-demoRegular` ist dann nur noch für schnelle Proben nötig.

*7. Apple Watch.* Die watchOS-Laufzeit muss mit Xcode 27.1 ebenfalls geladen werden (`xcodebuild -downloadPlatform watchOS`, rund 20 Minuten), das Watch-Gerät wie oben per Probieren anlegen. Den Schritt `continue-on-error: true` setzen und beim Committen **nur ersetzen, was der Lauf neu aufgenommen hat** – sonst löscht ein fehlgeschlagenes Watch-Bild das alte. Drei Fallen (Schreibo und Kaufo, Oktober 2026): Laufzeiten im JSON von `simctl` mit `.get` lesen – ein Eintrag ohne `platform` ließ den Filter sonst leer ausgehen. Manche Runner haben watchOS 27.0 eingetragen, aber ohne Abbild: `simctl list` führt sie oft sogar als verfügbar, `simctl create` meldet „runtime path not found“, und `-downloadPlatform` lädt nichts nach – scheitert das Anlegen, den Eintrag mit `xcrun simctl runtime delete` löschen und neu laden (rund 20 Minuten). Das Foto der Watch bricht gelegentlich mit „Timeout waiting for screen surfaces“ ab – mehrmals versuchen, App dazwischen neu starten. Der Workflow `appstore.yml` macht das alles.

*8. Rahmen.* `scripts/appstore_frames.py` aus appo-familie, Farben und Überschriften in `docs/appstore/frames.json` der App: `compose(…, size=…, corner=…)` rechnet hochkant wie bisher (Bezug Breite/1320) und quer mit eigener Aufteilung (Bezug Höhe/1650, Bild bis 88 % der Breite, Eckenradius 3,5 % statt 9 %). Ordner `raw-duo` → `framed-duo` (2853 × 2007), `raw-duo-aussen` → `framed-duo-aussen` (1398 × 2034), Überschriften unter `duo_captions` und `duo_outer_captions`. Rahmen lokal erzeugen, nicht in der CI.

*9. CI sparsam nutzen.* Ein `Screenshots`-Lauf mit Duo dauert 15–25 Minuten, `App-Store-Screenshots` 20–30 Minuten plus 20 für die Watch.

- Beide Bildläufe nur per Hand starten, nie bei `push`: vor einer neuen Version (1.4) erst `Screenshots`, dann `App-Store-Screenshots`. Bei Korrekturversionen (1.4.1) keinen Bildlauf.
- Erst die Duo-Szenen im `Screenshots`-Lauf prüfen, den App-Store-Lauf erst danach anfassen.
- Änderungen an den Workflows in appo-familie zuerst in einer App über einen Branch-Stand prüfen (`@<branch>` statt `@v1`), dann `v1` nachziehen.
- `concurrency` mit `cancel-in-progress: true` lassen, mehrere Änderungen in einem Push sammeln.
- `CI` (rund eine Minute) zuerst grün bekommen, bevor ein Bildlauf startet.
- Nach jedem Bildlauf die Bilder ansehen und auf schwarze prüfen, bevor gerahmt wird.

*10. Was beim Layout auffiel.* `NavigationSplitView` hält die Seitenleiste bei etwa einem Drittel der Breite – richtig für Liste und Detail, falsch für zwei gleich große Seiten (dann zwei `NavigationStack` nebeneinander, der Knick liegt genau dazwischen). Sheets bleiben innen schmal und kompakt, Zweispaltiges im Sheet greift nie – Breites gehört in die zweite Spalte. Innen quer steht die Leiste der rechten Spalte senkrecht am rechten Rand, die linke Spalte behält eine waagerechte. Außen liegen Blob und eigene Überlagerungen im sicheren Bereich neben der senkrechten Leiste, ohne eigenen Code. `ToolbarOverflowMenu` und `visibilityPriority` gibt es ab iOS 27.0, `ArrangementView` ab 27.1; bei Ziel iOS 26 in einem `ViewBuilder` oder `ViewModifier` mit `if #available(iOS 27.0, *)` umschalten, nicht im `ToolbarContentBuilder`.

**Bewusst nicht**

- Keine Effekte über den Klappwinkel (`onHingeChange`) und keine Inhalte auf beiden Displays gleichzeitig (Szenen-Zubehör). Das ist nett für Spiele und Kameras, passt aber nicht zu „so schlank wie möglich“.
- Keine Sonderansicht pro Haltung. Gestaltet wird für zwei Fälle, kompakte und reguläre Breite; die Haltungen dienen nur zum Prüfen.
- Vorerst keine mehreren Fenster derselben App (`UIApplicationSupportsMultipleScenes` bleibt `false`). Wieder ansehen, wenn sich jemand zwei Listen oder zwei Tage nebeneinander wünscht.

**Je App**

- [x] **Kaufo:** Innen stehen die Listen in einer Seitenleiste statt in den Reitern oben; rechts die gewählte Liste (`NavigationSplitView`, `ListSidebar` in `RootView.swift`, entschieden über `horizontalSizeClass`). Die Eingabe in der Zeile zum Hinzufügen liegt in `AddDrafts` und übersteht das Umschalten. Der Einkaufsmodus bleibt einspaltig mit großen Zeilen. Zettel und Kassenbon bleiben bei der Systemkamera. Prüfen ohne Duo-Simulator: Demo-Start mit `-demoRegular`. Gebaut mit Xcode 27.1; außen stehen die Systemleisten von selbst senkrecht. Duo-Screenshots außen und innen in `Screenshots` und `App-Store-Screenshots`, gerahmt nach `framed-duo` und `framed-duo-aussen`, die Webseite zeigt das aufgeklappte Duo. *Noch offen:* „Mehr“ als `ToolbarOverflowMenu`, Blob gegen `toolbarVerticalEdge` und Knick, `-demoRegular` ist mit dem Duo-Simulator verzichtbar.
- [ ] **Scanno:** Innen links die Liste der Scans, rechts das gewählte Dokument (`NavigationSplitView`, Auswahl über `openedID`, entschieden über die Breite). `ScanSession` hängt über dem `NavigationSplitView`, der laufende Scan ist ein Sheet – beim Auf- und Zuklappen wird keine Ansicht ausgetauscht. Teilen zeigt UIKit mit Popover-Anker (`ShareSheet`), Export über `.fileExporter`. `VNDocumentCameraViewController` bleibt die Kamera. Gebaut mit Xcode 27.1, Duo-Screenshots außen und innen in `Screenshots` und `App-Store-Screenshots`, gerahmt nach `framed-duo` und `framed-duo-aussen`. *Noch offen:* Halb aufgeklappt zeigt die Vorschau zwei Seiten nebeneinander wie ein aufgeschlagenes Heft (`PDFView` mit `.twoUp`, wenn eine Trennregion aktiv ist), `.topBarPinnedTrailing`, „Mehr“ als `ToolbarOverflowMenu`, Blob gegen `toolbarVerticalEdge` und Knick (alles iOS 27.1). Einzelheiten in Scannos `KONZEPT.md` („iPhone Duo“).
- [x] **Schreibo:** Innen wird das Notizbuch zur **Doppelseite** aus zwei gleich breiten Seiten (zwei `NavigationStack` nebeneinander in `NotebookView`; `NavigationSplitView` hätte die linke Spalte schmal gehalten). Links die Tagesseite mit Eingabeleiste und Blob, rechts die geöffnete Notiz, der Kalender (statt im Sheet) oder ohne Auswahl der nächste Tag mit „Zurück-/Weiterblättern“ – das liest sich wie ein aufgeschlagenes Notizbuch. Halb aufgeklappt liegt der Knick genau zwischen den Seiten. Notiz und Kalender wandern beim Zuklappen ins Sheet und zurück. „Mehr“ ab iOS 27 als `ToolbarOverflowMenu`, Duo-Screenshots außen und innen in CI und App-Store-Workflow.

**Reihenfolge**

1. SDK und Duo-Simulator in der CI, die Apps einmal im Simulator durchklicken (außen, innen, Split View links und rechts, halb aufgeklappt).
2. Leisten prüfen: Titel und Symbole, „Mehr“ als Überlaufmenü, Prioritäten.
3. Blob, Banner und eigene Leisten gegen senkrechte Leisten und den Knick absichern.
4. Zwei Spalten innen, je App wie oben.
5. Duo-Screenshots in den App Store, Webseite ergänzen.

## Webseite

Jede App hat eine Webseite aus einer einzigen HTML-Datei (`docs/website/index.html` im Repo der App), Bilder eingebettet (JPEG, 660 Pixel breit, base64), ohne fremde Schriften, Skripte oder Zähler.

- **Alle Webseiten sehen gleich aus.** Gleicher Aufbau, gleiche Gestaltung, gleiche Bausteine; die App bringt nur ihre Standard-Farbwelt, ihr Icon, ihre Texte und ihre Bilder mit. Wer eine Seite ansieht, erkennt die Familie.
- **Feste Reihenfolge der Abschnitte:** Kopf (Icon, Name, ein Satz, Knopf zum App Store) → Funktionen → iPhone Duo → Hilfe → Datenschutz → Impressum. Was eine App nicht hat, fällt weg; neue Abschnitte bekommen in allen Apps denselben Platz.
- **Gemeinsam ändern.** Ein neuer Abschnitt oder eine geänderte Gestaltung kommt in alle Webseiten zugleich, in derselben Sitzung. Keine Seite bekommt etwas, das die anderen nicht auch bekommen, außer dem Inhalt.
- **Woher:** Vorlage, Gestaltung und Erzeugungs-Skript liegen hier in appo-familie (`website/`), der Inhalt je App in `docs/website/site.json` plus den App-Store-Rohbildern. Das Skript (`website/make_website.py`) schreibt wie bisher `docs/website/index.html` ins Repo der App, damit Adresse und Veröffentlichung bleiben, wie sie sind. Die Seite nie von Hand ändern, sondern `site.json` oder die Vorlage – und nach einer Änderung der Vorlage alle drei Seiten neu erzeugen.
- **Bausteine:** Kopf mit Logo (Blob mit dem Zeichen des App-Icons), Einleitung, Knopf zum App Store und Bild im Blob; Funktionskarten (sechs, Symbole aus `website/symbole.json`) mit Bildleiste; iPhone Duo mit innerem Display (hell und dunkel) und Außendisplay; Hilfe als Fragen und Antworten mit Kontakt; Datenschutz mit den gemeinsamen Abschnitten; Impressum; Fußzeile mit den Apple-Marken der App.

## App Store: Stolpersteine beim ersten Upload

Alles in `project.yml`, damit es beim Neuerzeugen mit XcodeGen erhalten bleibt:

- **Team:** `DEVELOPMENT_TEAM: 9H7F5NMT97` (Aketo GmbH) in den gemeinsamen `settings.base`.
- **Nur iPhone:** `TARGETED_DEVICE_FAMILY: "1"` in `settings.base` **und** an jedem iOS-Target (App, Widget, Erweiterungen); die Watch-App bekommt `"4"`. XcodeGen setzt pro Target sonst „1,2“ und überschreibt die Projekteinstellung – dann sind iPhone und iPad eingetragen, und App Store Connect verlangt iPad-Screenshots.
- **Ausrichtungen:** alle vier in `UISupportedInterfaceOrientations` (Portrait, PortraitUpsideDown, LandscapeLeft, LandscapeRight), sonst lehnt die Prüfung wegen iPad-Multitasking ab.
- **Exportkontrolle:** `ITSAppUsesNonExemptEncryption: false` in den Info-Properties der App, solange nur die Verschlüsselung von iOS genutzt wird (HTTPS, iCloud). Dann fragt App Store Connect bei keinem Upload mehr nach der Verschlüsselung.
- **Build-Nummer:** Version und Build stehen nur in `project.yml` (`MARKETING_VERSION`, `CURRENT_PROJECT_VERSION` in `settings.base`). Vor jedem Upload dort erhöhen und mitcommitten, nie in Xcode unter „General“ – das nächste `xcodegen generate` setzt sie sonst zurück, und App Store Connect nimmt jede Nummer nur einmal. In den Info-Properties **jedes** Targets müssen `CFBundleShortVersionString: $(MARKETING_VERSION)` und `CFBundleVersion: $(CURRENT_PROJECT_VERSION)` stehen – XcodeGen schreibt sonst bei jedem Erzeugen fest „1.0 (1)“ in die Info.plist.
- **SwiftData mit CloudKit-Berechtigung:** Container mit `cloudKitDatabase: .none` anlegen, wenn der Abgleich selbst gebaut ist (sonst Absturz beim Start).
- **Screenshots:** 1320 × 2868 ins Fach „6,9 Zoll“, ohne Transparenz. Vor den Aufnahmen im Simulator abwarten, bis Systemmitteilungen verschwunden sind. Mit Watch-App ist auch ein Watch-Screenshot Pflicht (Rohbild aus dem Watch-Simulator).
- **App-Informationen:** Inhaltsrechte („Inhalte Dritter?“) ausfüllen, App-Datenschutz angeben.

## Bausteine

Was in appo-familie liegt, wird eingebunden, nicht kopiert. Der Rest wird vorerst aus der genannten App kopiert und wandert nach und nach ins Paket – in dieser Reihenfolge, jeweils erst in einer App erprobt.

| Was | Wo heute | Ziel |
| --- | --- | --- |
| „Weitere Apps von uns“ (ganz unten in den Einstellungen) | appo-familie, Produkt `MoreApps` | erledigt |
| CI, Screenshots, App-Store-Bilder | appo-familie, `.github/workflows/` | erledigt |
| Veröffentlichen (archivieren, signieren, zu App Store Connect hochladen) | appo-familie, `.github/workflows/release.yml` | erledigt |
| App-Store-Bilder gestalten und hochladen | appo-familie, `.github/workflows/appstore-upload.yml`, `scripts/appstore_upload.py` | in Kaufo in Erprobung |
| App-Icon, App-Store-Rahmen | appo-familie, `scripts/make_icon.py`, `scripts/appstore_frames.py` | erledigt |
| Webseite (Vorlage, Gestaltung, Abschnitte) | appo-familie `website/`, Inhalt je App in `docs/website/site.json` | erledigt |
| Farbwelten (`AppTheme`, `Color(light:dark:)`, `\.theme`) | appo-familie, Produkt `FamilieUI` (`Farbwelt.swift`); Standard-Farbwelt und Icon-Namen in der App | erledigt |
| Schriften und `.appFont` (`Typeface`, `\.typeface`) | `FamilieUI` (`Schrift.swift`) | erledigt |
| Blob, Blob-Button, Logo (`BlobShape`, `BlobButton`, `BlobLogo`, `BlobSymbol`) | `FamilieUI` (`Blob.swift`) | erledigt |
| Banner, Fächer-Menü (`Banner`, `BannerView`, `FanItem`, `BlobFan`, `BlobMenu`) | `FamilieUI` (`Banner.swift`, `Faecher.swift`) | erledigt |
| Statistik-Bausteine (`StatCard`, `StatTile`, `RankedBars`) | `FamilieUI` (`Statistik.swift`) | erledigt |
| Spracheingabe | Kaufo `App/Services/SpeechInput.swift` | später, eigenes Produkt |
| Palette und Ladenfarben | Kaufo `Shared/ListColor.swift`, `Shared/StoreBrand.swift` | bleibt in Kaufo |
| iCloud und Haushalt | Kaufo `App/Services/Sync/` | bleibt je App (Zonen und Datensätze unterscheiden sich) |
| Widget im Erinnerungen-Stil | Kaufo `Widget/EinkaufWidget.swift` | bleibt je App |
| Live-Aktivität, Steuerelemente | Kaufo `Intents/`, `Widget/ShoppingLiveActivity.swift`, `Widget/Controls.swift` | bleibt je App |
| Demo-Modus | Kaufo `App/Services/DemoData.swift` | bleibt je App, Startargumente wie oben |
| Projekt | Kaufo `project.yml` | bleibt je App |
| App-Store-Texte als Vorlage | Kaufo `docs/appstore/texte.md` | bleibt je App |

Ins Paket gehört nur, was in allen Apps gleich aussieht und sich gleich verhält. Sobald eine App etwas anders braucht, bekommt der Baustein einen Parameter, keine Kopie mit Änderungen.
