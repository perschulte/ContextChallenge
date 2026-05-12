# pkn-punkte

Persönliches Automatisierungs-Skript zur halbjährlichen Einreichung von CME-Punkten
einer akkreditierten Intervisionsgruppe im PKN-Mitgliederportal (pknds.eu).

Rein lokaler Eigengebrauch. Keine Cloud, keine Multi-User-Funktionalität,
keine Patienten- oder Behandlungsdaten.

## Aktueller Stand (MVP)

Implementiert ist die erste Stufe:
- Login ins Portal (headless oder mit `--headed`)
- Einlesen der Teilnehmer\*innen-Liste aus CSV
- Ausfüllen des Eingabeformulars pro Eintrag
- **Dry-Run-Modus per Default** (kein Absenden, nur Screenshot des befüllten Formulars)
- JSONL-Run-Log + Screenshot-Belege

Noch nicht implementiert (folgt, sobald Login + ein Test-Eintrag stabil sind):
- Idempotenz / Status-Cache (`state.json`)
- Retry mit Backoff
- Captcha-Behandlung (falls vorhanden — bisher unbekannt)
- Session-Resume bei Timeout

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
playwright install chromium

cp .env.example .env                      # Zugangsdaten eintragen
cp config.yaml.example config.yaml        # VNR + Selektoren eintragen
cp data/participants.example.csv data/participants.csv
```

`.env`, `config.yaml` und `data/participants.csv` sind gitignored.

### Selektoren ermitteln

Das Portal ist nicht öffentlich dokumentiert. Beim ersten manuellen Login:

1. DevTools öffnen (F12) → Elements
2. Login-Felder inspizieren → `selectors.login.*` in `config.yaml` eintragen
3. Zum Punkte-Einreichungs-Formular navigieren → `portal.entry_url` notieren
4. Formularfelder inspizieren → `selectors.entry.*` eintragen
5. Bevorzugt stabile Attribute (`name`, `id`, `aria-label`) statt CSS-Pfaden

### Captcha?

Bisher unbekannt, ob das Portal eines verwendet. Falls ja:
`--headed` benutzen und für den Captcha-Schritt manuell pausieren —
Vollautomatisierung wäre dann nicht möglich.

## Benutzung

Empfohlene erste Schritte zum Validieren:

```bash
# Headed, ein Eintrag, dry-run — Browser bleibt sichtbar, nichts wird abgesendet
pkn-punkte --headed --once

# Wenn das durchläuft: alle Einträge dry-run
pkn-punkte

# Erst wenn dry-run stabil ist und Screenshots korrekt aussehen:
pkn-punkte --no-dry-run
```

### Optionen

| Flag                  | Default | Wirkung                                                      |
|-----------------------|---------|--------------------------------------------------------------|
| `--config PATH`       | `config.yaml` | Pfad zur Konfigurationsdatei                            |
| `--dry-run/--no-dry-run` | dry-run | Formular ausfüllen + Screenshot, **nicht absenden**       |
| `--once`              | off     | Nur den ersten Eintrag aus der CSV abarbeiten                |
| `--headed`            | off     | Browser sichtbar starten                                     |

## Ausgaben

- `runs/log.jsonl` — strukturiertes Run-Log (eine JSON-Zeile pro Event)
- `screenshots/` — befüllte Formulare + Bestätigungen
- `state.json` — *(geplant)* bereits eingereichte Einträge

## Sicherheit / Daten

- Passwort kommt aus `.env` oder optional aus dem System-Keychain
  (`pip install pkn-punkte[keychain]`, dann `PKN_KEYRING_SERVICE` / `PKN_KEYRING_USER` setzen)
- Teilnehmer\*innen-CSV enthält nur Name + EFN (Einheitliche Fortbildungsnummer), keine Falldaten
- CSVs sind gitignored
