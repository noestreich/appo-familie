"""Bereitet die nächste Version in App Store Connect vor: anlegen, Build zuordnen, Neuerungen eintragen.

Aufruf im Ordner der App (Schlüssel aus der Umgebung: ASC_KEY_ID, ASC_ISSUER_ID, ASC_KEY_P8):
  python3 <appo-familie>/scripts/appstore_version.py --bundle-id de.ncls.kaufo --version 1.1.1 --build 15 \
      [--texts docs/appstore/texte.md] [--wait 20] [--dry-run]

Was passiert:
  1. Die App suchen und ihre Versionen zeigen.
  2. Die Version aus --version nehmen oder anlegen. Apple legt keine neue Version an, solange eine andere
     noch in Prüfung ist oder auf Freigabe wartet – dann bricht das Skript mit dieser Meldung ab.
  3. Den Build --build dieser Version suchen. Ist er noch in Verarbeitung, bis zu --wait Minuten warten.
  4. Den Build der Version zuordnen.
  5. Den Text unter „## Neuerungen in dieser Version (…)“ aus --texts als „Neuerungen“ in der Sprache der App
     eintragen (der erste Codeblock nach der Überschrift).

Eingereicht wird nicht – das bleibt in App Store Connect. Nur Python 3 und das Paket cryptography.
"""
import argparse
import os
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from appstore_upload import Connect, fail  # noqa: E402

# Zustände, in denen sich eine Version noch ändern lässt.
EDITABLE = {"PREPARE_FOR_SUBMISSION", "DEVELOPER_REJECTED", "REJECTED", "METADATA_REJECTED", "INVALID_BINARY"}


def whats_new(path, version):
    """Der Text unter „## Neuerungen in dieser Version (…)“, erster Codeblock danach."""
    text = Path(path).read_text(encoding="utf-8")
    match = re.search(r"^## Neuerungen in dieser Version \(([^)]*)\)\s*\n+```\n(.*?)\n```", text, re.S | re.M)
    if not match:
        fail(f"{path}: kein Abschnitt „## Neuerungen in dieser Version (…)“ mit Codeblock")
    heading, body = match.group(1), match.group(2).strip()
    if heading.split(",")[0].strip() != version:
        fail(f"{path}: Die Neuerungen sind für „{heading}“, nicht für {version} – erst texte.md nachziehen")
    if len(body) > 4000:
        fail(f"{path}: Neuerungen mit {len(body)} Zeichen, App Store Connect nimmt höchstens 4000")
    return body


def state_of(version):
    attributes = version["attributes"]
    return attributes.get("appVersionState") or attributes.get("appStoreState") or "?"


def find_or_create_version(connect, app_id, version_string, dry_run):
    versions = connect.all(f"/v1/apps/{app_id}/appStoreVersions?filter[platform]=IOS&limit=50")
    versions.sort(key=lambda v: v["attributes"].get("createdDate") or "", reverse=True)
    for version in versions[:5]:
        print(f"  Version {version['attributes']['versionString']}: {state_of(version)}")
    for version in versions:
        if version["attributes"]["versionString"] == version_string:
            state = state_of(version)
            if state not in EDITABLE and version["attributes"].get("appStoreState") not in EDITABLE:
                fail(f"Version {version_string} gibt es schon und sie lässt sich nicht mehr ändern ({state})")
            print(f"Version {version_string} ist schon angelegt ({state})")
            return version["id"]
    if dry_run:
        print(f"Würde Version {version_string} anlegen")
        return None
    try:
        created = connect.call("POST", "/v1/appStoreVersions", {"data": {
            "type": "appStoreVersions",
            "attributes": {"platform": "IOS", "versionString": version_string},
            "relationships": {"app": {"data": {"type": "apps", "id": app_id}}},
        }})
    except RuntimeError as error:
        done = {"READY_FOR_SALE", "READY_FOR_DISTRIBUTION", "REPLACED_WITH_NEW_VERSION", "REMOVED_FROM_SALE",
                "DEVELOPER_REMOVED_FROM_SALE"}
        busy = [f"{v['attributes']['versionString']} ({state_of(v)})" for v in versions if state_of(v) not in done]
        hint = f" Noch offen: {', '.join(busy)} – erst nach deren Freigabe noch einmal starten." if busy else ""
        fail(f"Version {version_string} ließ sich nicht anlegen: {error}.{hint}")
    print(f"Version {version_string} angelegt")
    return created["data"]["id"]


def find_build(connect, app_id, version_string, build_number, wait_minutes):
    deadline = time.time() + wait_minutes * 60
    while True:
        builds = connect.all(
            f"/v1/builds?filter[app]={app_id}&filter[version]={build_number}"
            f"&filter[preReleaseVersion.version]={version_string}&limit=10"
        )
        if builds:
            build = builds[0]
            state = build["attributes"].get("processingState")
            if state == "VALID":
                print(f"Build {version_string} ({build_number}) ist verarbeitet")
                return build["id"]
            if state in ("FAILED", "INVALID"):
                fail(f"Build {version_string} ({build_number}) ist ungültig ({state})")
            label = f"in Verarbeitung ({state})"
        else:
            label = "noch nicht da"
        if time.time() >= deadline:
            fail(f"Build {version_string} ({build_number}) ist {label} – später noch einmal starten")
        print(f"Build {version_string} ({build_number}) ist {label}, warte eine Minute …")
        time.sleep(60)


def set_whats_new(connect, version_id, locale, text):
    localizations = connect.all(f"/v1/appStoreVersions/{version_id}/appStoreVersionLocalizations?limit=50")
    for item in localizations:
        if item["attributes"]["locale"] == locale:
            connect.call("PATCH", f"/v1/appStoreVersionLocalizations/{item['id']}", {"data": {
                "type": "appStoreVersionLocalizations", "id": item["id"], "attributes": {"whatsNew": text},
            }})
            print(f"Neuerungen ({locale}, {len(text)} Zeichen) eingetragen")
            return
    connect.call("POST", "/v1/appStoreVersionLocalizations", {"data": {
        "type": "appStoreVersionLocalizations",
        "attributes": {"locale": locale, "whatsNew": text},
        "relationships": {"appStoreVersion": {"data": {"type": "appStoreVersions", "id": version_id}}},
    }})
    print(f"Sprache {locale} mit Neuerungen ({len(text)} Zeichen) angelegt")


def main():
    parser = argparse.ArgumentParser(description="Version in App Store Connect vorbereiten")
    parser.add_argument("--bundle-id", required=True)
    parser.add_argument("--version", required=True, help="z. B. 1.1.1 (MARKETING_VERSION)")
    parser.add_argument("--build", required=True, help="Build-Nummer (CURRENT_PROJECT_VERSION)")
    parser.add_argument("--texts", default="docs/appstore/texte.md", help="Datei mit den Neuerungen")
    parser.add_argument("--wait", type=int, default=20, help="Minuten warten, bis der Build verarbeitet ist")
    parser.add_argument("--dry-run", action="store_true", help="nur zeigen, was passieren würde")
    args = parser.parse_args()

    text = whats_new(args.texts, args.version)
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

    version_id = find_or_create_version(connect, app["id"], args.version, args.dry_run)
    build_id = find_build(connect, app["id"], args.version, args.build, 0 if args.dry_run else args.wait)
    if args.dry_run:
        print(f"Würde Build {args.build} zuordnen und die Neuerungen eintragen:\n{text}")
        return
    connect.call("PATCH", f"/v1/appStoreVersions/{version_id}/relationships/build", {
        "data": {"type": "builds", "id": build_id},
    })
    print(f"Build {args.build} der Version {args.version} zugeordnet")
    set_whats_new(connect, version_id, locale, text)
    print(f"Fertig: {args.version} ({args.build}) wartet in App Store Connect aufs Einreichen")


if __name__ == "__main__":
    main()
