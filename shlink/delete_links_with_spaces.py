#!/usr/bin/env python3
"""
Löscht alle Shlink Links mit Leerzeichen in der URL (nur die ohne Besuche)

Verwendung:
    python delete_links_with_spaces.py --dry-run    # Simuliert nur
    python delete_links_with_spaces.py --execute    # Löscht wirklich
"""

import argparse
import sys
from pathlib import Path

# Füge das shlink Verzeichnis zum Python-Pfad hinzu
sys.path.append(str(Path(__file__).parent))

from shlink_manager import ShlinkManager

def main():
    parser = argparse.ArgumentParser(description='Löscht Links mit Leerzeichen in der URL')
    parser.add_argument('--dry-run', action='store_true', help='Nur simulieren, nicht wirklich löschen')
    parser.add_argument('--execute', action='store_true', help='Wirklich löschen')
    
    args = parser.parse_args()
    
    if not args.dry_run and not args.execute:
        print("❌ Bitte --dry-run oder --execute angeben!")
        return
    
    dry_run = args.dry_run
    
    print("🚀 Starte Shlink Link-Bereinigung...")
    
    manager = ShlinkManager()
    
    # Zeige zuerst Statistiken
    print("\n📊 Aktuelle Statistiken:")
    stats = manager.analyze_links()
    print(f"   Gesamt Links: {stats['total_links']}")
    print(f"   Mit Leerzeichen: {stats['with_spaces']}")
    print(f"   Löschbar: {stats['deletable_links']}")
    print(f"   Nicht löschbar: {stats['not_deletable_links']}")
    
    if stats['deletable_links'] == 0:
        print("✅ Keine Links mit Leerzeichen zum Löschen gefunden!")
        return
    
    # Zeige Details der löschbaren Links
    print(f"\n🗑️  {stats['deletable_links']} Links können gelöscht werden:")
    for link in stats['deletable_links_list']:
        print(f"   - {link['short_code']}: {link['long_url'][:80]}...")
    
    if dry_run:
        print(f"\n🔍 DRY RUN - Würde {stats['deletable_links']} Links löschen")
        print("   Verwende --execute um wirklich zu löschen")
    else:
        # Bestätigung
        confirm = input(f"\n⚠️  Wirklich {stats['deletable_links']} Links löschen? (ja/nein): ")
        if confirm.lower() not in ['ja', 'yes', 'y']:
            print("❌ Abgebrochen!")
            return
        
        # Lösche Links
        result = manager.delete_links_with_spaces(dry_run=False)
        
        print(f"\n🎉 Bereinigung abgeschlossen!")
        print(f"   Gelöscht: {result['deleted']}")
        if result['errors']:
            print(f"   Fehler: {len(result['errors'])}")
            for error in result['errors']:
                print(f"     - {error}")

if __name__ == "__main__":
    main()
