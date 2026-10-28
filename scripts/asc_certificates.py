"""Räumt Entwicklungszertifikate auf, die ein Lauf von „Veröffentlichen“ angelegt hat.

Xcode legt beim Archivieren auf einem frischen Runner ein neues „Apple Development“-Zertifikat an
(-allowProvisioningUpdates). Der private Schlüssel liegt nur auf dem Runner und ist danach wertlos – nach
etwa zehn Läufen meldet Apple „Your account has reached the maximum number of certificates“. Darum:

  python3 asc_certificates.py remember liste.txt   # vor dem Archivieren: vorhandene Zertifikate merken
  python3 asc_certificates.py cleanup liste.txt    # danach: alle neuen Entwicklungszertifikate zurückziehen

Zurückgezogen wird nur, was während des Laufs dazugekommen ist – eigene Zertifikate am Mac bleiben.
Schlüssel aus der Umgebung: ASC_KEY_ID, ASC_ISSUER_ID, ASC_KEY_P8 (Rolle Admin). Nur Python 3 und cryptography.
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from appstore_upload import Connect, fail  # noqa: E402

DEVELOPMENT = {"DEVELOPMENT", "IOS_DEVELOPMENT"}


def development_certificates(connect):
    result = {}
    for item in connect.all("/v1/certificates?limit=200"):
        attributes = item["attributes"]
        if attributes.get("certificateType") in DEVELOPMENT:
            result[item["id"]] = attributes.get("displayName") or attributes.get("name") or item["id"]
    return result


def main():
    if len(sys.argv) != 3 or sys.argv[1] not in ("remember", "cleanup"):
        fail("Aufruf: asc_certificates.py remember|cleanup <datei>")
    action, path = sys.argv[1], Path(sys.argv[2])
    missing = [name for name in ("ASC_KEY_ID", "ASC_ISSUER_ID", "ASC_KEY_P8") if not os.environ.get(name)]
    if missing:
        fail(f"Fehlende Secrets: {', '.join(missing)}")
    connect = Connect(os.environ["ASC_KEY_ID"], os.environ["ASC_ISSUER_ID"], os.environ["ASC_KEY_P8"])
    current = development_certificates(connect)

    if action == "remember":
        path.write_text("\n".join(sorted(current)) + "\n")
        print(f"{len(current)} Entwicklungszertifikate vorhanden")
        return

    known = set(path.read_text().split()) if path.exists() else None
    if known is None:
        fail(f"{path} fehlt – ohne die Liste von vorher wird nichts zurückgezogen")
    new = {cid: name for cid, name in current.items() if cid not in known}
    if not new:
        print("Kein neues Entwicklungszertifikat")
        return
    for cid, name in new.items():
        connect.call("DELETE", f"/v1/certificates/{cid}")
        print(f"Zurückgezogen: {name} ({cid})")


if __name__ == "__main__":
    main()
