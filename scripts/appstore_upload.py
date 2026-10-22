"""Lädt die gestalteten App-Store-Bilder zu App Store Connect hoch.

Aufruf im Ordner der App (Schlüssel aus der Umgebung: ASC_KEY_ID, ASC_ISSUER_ID, ASC_KEY_P8):
  python3 <appo-familie>/scripts/appstore_upload.py --bundle-id de.ncls.kaufo [--version 1.0.2] [--dry-run]

Was passiert:
  1. Die App und ihre bearbeitbare Version suchen (in Vorbereitung oder abgelehnt). Gibt es keine,
     wird die Version aus --version angelegt; ohne --version bricht das Skript ab.
  2. Die Sprache der App (primäre Sprache) wählen – die Überschriften sind auf Deutsch.
  3. Je Ordner das passende Fach finden und dessen Bilder ersetzen, in der Reihenfolge der Dateinamen:
       framed/            1320 × 2868  (iPhone 6,9")
       framed-6.3/        1206 × 2622  (iPhone 6,3")
       framed-duo/        2853 × 2007  (iPhone Duo innen)
       framed-duo-aussen/ 1398 × 2034  (iPhone Duo außen)
       watch/              410 × 502   (Apple Watch Ultra)
     Das Fach ergibt sich aus der Bildgröße: Liegt in der Version schon ein Fach mit Bildern dieser Größe,
     kommt es dorthin. Sonst gilt die Tabelle FALLBACK; fehlt die Größe auch dort, wird der Ordner übersprungen.

--dry-run zeigt nur, was hochgeladen würde. Nur Python 3 und das Paket cryptography.
"""
import argparse
import base64
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, utils

API = "https://api.appstoreconnect.apple.com"

FOLDERS = ["framed", "framed-6.3", "framed-duo", "framed-duo-aussen", "watch"]

# Fächer für Größen, die in der Version noch kein Fach haben (Namen aus der API von App Store Connect).
FALLBACK = {
    (1320, 2868): "APP_IPHONE_67",
    (1206, 2622): "APP_IPHONE_61",
    (410, 502): "APP_WATCH_ULTRA",
}

EDITABLE = {"PREPARE_FOR_SUBMISSION", "DEVELOPER_REJECTED", "REJECTED", "METADATA_REJECTED", "INVALID_BINARY"}


def fail(message):
    print(f"::error::{message}")
    sys.exit(1)


def b64url(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


class Connect:
    def __init__(self, key_id, issuer_id, key_p8):
        self.key_id = key_id
        self.issuer_id = issuer_id
        self.key = serialization.load_pem_private_key(key_p8.encode(), password=None)

    def token(self):
        now = int(time.time())
        header = {"alg": "ES256", "kid": self.key_id, "typ": "JWT"}
        payload = {"iss": self.issuer_id, "iat": now, "exp": now + 15 * 60, "aud": "appstoreconnect-v1"}
        signing_input = f"{b64url(json.dumps(header).encode())}.{b64url(json.dumps(payload).encode())}"
        der = self.key.sign(signing_input.encode(), ec.ECDSA(hashes.SHA256()))
        r, s = utils.decode_dss_signature(der)
        return f"{signing_input}.{b64url(r.to_bytes(32, 'big') + s.to_bytes(32, 'big'))}"

    def call(self, method, path, body=None):
        url = path if path.startswith("http") else API + path
        data = json.dumps(body).encode() if body is not None else None
        request = urllib.request.Request(url, data=data, method=method)
        request.add_header("Authorization", f"Bearer {self.token()}")
        if data is not None:
            request.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                raw = response.read()
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as error:
            text = error.read().decode(errors="replace")
            try:
                details = "; ".join(e.get("detail") or e.get("title", "") for e in json.loads(text).get("errors", []))
            except ValueError:
                details = text[:500]
            raise RuntimeError(f"{method} {path}: HTTP {error.code} – {details}") from None

    def all(self, path):
        items = []
        while path:
            page = self.call("GET", path)
            items.extend(page.get("data", []))
            path = page.get("links", {}).get("next")
        return items


def image_size(path):
    with open(path, "rb") as f:
        header = f.read(24)
    if header[:8] != b"\x89PNG\r\n\x1a\n":
        fail(f"{path} ist kein PNG")
    return int.from_bytes(header[16:20], "big"), int.from_bytes(header[20:24], "big")


def find_version(connect, app_id, version_string, dry_run):
    versions = connect.all(f"/v1/apps/{app_id}/appStoreVersions?filter[platform]=IOS&limit=50")
    for version in versions:
        attributes = version["attributes"]
        state = attributes.get("appVersionState") or attributes.get("appStoreState")
        if state in EDITABLE or attributes.get("appStoreState") in EDITABLE:
            print(f"Version {attributes['versionString']} ({state}) wird bearbeitet")
            return version["id"]
    if not version_string:
        fail("Keine bearbeitbare Version in App Store Connect und keine Version angegeben (--version)")
    if dry_run:
        print(f"Würde Version {version_string} anlegen")
        return None
    created = connect.call("POST", "/v1/appStoreVersions", {"data": {
        "type": "appStoreVersions",
        "attributes": {"platform": "IOS", "versionString": version_string},
        "relationships": {"app": {"data": {"type": "apps", "id": app_id}}},
    }})
    print(f"Version {version_string} angelegt")
    return created["data"]["id"]


def existing_sets(connect, localization_id):
    """Fach → (Set-ID, Größe der vorhandenen Bilder oder None, IDs der Bilder)."""
    result = {}
    for item in connect.all(f"/v1/appStoreVersionLocalizations/{localization_id}/appScreenshotSets?limit=50"):
        shots = connect.all(f"/v1/appScreenshotSets/{item['id']}/appScreenshots?limit=50")
        size = None
        for shot in shots:
            asset = shot["attributes"].get("imageAsset") or {}
            if asset.get("width"):
                size = (asset["width"], asset["height"])
                break
        result[item["attributes"]["screenshotDisplayType"]] = (item["id"], size, [s["id"] for s in shots])
    return result


def display_type_for(size, sets):
    flipped = (size[1], size[0])
    for display_type, (_, existing, _) in sets.items():
        if existing in (size, flipped):
            return display_type
    return FALLBACK.get(size) or FALLBACK.get(flipped)


def upload(connect, set_id, path):
    data = path.read_bytes()
    created = connect.call("POST", "/v1/appScreenshots", {"data": {
        "type": "appScreenshots",
        "attributes": {"fileName": path.name, "fileSize": len(data)},
        "relationships": {"appScreenshotSet": {"data": {"type": "appScreenshotSets", "id": set_id}}},
    }})
    shot_id = created["data"]["id"]
    for operation in created["data"]["attributes"]["uploadOperations"]:
        chunk = data[operation["offset"]:operation["offset"] + operation["length"]]
        request = urllib.request.Request(operation["url"], data=chunk, method=operation["method"])
        for header in operation.get("requestHeaders", []):
            request.add_header(header["name"], header["value"])
        with urllib.request.urlopen(request, timeout=120):
            pass
    connect.call("PATCH", f"/v1/appScreenshots/{shot_id}", {"data": {
        "type": "appScreenshots", "id": shot_id,
        "attributes": {"uploaded": True, "sourceFileChecksum": hashlib.md5(data).hexdigest()},
    }})
    return shot_id


def wait_until_processed(connect, shot_ids):
    pending = set(shot_ids)
    for _ in range(40):
        for shot_id in list(pending):
            state = connect.call("GET", f"/v1/appScreenshots/{shot_id}")["data"]["attributes"].get("assetDeliveryState") or {}
            if state.get("state") == "COMPLETE":
                pending.discard(shot_id)
            elif state.get("state") == "FAILED":
                errors = "; ".join(e.get("description", "") for e in state.get("errors", []))
                raise RuntimeError(f"Apple hat ein Bild abgelehnt: {errors}")
        if not pending:
            return
        time.sleep(5)
    print(f"::warning::{len(pending)} Bilder sind bei Apple noch in Arbeit – in App Store Connect nachsehen")


def main():
    parser = argparse.ArgumentParser(description="App-Store-Bilder zu App Store Connect hochladen")
    parser.add_argument("--bundle-id", required=True)
    parser.add_argument("--root", default="docs/appstore", help="Ordner mit framed/, framed-6.3/, … und watch/")
    parser.add_argument("--version", default="", help="Version, die angelegt wird, falls keine bearbeitbar ist")
    parser.add_argument("--dry-run", action="store_true", help="nur zeigen, was hochgeladen würde")
    args = parser.parse_args()

    missing = [name for name in ("ASC_KEY_ID", "ASC_ISSUER_ID", "ASC_KEY_P8") if not os.environ.get(name)]
    if missing:
        fail(f"Fehlende Secrets: {', '.join(missing)}")
    connect = Connect(os.environ["ASC_KEY_ID"], os.environ["ASC_ISSUER_ID"], os.environ["ASC_KEY_P8"])

    apps = connect.call("GET", f"/v1/apps?filter[bundleId]={args.bundle_id}")["data"]
    if not apps:
        fail(f"Keine App mit der Bundle-ID {args.bundle_id} in App Store Connect")
    app = apps[0]
    locale = app["attributes"].get("primaryLocale", "de-DE")
    print(f"App {app['attributes']['name']} ({args.bundle_id}), Sprache {locale}")

    version_id = find_version(connect, app["id"], args.version, args.dry_run)
    sets = {}
    localization_id = None
    if version_id:
        for item in connect.all(f"/v1/appStoreVersions/{version_id}/appStoreVersionLocalizations?limit=50"):
            if item["attributes"]["locale"] == locale:
                localization_id = item["id"]
        if not localization_id:
            fail(f"Die Version hat keine Sprache {locale}")
        sets = existing_sets(connect, localization_id)
        for display_type, (_, size, shots) in sorted(sets.items()):
            print(f"  vorhanden: {display_type} – {len(shots)} Bilder, {size[0]} × {size[1]}" if size
                  else f"  vorhanden: {display_type} – leer")

    root = Path(args.root)
    plan = []
    for folder in FOLDERS:
        files = sorted((root / folder).glob("*.png"))
        if not files:
            continue
        sizes = {image_size(f) for f in files}
        if len(sizes) > 1:
            fail(f"{folder}/ enthält Bilder verschiedener Größen: {sorted(sizes)}")
        size = sizes.pop()
        display_type = display_type_for(size, sets)
        if not display_type:
            print(f"::warning::{folder}/ ({size[0]} × {size[1]}): kein passendes Fach in App Store Connect – übersprungen")
            continue
        if len(files) > 10:
            print(f"::warning::{folder}/: App Store Connect nimmt höchstens 10 Bilder je Fach, die übrigen fallen weg")
            files = files[:10]
        print(f"{folder}/ → {display_type}: {', '.join(f.name for f in files)}")
        plan.append((folder, display_type, files))

    if args.dry_run or not plan:
        return

    summary = []
    for folder, display_type, files in plan:
        if display_type in sets:
            set_id, _, old = sets[display_type]
        else:
            set_id = connect.call("POST", "/v1/appScreenshotSets", {"data": {
                "type": "appScreenshotSets",
                "attributes": {"screenshotDisplayType": display_type},
                "relationships": {"appStoreVersionLocalization": {
                    "data": {"type": "appStoreVersionLocalizations", "id": localization_id}}},
            }})["data"]["id"]
            old = []
        # Erst die alten Bilder entfernen – ein Fach nimmt höchstens zehn.
        for shot_id in old:
            connect.call("DELETE", f"/v1/appScreenshots/{shot_id}")
        new = [upload(connect, set_id, path) for path in files]
        wait_until_processed(connect, new)
        print(f"✓ {display_type}: {len(new)} Bilder")
        summary.append(f"- {folder}/ → {display_type}: {len(new)} Bilder")

    step_summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if step_summary:
        with open(step_summary, "a") as f:
            f.write("### App-Store-Bilder hochgeladen\n" + "\n".join(summary) + "\n")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as error:
        fail(str(error))
