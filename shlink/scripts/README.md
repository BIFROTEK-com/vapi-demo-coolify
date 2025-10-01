# Shlink Scripts

Dieser Ordner enthält alle funktionierenden Python-Skripte für die Arbeit mit Shlink.

## Verfügbare Skripte

### Link-Management
- `register_demo_links.py` - Registriert Demo-Links in Shlink
- `register_demo_links_corrected.py` - Korrigierte Version der Demo-Link-Registrierung
- `register_all_csv_links.py` - Registriert alle Links aus CSV-Dateien

### Analyse & Monitoring
- `check_clicked_links.py` - Überprüft geklickte Links
- `check_all_clicked_links.py` - Überprüft alle geklickten Links
- `complete_click_analysis.py` - Vollständige Klick-Analyse
- `detailed_click_times.py` - Detaillierte Klick-Zeit-Analyse
- `verify_links.py` - Verifiziert Links in Shlink

### Test-Skripte
- `test_shlink.py` - Grundlegende Shlink-Tests
- `test_shlink_service.py` - Test des Shlink-Services
- `test_shlink_playwright.py` - Playwright-Tests für Shlink

## Daten-Dateien
- `shlink_links_to_register.json` - Links die in Shlink registriert werden sollen
- `shlink_registration_results.json` - Ergebnisse der Link-Registrierung
- `shlink_registration_results_corrected.json` - Korrigierte Registrierungsergebnisse
- `shlink_csv_registration_success.json` - Erfolgreiche CSV-Registrierungen
- `shlink_csv_registration_failed.json` - Fehlgeschlagene CSV-Registrierungen
- `clicked_links_detailed.json` - Detaillierte Klick-Daten
- `complete_click_analysis.json` - Vollständige Klick-Analyse-Daten
- `detailed_click_times.json` - Detaillierte Klick-Zeit-Daten

## Verwendung

Alle Skripte verwenden den ShlinkHelper und sind für die Demo-Domain `demo.bifrotek.com` konfiguriert.

```bash
# Beispiel: Links registrieren
python shlink/scripts/register_demo_links.py

# Beispiel: Klick-Analyse durchführen
python shlink/scripts/complete_click_analysis.py
```

## Wichtige Hinweise

- Die Skripte verwenden die Shlink API mit dem konfigurierten API-Key
- Alle Links werden auf der Domain `demo.bifrotek.com` erstellt
- Besuchsstatistiken werden bei Updates beibehalten







