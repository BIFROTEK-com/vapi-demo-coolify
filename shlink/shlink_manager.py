#!/usr/bin/env python3
"""
ShlinkManager - Zentrale Klasse für Short URL Management

Diese Klasse bietet alle Funktionen für die Verwaltung von Short URLs über die Shlink API.
Kann sowohl als eigenständiges Modul als auch über MCP verwendet werden.

Verwendung:
    # Direkt
    from shlink_manager import ShlinkManager
    shlink = ShlinkManager()
    
    # Über MCP (wenn verfügbar)
    # Alle Methoden sind als MCP-Funktionen verfügbar
"""

import requests
import os
import time
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlparse, parse_qs, urlencode

class ShlinkManager:
    """
    Manager für Shlink Short URL Service
    
    Bietet alle CRUD-Operationen für Short URLs:
    - Erstellen, Lesen, Aktualisieren, Löschen
    - Statistiken und Besucher-Tracking
    - Bulk-Operationen
    - URL-Validierung
    """
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://demo.bifrotek.com/rest/v3"):
        """
        Initialisiert den ShlinkManager
        
        Args:
            api_key: Shlink API Key (wird aus .env geladen falls nicht angegeben)
            base_url: Shlink API Base URL
        """
        self.api_key = api_key or self._load_api_key()
        self.base_url = base_url
        self.short_urls_endpoint = f"{base_url}/short-urls"
        
        if not self.api_key:
            raise ValueError("Shlink API Key ist erforderlich!")
    
    def _load_api_key(self) -> Optional[str]:
        """Lädt API Key aus .env Datei"""
        root_dir = Path(__file__).parent.parent
        env_file = root_dir / '.env'
        
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        if key == 'SHLINK_API_KEY':
                            return value
        return None
    
    def _get_headers(self) -> Dict[str, str]:
        """Gibt Standard-Headers für API-Requests zurück"""
        return {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json"
        }
    
    def create_short_link(self, destination_url: str, custom_slug: Optional[str] = None, 
                         title: Optional[str] = None, tags: Optional[List[str]] = None) -> Dict:
        """
        Erstellt einen neuen Short Link
        
        Args:
            destination_url: Ziel-URL
            custom_slug: Optionaler benutzerdefinierter Slug
            title: Optionaler Titel
            tags: Optionale Tags
            
        Returns:
            Dict mit Link-Details oder Fehler-Info
        """
        payload = {"longUrl": destination_url}
        if custom_slug:
            payload["customSlug"] = custom_slug
        if title:
            payload["title"] = title
        if tags:
            payload["tags"] = tags
        
        try:
            response = requests.post(self.short_urls_endpoint, headers=self._get_headers(), json=payload)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e), "status_code": getattr(e.response, 'status_code', None)}
    
    def get_short_link(self, short_code: str) -> Dict:
        """
        Holt Details eines Short Links
        
        Args:
            short_code: Short Code des Links
            
        Returns:
            Dict mit Link-Details oder Fehler-Info
        """
        url = f"{self.short_urls_endpoint}/{short_code}"
        
        try:
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e), "status_code": getattr(e.response, 'status_code', None)}
    
    def update_short_link(self, short_code: str, new_long_url: str, 
                         title: Optional[str] = None, tags: Optional[List[str]] = None) -> Dict:
        """
        Aktualisiert einen bestehenden Short Link
        
        Args:
            short_code: Short Code des zu aktualisierenden Links
            new_long_url: Neue Ziel-URL
            title: Optionaler neuer Titel
            tags: Optionale neue Tags
            
        Returns:
            Dict mit Erfolg/Fehler-Info
        """
        url = f"{self.short_urls_endpoint}/{short_code}"
        payload = {"longUrl": new_long_url}
        if title:
            payload["title"] = title
        if tags:
            payload["tags"] = tags
        
        try:
            response = requests.put(url, headers=self._get_headers(), json=payload)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e), "status_code": getattr(e.response, 'status_code', None)}
    
    def delete_short_link(self, short_code: str) -> Dict:
        """
        Löscht einen Short Link
        
        Args:
            short_code: Short Code des zu löschenden Links
            
        Returns:
            Dict mit Erfolg/Fehler-Info
        """
        url = f"{self.short_urls_endpoint}/{short_code}"
        
        try:
            response = requests.delete(url, headers=self._get_headers())
            response.raise_for_status()
            return {"success": True}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e), "status_code": getattr(e.response, 'status_code', None)}
    
    def list_all_links(self, page: int = 1, items_per_page: int = 100) -> Dict:
        """
        Listet alle Short Links auf
        
        Args:
            page: Seitenzahl
            items_per_page: Anzahl Items pro Seite
            
        Returns:
            Dict mit Liste aller Links oder Fehler-Info
        """
        params = {"page": page, "itemsPerPage": items_per_page}
        
        try:
            response = requests.get(self.short_urls_endpoint, headers=self._get_headers(), params=params)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e), "status_code": getattr(e.response, 'status_code', None)}
    
    def get_all_links_paginated(self) -> List[Dict]:
        """
        Holt alle Links mit automatischer Paginierung
        
        Returns:
            Liste aller Links
        """
        all_links = []
        page = 1
        
        while True:
            result = self.list_all_links(page=page, items_per_page=100)
            if not result["success"]:
                break
                
            data = result["data"]
            short_urls_data = data.get('shortUrls', {})
            links = short_urls_data.get('data', [])
            
            if not links:
                break
                
            all_links.extend(links)
            pagination = short_urls_data.get('pagination', {})
            
            if page >= pagination.get('pagesCount', 1):
                break
                
            page += 1
        
        return all_links
    
    def get_link_visits(self, short_code: str) -> Dict:
        """
        Holt Besucher-Statistiken für einen Link
        
        Args:
            short_code: Short Code des Links
            
        Returns:
            Dict mit Besucher-Statistiken oder Fehler-Info
        """
        url = f"{self.short_urls_endpoint}/{short_code}/visits"
        
        try:
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            data = response.json()
            total_visits = data.get('visits', {}).get('pagination', {}).get('totalItems', 0)
            return {"success": True, "total_visits": total_visits, "data": data}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e), "status_code": getattr(e.response, 'status_code', None)}
    
    def analyze_links(self) -> Dict:
        """
        Analysiert alle Links und gibt Statistiken zurück
        
        Returns:
            Dict mit detaillierten Statistiken
        """
        print("🔍 Analysiere alle Shlink Links...")
        
        links = self.get_all_links_paginated()
        if not links:
            return {"error": "Keine Links gefunden"}
        
        # Kategorien
        with_spaces = []  # Links mit Leerzeichen in URL
        without_spaces = []  # Links ohne Leerzeichen
        bifrotek_links = []  # Bifrotek interne Links
        other_links = []  # Andere Links
        
        total_visits = 0
        links_with_visits = []
        links_without_visits = []
        
        for i, link in enumerate(links):
            if i % 50 == 0:
                print(f"   Fortschritt: {i}/{len(links)}")
            
            short_code = link.get('shortCode', '')
            long_url = link.get('longUrl', '')
            title = link.get('title', '')
            
            # Hole Besucher-Statistiken
            visits_result = self.get_link_visits(short_code)
            visits = visits_result.get('total_visits', 0) if visits_result['success'] else 0
            total_visits += visits
            
            link_info = {
                'short_code': short_code,
                'long_url': long_url,
                'title': title,
                'visits': visits
            }
            
            # Kategorisiere
            if 'bifrotek.com' in long_url:
                bifrotek_links.append(link_info)
            elif ' ' in long_url:  # Leerzeichen in URL
                with_spaces.append(link_info)
                if visits > 0:
                    links_with_visits.append(link_info)
                else:
                    links_without_visits.append(link_info)
            else:
                without_spaces.append(link_info)
        
        return {
            'total_links': len(links),
            'with_spaces': len(with_spaces),
            'without_spaces': len(without_spaces),
            'bifrotek_links': len(bifrotek_links),
            'deletable_links': len(links_without_visits),
            'not_deletable_links': len(links_with_visits),
            'total_visits': total_visits,
            'links_with_spaces': with_spaces,
            'deletable_links_list': links_without_visits,
            'not_deletable_links_list': links_with_visits
        }
    
    def delete_links_with_spaces(self, dry_run: bool = True) -> Dict:
        """
        Löscht alle Links mit Leerzeichen in der URL (nur die ohne Besuche)
        
        Args:
            dry_run: Wenn True, wird nur simuliert ohne zu löschen
            
        Returns:
            Dict mit Lösch-Ergebnissen
        """
        print(f"🔍 {'Simuliere' if dry_run else 'Lösche'} Links mit Leerzeichen...")
        
        analysis = self.analyze_links()
        deletable_links = analysis['deletable_links_list']
        
        if not deletable_links:
            return {"message": "Keine löschbaren Links mit Leerzeichen gefunden", "deleted": 0}
        
        deleted_count = 0
        errors = []
        
        for link in deletable_links:
            short_code = link['short_code']
            long_url = link['long_url']
            
            print(f"{'🗑️  Würde löschen' if dry_run else '🗑️  Lösche'}: {short_code} | {long_url[:60]}...")
            
            if not dry_run:
                result = self.delete_short_link(short_code)
                if result['success']:
                    deleted_count += 1
                else:
                    errors.append(f"{short_code}: {result['error']}")
                
                # Rate limiting
                time.sleep(0.1)
        
        return {
            "dry_run": dry_run,
            "total_deletable": len(deletable_links),
            "deleted": deleted_count,
            "errors": errors
        }
    
    def sync_with_baserow_urls(self, baserow_mappings: Dict[str, str]) -> Dict:
        """
        Synchronisiert Shlink Links mit Baserow URL-Mappings
        
        Args:
            baserow_mappings: Dict mit {short_code: new_long_url} Mappings
            
        Returns:
            Dict mit Sync-Ergebnissen
        """
        print("🔄 Synchronisiere Shlink mit Baserow URLs...")
        
        links = self.get_all_links_paginated()
        updated_count = 0
        skipped_count = 0
        error_count = 0
        
        for link in links:
            short_code = link.get('shortCode', '')
            current_long_url = link.get('longUrl', '')
            title = link.get('title', '')
            
            if not short_code or short_code not in baserow_mappings:
                skipped_count += 1
                continue
            
            new_long_url = baserow_mappings[short_code]
            
            if current_long_url == new_long_url:
                skipped_count += 1
                continue
            
            print(f"📝 Aktualisiere {short_code}...")
            print(f"   Von: {current_long_url[:80]}...")
            print(f"   Zu:  {new_long_url[:80]}...")
            
            result = self.update_short_link(short_code, new_long_url, title=title)
            if result['success']:
                updated_count += 1
            else:
                error_count += 1
                print(f"❌ Fehler: {result['error']}")
            
            time.sleep(0.1)
        
        return {
            "updated": updated_count,
            "skipped": skipped_count,
            "errors": error_count
        }

if __name__ == "__main__":
    # Test der Manager-Klasse
    manager = ShlinkManager()
    
    print("🧪 Teste ShlinkManager...")
    
    # Teste Analyse
    stats = manager.analyze_links()
    print(f"\n📊 Statistiken:")
    print(f"   Gesamt Links: {stats['total_links']}")
    print(f"   Mit Leerzeichen: {stats['with_spaces']}")
    print(f"   Löschbar: {stats['deletable_links']}")
    print(f"   Nicht löschbar: {stats['not_deletable_links']}")