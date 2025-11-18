"""Local contact cache with SQLite and sync token support."""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List

from ..shared.exceptions import APIError


class ContactCache:
    """SQLite-based contact cache with incremental sync support."""

    def __init__(self, db_path: Optional[str] = None):
        """Initialize the contact cache.

        Args:
            db_path: Path to SQLite database. If None, uses ~/.config/gwc/contacts.db
        """
        if db_path is None:
            config_dir = Path.home() / '.config' / 'gwc'
            config_dir.mkdir(parents=True, exist_ok=True)
            db_path = str(config_dir / 'contacts.db')

        self.db_path = db_path
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        """Create database schema if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS contacts (
                    resourceName TEXT PRIMARY KEY,
                    displayName TEXT,
                    email TEXT,
                    phone TEXT,
                    organization TEXT,
                    fullJson TEXT NOT NULL,
                    lastModified TEXT,
                    cachedAt TEXT NOT NULL
                )
            ''')

            conn.execute('''
                CREATE TABLE IF NOT EXISTS sync_token (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    lastSyncToken TEXT,
                    lastSyncTime TEXT
                )
            ''')

            conn.execute('''
                CREATE TABLE IF NOT EXISTS metadata (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    schemaVersion INTEGER DEFAULT 1,
                    lastFullSync TEXT
                )
            ''')

            # Ensure exactly one row in sync_token and metadata
            conn.execute('''
                INSERT OR IGNORE INTO sync_token (id, lastSyncToken, lastSyncTime)
                VALUES (1, NULL, NULL)
            ''')

            conn.execute('''
                INSERT OR IGNORE INTO metadata (id, schemaVersion)
                VALUES (1, 1)
            ''')

            conn.commit()

    def cache_contact(self, contact: Dict[str, Any]) -> None:
        """Cache a single contact.

        Args:
            contact: Contact object from Google People API

        Raises:
            APIError: If caching fails
        """
        resource_name = contact.get('resourceName')
        if not resource_name:
            raise APIError("Contact must have resourceName")

        # Extract basic fields
        names = contact.get('names', [])
        display_name = names[0].get('displayName', 'N/A') if names else 'N/A'

        emails = contact.get('emailAddresses', [])
        email = emails[0].get('value', 'N/A') if emails else 'N/A'

        phones = contact.get('phoneNumbers', [])
        phone = phones[0].get('value', 'N/A') if phones else 'N/A'

        orgs = contact.get('organizations', [])
        organization = orgs[0].get('name', 'N/A') if orgs else 'N/A'

        # Get lastModified from metadata if available
        last_modified = None
        metadata = contact.get('metadata', {})
        if metadata:
            sources = metadata.get('sources', [])
            if sources:
                last_modified = sources[0].get('updateTime')

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO contacts
                    (resourceName, displayName, email, phone, organization, fullJson, lastModified, cachedAt)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    resource_name,
                    display_name,
                    email,
                    phone,
                    organization,
                    json.dumps(contact),
                    last_modified,
                    datetime.utcnow().isoformat()
                ))
                conn.commit()
        except sqlite3.Error as e:
            raise APIError(f"Failed to cache contact: {e}")

    def cache_contacts(self, contacts: List[Dict[str, Any]]) -> None:
        """Cache multiple contacts.

        Args:
            contacts: List of contact objects from Google People API

        Raises:
            APIError: If caching fails
        """
        for contact in contacts:
            self.cache_contact(contact)

    def get_from_cache(self, resource_name: str) -> Optional[Dict[str, Any]]:
        """Get a cached contact by resource name.

        Args:
            resource_name: Contact resource name (e.g., people/c123...)

        Returns:
            Contact dict if found, None otherwise

        Raises:
            APIError: If cache lookup fails
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    'SELECT fullJson FROM contacts WHERE resourceName = ?',
                    (resource_name,)
                )
                row = cursor.fetchone()
                if row:
                    return json.loads(row[0])
                return None
        except sqlite3.Error as e:
            raise APIError(f"Failed to read from cache: {e}")

    def search_cache(self, query: str, limit: int = 30) -> List[Dict[str, Any]]:
        """Search cached contacts by email or display name.

        Args:
            query: Search query
            limit: Maximum results to return

        Returns:
            List of matching contacts from cache
        """
        query_pattern = f"{query}%"

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT fullJson FROM contacts
                    WHERE displayName LIKE ? OR email LIKE ?
                    ORDER BY displayName
                    LIMIT ?
                ''', (query_pattern, query_pattern, limit))

                results = []
                for row in cursor.fetchall():
                    results.append(json.loads(row[0]))
                return results
        except sqlite3.Error as e:
            raise APIError(f"Failed to search cache: {e}")

    def list_cached(self, limit: int = 100, sort_by: str = 'displayName') -> List[Dict[str, Any]]:
        """List cached contacts.

        Args:
            limit: Maximum results to return
            sort_by: Field to sort by (displayName, email, lastModified)

        Returns:
            List of cached contacts
        """
        valid_sorts = {'displayName', 'email', 'lastModified'}
        if sort_by not in valid_sorts:
            sort_by = 'displayName'

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(f'''
                    SELECT fullJson FROM contacts
                    ORDER BY {sort_by}
                    LIMIT ?
                ''', (limit,))

                results = []
                for row in cursor.fetchall():
                    results.append(json.loads(row[0]))
                return results
        except sqlite3.Error as e:
            raise APIError(f"Failed to list cache: {e}")

    def get_sync_token(self) -> Optional[str]:
        """Get the last sync token.

        Returns:
            Last sync token or None if no sync has been performed

        Raises:
            APIError: If cache lookup fails
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('SELECT lastSyncToken FROM sync_token WHERE id = 1')
                row = cursor.fetchone()
                return row[0] if row else None
        except sqlite3.Error as e:
            raise APIError(f"Failed to get sync token: {e}")

    def set_sync_token(self, token: Optional[str]) -> None:
        """Store the sync token.

        Args:
            token: Sync token from Google People API

        Raises:
            APIError: If cache update fails
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    'UPDATE sync_token SET lastSyncToken = ?, lastSyncTime = ? WHERE id = 1',
                    (token, datetime.utcnow().isoformat())
                )
                conn.commit()
        except sqlite3.Error as e:
            raise APIError(f"Failed to set sync token: {e}")

    def get_last_sync_time(self) -> Optional[datetime]:
        """Get the last sync time.

        Returns:
            Last sync datetime or None if no sync has been performed
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('SELECT lastSyncTime FROM sync_token WHERE id = 1')
                row = cursor.fetchone()
                if row and row[0]:
                    return datetime.fromisoformat(row[0])
                return None
        except (sqlite3.Error, ValueError):
            return None

    def should_sync(self, hours: int = 24) -> bool:
        """Check if cache should be synced.

        Args:
            hours: Number of hours before forcing a sync (default: 24)

        Returns:
            True if cache is older than specified hours, False otherwise
        """
        last_sync = self.get_last_sync_time()
        if last_sync is None:
            return True  # Never synced
        return datetime.utcnow() - last_sync > timedelta(hours=hours)

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dict with cache stats (contact count, last sync time, etc.)

        Raises:
            APIError: If stats retrieval fails
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get contact count
                cursor = conn.execute('SELECT COUNT(*) FROM contacts')
                contact_count = cursor.fetchone()[0]

                # Get last sync time
                cursor = conn.execute('SELECT lastSyncTime FROM sync_token WHERE id = 1')
                last_sync_row = cursor.fetchone()
                last_sync_time = last_sync_row[0] if last_sync_row else None

                # Get cache size
                db_size = Path(self.db_path).stat().st_size if Path(self.db_path).exists() else 0

                return {
                    'contact_count': contact_count,
                    'last_sync_time': last_sync_time,
                    'cache_size_bytes': db_size,
                    'should_sync': self.should_sync()
                }
        except sqlite3.Error as e:
            raise APIError(f"Failed to get cache stats: {e}")

    def clear_cache(self) -> None:
        """Clear all cached contacts and reset sync token.

        Raises:
            APIError: If cache clearing fails
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('DELETE FROM contacts')
                conn.execute('UPDATE sync_token SET lastSyncToken = NULL, lastSyncTime = NULL WHERE id = 1')
                conn.execute('UPDATE metadata SET lastFullSync = NULL WHERE id = 1')
                conn.commit()
        except sqlite3.Error as e:
            raise APIError(f"Failed to clear cache: {e}")

    def delete_contact_from_cache(self, resource_name: str) -> None:
        """Remove a contact from cache.

        Args:
            resource_name: Contact resource name

        Raises:
            APIError: If deletion fails
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('DELETE FROM contacts WHERE resourceName = ?', (resource_name,))
                conn.commit()
        except sqlite3.Error as e:
            raise APIError(f"Failed to delete from cache: {e}")

    def export_json(self, file_path: str) -> None:
        """Export all cached contacts as JSON.

        Args:
            file_path: Path to write JSON file

        Raises:
            APIError: If export fails
        """
        try:
            contacts = self.list_cached(limit=10000)
            with open(file_path, 'w') as f:
                json.dump(contacts, f, indent=2)
        except (OSError, sqlite3.Error) as e:
            raise APIError(f"Failed to export cache: {e}")
