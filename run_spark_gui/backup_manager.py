"""
Backup Manager Module
Provides automatic backup and restore functionality
"""
import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict


class BackupManager:
    """Manages automatic backups of configuration and data"""
    
    def __init__(self, backup_dir: str = "backups", max_backups: int = 10):
        self.backup_dir = Path(backup_dir)
        self.max_backups = max_backups
        self.backup_dir.mkdir(exist_ok=True)
    
    def create_backup(self, source: str, backup_name: Optional[str] = None) -> Optional[str]:
        """Create a backup of a file or directory"""
        try:
            source_path = Path(source)
            
            if not source_path.exists():
                print(f"❌ Source does not exist: {source}")
                return None
            
            # Generate backup name with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if backup_name:
                backup_subdir = f"{backup_name}_{timestamp}"
            else:
                backup_subdir = f"backup_{timestamp}"
            
            backup_path = self.backup_dir / backup_subdir
            backup_path.mkdir(exist_ok=True)
            
            # Copy file or directory
            if source_path.is_file():
                dest = backup_path / source_path.name
                shutil.copy2(source_path, dest)
            else:
                dest = backup_path / source_path.name
                shutil.copytree(source_path, dest)
            
            # Save metadata
            metadata = {
                'timestamp': timestamp,
                'source': str(source_path.absolute()),
                'backup_path': str(backup_path.absolute()),
                'size': self._get_size(dest)
            }
            
            metadata_file = backup_path / 'backup_metadata.json'
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            print(f"✅ Backup created: {backup_path}")
            
            # Cleanup old backups
            self._cleanup_old_backups()
            
            return str(backup_path)
        
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return None
    
    def restore_backup(self, backup_path: str, restore_to: Optional[str] = None) -> bool:
        """Restore from a backup"""
        try:
            backup_path = Path(backup_path)
            
            if not backup_path.exists():
                print(f"❌ Backup does not exist: {backup_path}")
                return False
            
            # Read metadata
            metadata_file = backup_path / 'backup_metadata.json'
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                    original_source = metadata['source']
            else:
                print("⚠️ No metadata found")
                original_source = None
            
            # Determine restore destination
            if restore_to:
                dest = Path(restore_to)
            elif original_source:
                dest = Path(original_source)
            else:
                print("❌ Cannot determine restore destination")
                return False
            
            # Find the backed up item
            items = [item for item in backup_path.iterdir() 
                    if item.name != 'backup_metadata.json']
            
            if not items:
                print("❌ No backed up items found")
                return False
            
            backed_item = items[0]
            
            # Restore
            if backed_item.is_file():
                shutil.copy2(backed_item, dest)
            else:
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.copytree(backed_item, dest)
            
            print(f"✅ Restored from: {backup_path}")
            return True
        
        except Exception as e:
            print(f"❌ Restore failed: {e}")
            return False
    
    def list_backups(self) -> List[Dict]:
        """List all available backups"""
        backups = []
        
        for backup_subdir in self.backup_dir.iterdir():
            if backup_subdir.is_dir():
                metadata_file = backup_subdir / 'backup_metadata.json'
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                        backups.append({
                            'path': str(backup_subdir),
                            'name': backup_subdir.name,
                            **metadata
                        })
        
        return sorted(backups, key=lambda x: x['timestamp'], reverse=True)
    
    def _cleanup_old_backups(self):
        """Remove old backups exceeding max_backups limit"""
        backups = self.list_backups()
        
        if len(backups) > self.max_backups:
            for backup in backups[self.max_backups:]:
                try:
                    backup_path = Path(backup['path'])
                    if backup_path.exists():
                        shutil.rmtree(backup_path)
                        print(f"🗑️ Removed old backup: {backup_path.name}")
                except Exception as e:
                    print(f"❌ Failed to remove backup: {e}")
    
    def _get_size(self, path: Path) -> int:
        """Get size of file or directory"""
        if path.is_file():
            return path.stat().st_size
        else:
            total = 0
            for item in path.rglob('*'):
                if item.is_file():
                    total += item.stat().st_size
            return total


# Global instance
_backup_manager = None


def get_backup_manager(backup_dir: str = "backups", max_backups: int = 10) -> BackupManager:
    """Get or create global backup manager"""
    global _backup_manager
    if _backup_manager is None:
        _backup_manager = BackupManager(backup_dir, max_backups)
    return _backup_manager
