"""
Configuration Manager - Quản lý cấu hình hệ thống nâng cao
Version: 1.0.0
Date: 2025-10-13

Features:
- Profile management (Dev, Staging, Production)
- Environment variables
- Secret management
- Config validation
- Import/Export configs
- Version control
"""

import json
import os
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
import hashlib


class ConfigProfile:
    """Một profile cấu hình"""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.config: Dict[str, Any] = {}
        self.env_vars: Dict[str, str] = {}
        self.secrets: Dict[str, str] = {}
        self.created_at = datetime.now()
        self.modified_at = datetime.now()
        self.version = "1.0.0"
    
    def set(self, key: str, value: Any):
        """Set giá trị config"""
        self.config[key] = value
        self.modified_at = datetime.now()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get giá trị config"""
        return self.config.get(key, default)
    
    def set_env(self, key: str, value: str):
        """Set environment variable"""
        self.env_vars[key] = value
        self.modified_at = datetime.now()
    
    def get_env(self, key: str, default: str = "") -> str:
        """Get environment variable"""
        return self.env_vars.get(key, default)
    
    def set_secret(self, key: str, value: str):
        """Set secret (will be encrypted)"""
        # Simple encryption (in production, use proper encryption)
        encrypted = self._encrypt(value)
        self.secrets[key] = encrypted
        self.modified_at = datetime.now()
    
    def get_secret(self, key: str, default: str = "") -> str:
        """Get decrypted secret"""
        encrypted = self.secrets.get(key)
        if encrypted:
            return self._decrypt(encrypted)
        return default
    
    def _encrypt(self, value: str) -> str:
        """Simple encryption (replace with proper encryption in production)"""
        # This is just a demo - use cryptography library in production
        return hashlib.sha256(value.encode()).hexdigest()
    
    def _decrypt(self, encrypted: str) -> str:
        """Decrypt (not possible with hash, just for demo)"""
        return "***encrypted***"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'description': self.description,
            'config': self.config,
            'env_vars': self.env_vars,
            'secrets': self.secrets,  # In production, don't export secrets
            'created_at': self.created_at.isoformat(),
            'modified_at': self.modified_at.isoformat(),
            'version': self.version
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConfigProfile':
        """Create from dictionary"""
        profile = cls(data['name'], data.get('description', ''))
        profile.config = data.get('config', {})
        profile.env_vars = data.get('env_vars', {})
        profile.secrets = data.get('secrets', {})
        profile.version = data.get('version', '1.0.0')
        
        if 'created_at' in data:
            profile.created_at = datetime.fromisoformat(data['created_at'])
        if 'modified_at' in data:
            profile.modified_at = datetime.fromisoformat(data['modified_at'])
        
        return profile


class ConfigurationManager:
    """
    Quản lý cấu hình hệ thống với:
    - Multiple profiles
    - Validation
    - Import/Export
    - Version control
    """
    
    def __init__(self, config_dir: str = "./configs"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
        self.profiles: Dict[str, ConfigProfile] = {}
        self.active_profile: Optional[str] = None
        
        # Default profiles
        self._create_default_profiles()
        
        # Load saved profiles
        self._load_profiles()
    
    def _create_default_profiles(self):
        """Tạo các profile mặc định"""
        
        # Development profile
        dev = ConfigProfile(
            "development",
            "Development environment configuration"
        )
        dev.set('spark.master', 'local[*]')
        dev.set('spark.driver.memory', '2g')
        dev.set('spark.executor.memory', '2g')
        dev.set('log.level', 'DEBUG')
        dev.set('debug.enabled', True)
        dev.set_env('SPARK_HOME', '/opt/spark')
        dev.set_env('JAVA_HOME', '/usr/lib/jvm/java-11')
        
        # Staging profile
        staging = ConfigProfile(
            "staging",
            "Staging environment configuration"
        )
        staging.set('spark.master', 'spark://staging-master:7077')
        staging.set('spark.driver.memory', '4g')
        staging.set('spark.executor.memory', '4g')
        staging.set('log.level', 'INFO')
        staging.set('debug.enabled', False)
        staging.set_env('SPARK_HOME', '/opt/spark')
        staging.set_env('JAVA_HOME', '/usr/lib/jvm/java-11')
        
        # Production profile
        prod = ConfigProfile(
            "production",
            "Production environment configuration"
        )
        prod.set('spark.master', 'spark://prod-master:7077')
        prod.set('spark.driver.memory', '8g')
        prod.set('spark.executor.memory', '8g')
        prod.set('spark.executor.cores', 4)
        prod.set('log.level', 'WARN')
        prod.set('debug.enabled', False)
        prod.set('monitoring.enabled', True)
        prod.set_env('SPARK_HOME', '/opt/spark')
        prod.set_env('JAVA_HOME', '/usr/lib/jvm/java-11')
        
        self.profiles['development'] = dev
        self.profiles['staging'] = staging
        self.profiles['production'] = prod
        
        self.active_profile = 'development'
    
    def create_profile(self, name: str, description: str = "",
                      base_profile: Optional[str] = None) -> ConfigProfile:
        """Tạo profile mới"""
        if name in self.profiles:
            raise ValueError(f"Profile '{name}' already exists")
        
        profile = ConfigProfile(name, description)
        
        # Copy from base profile if specified
        if base_profile and base_profile in self.profiles:
            base = self.profiles[base_profile]
            profile.config = base.config.copy()
            profile.env_vars = base.env_vars.copy()
        
        self.profiles[name] = profile
        return profile
    
    def get_profile(self, name: str) -> Optional[ConfigProfile]:
        """Lấy profile theo tên"""
        return self.profiles.get(name)
    
    def get_active_profile(self) -> Optional[ConfigProfile]:
        """Lấy profile đang active"""
        if self.active_profile:
            return self.profiles.get(self.active_profile)
        return None
    
    def set_active_profile(self, name: str) -> bool:
        """Set profile active"""
        if name not in self.profiles:
            return False
        
        self.active_profile = name
        print(f"✅ Activated profile: {name}")
        return True
    
    def delete_profile(self, name: str) -> bool:
        """Xóa profile"""
        if name not in self.profiles:
            return False
        
        # Don't delete default profiles
        if name in ['development', 'staging', 'production']:
            raise ValueError(f"Cannot delete default profile: {name}")
        
        del self.profiles[name]
        
        # If active profile was deleted, switch to development
        if self.active_profile == name:
            self.active_profile = 'development'
        
        return True
    
    def list_profiles(self) -> List[str]:
        """Liệt kê tất cả profiles"""
        return list(self.profiles.keys())
    
    def validate_profile(self, name: str) -> tuple[bool, List[str]]:
        """
        Validate cấu hình của profile
        
        Returns:
            tuple: (is_valid, error_messages)
        """
        if name not in self.profiles:
            return False, [f"Profile '{name}' not found"]
        
        profile = self.profiles[name]
        errors = []
        
        # Check required configs
        required = ['spark.master', 'log.level']
        for key in required:
            if key not in profile.config:
                errors.append(f"Missing required config: {key}")
        
        # Validate values
        if 'spark.driver.memory' in profile.config:
            mem = profile.config['spark.driver.memory']
            if not isinstance(mem, str) or not any(mem.endswith(u) for u in ['g', 'G', 'm', 'M']):
                errors.append(f"Invalid spark.driver.memory format: {mem}")
        
        if 'log.level' in profile.config:
            level = profile.config['log.level']
            valid_levels = ['DEBUG', 'INFO', 'WARN', 'ERROR']
            if level not in valid_levels:
                errors.append(f"Invalid log.level: {level}. Must be one of {valid_levels}")
        
        return len(errors) == 0, errors
    
    def export_profile(self, name: str, filepath: str) -> bool:
        """Export profile ra file JSON"""
        if name not in self.profiles:
            return False
        
        profile = self.profiles[name]
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(profile.to_dict(), f, indent=2, ensure_ascii=False)
            
            print(f"✅ Exported profile '{name}' to {filepath}")
            return True
        
        except Exception as e:
            print(f"❌ Export failed: {e}")
            return False
    
    def import_profile(self, filepath: str, overwrite: bool = False) -> Optional[str]:
        """Import profile từ file JSON"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            profile = ConfigProfile.from_dict(data)
            
            if profile.name in self.profiles and not overwrite:
                print(f"⚠️ Profile '{profile.name}' already exists. Use overwrite=True")
                return None
            
            self.profiles[profile.name] = profile
            print(f"✅ Imported profile '{profile.name}' from {filepath}")
            return profile.name
        
        except Exception as e:
            print(f"❌ Import failed: {e}")
            return None
    
    def save_profiles(self) -> bool:
        """Lưu tất cả profiles ra file"""
        try:
            save_file = self.config_dir / 'profiles.json'
            
            data = {
                'active_profile': self.active_profile,
                'profiles': {
                    name: profile.to_dict()
                    for name, profile in self.profiles.items()
                }
            }
            
            with open(save_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Saved {len(self.profiles)} profiles")
            return True
        
        except Exception as e:
            print(f"❌ Save failed: {e}")
            return False
    
    def _load_profiles(self):
        """Load profiles từ file"""
        try:
            save_file = self.config_dir / 'profiles.json'
            
            if not save_file.exists():
                return
            
            with open(save_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Load profiles (merge with defaults)
            for name, profile_data in data.get('profiles', {}).items():
                profile = ConfigProfile.from_dict(profile_data)
                self.profiles[name] = profile
            
            # Set active profile
            if 'active_profile' in data:
                self.active_profile = data['active_profile']
            
            print(f"✅ Loaded {len(self.profiles)} profiles")
        
        except Exception as e:
            print(f"⚠️ Load profiles failed: {e}")
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Lấy tóm tắt cấu hình"""
        return {
            'total_profiles': len(self.profiles),
            'active_profile': self.active_profile,
            'profiles': [
                {
                    'name': name,
                    'description': profile.description,
                    'configs': len(profile.config),
                    'env_vars': len(profile.env_vars),
                    'secrets': len(profile.secrets),
                    'modified': profile.modified_at.isoformat()
                }
                for name, profile in self.profiles.items()
            ]
        }
    
    def apply_profile_to_env(self, name: Optional[str] = None):
        """Apply profile environment variables to current process"""
        profile_name = name or self.active_profile
        if not profile_name or profile_name not in self.profiles:
            return False
        
        profile = self.profiles[profile_name]
        
        # Apply environment variables
        for key, value in profile.env_vars.items():
            os.environ[key] = value
        
        print(f"✅ Applied {len(profile.env_vars)} environment variables from '{profile_name}'")
        return True


# Global instance
_config_manager: Optional[ConfigurationManager] = None


def get_config_manager(config_dir: str = "./configs") -> ConfigurationManager:
    """Get singleton instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigurationManager(config_dir)
    return _config_manager


# Testing
if __name__ == '__main__':
    print("Testing Configuration Manager\n" + "="*70)
    
    # Create manager
    manager = ConfigurationManager("./test_configs")
    
    # List profiles
    print("\n1. Available profiles:")
    for name in manager.list_profiles():
        print(f"   - {name}")
    
    # Get active profile
    print(f"\n2. Active profile: {manager.active_profile}")
    active = manager.get_active_profile()
    if active:
        print(f"   Description: {active.description}")
        print(f"   Configs: {len(active.config)}")
        print(f"   Sample config: spark.master = {active.get('spark.master')}")
    
    # Create custom profile
    print("\n3. Creating custom profile...")
    custom = manager.create_profile(
        "my_custom",
        "My custom configuration",
        base_profile="development"
    )
    custom.set('spark.master', 'local[4]')
    custom.set('app.name', 'My Spark App')
    custom.set_env('MY_VAR', 'test_value')
    print(f"   Created: {custom.name}")
    
    # Validate
    print("\n4. Validating profiles...")
    for name in manager.list_profiles():
        is_valid, errors = manager.validate_profile(name)
        status = "✅" if is_valid else "❌"
        print(f"   {status} {name}")
        if errors:
            for error in errors:
                print(f"      - {error}")
    
    # Export/Import
    print("\n5. Testing export/import...")
    export_file = "./test_configs/exported_profile.json"
    manager.export_profile("my_custom", export_file)
    
    # Delete and re-import
    manager.delete_profile("my_custom")
    print(f"   Deleted my_custom")
    
    manager.import_profile(export_file)
    print(f"   Re-imported my_custom")
    
    # Save
    print("\n6. Saving profiles...")
    manager.save_profiles()
    
    # Summary
    print("\n7. Configuration summary:")
    summary = manager.get_config_summary()
    print(f"   Total profiles: {summary['total_profiles']}")
    print(f"   Active: {summary['active_profile']}")
    
    print("\n✅ Configuration Manager test completed!")
