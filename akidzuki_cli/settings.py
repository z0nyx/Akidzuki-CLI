import json
from pathlib import Path
from typing import Optional, Dict, Any


class Settings:
    
    def __init__(self, settings_file: Optional[str] = None):
        if settings_file is None:
            self.settings_file = Path(".ssh_cli_settings.json")
        else:
            self.settings_file = Path(settings_file)
        
        self._settings = self._load_settings()
    
    def _load_settings(self) -> Dict[str, Any]:
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return self._default_settings()
    
    def _default_settings(self) -> Dict[str, Any]:
        return {
            "config_path": ".ssh_config",
            "log_file": "ssh_cli.log",
            "log_level": "INFO",
            "ssh_timeout": 10,
            "test_timeout": 5,
            "keepalive_interval": 30,
            "show_colors": True,
            "sort_by": "name",
            "default_group": None,
            "recent_limit": 5
        }
    
    def _save_settings(self):
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, indent=2, ensure_ascii=False)
        except Exception:
            pass
    
    def get(self, key: str, default: Any = None) -> Any:
        return self._settings.get(key, default)
    
    def set(self, key: str, value: Any):
        self._settings[key] = value
        self._save_settings()
    
    def get_config_path(self) -> str:
        return self.get("config_path", ".ssh_config")
    
    def get_log_file(self) -> Optional[str]:
        return self.get("log_file")
    
    def get_log_level(self) -> str:
        return self.get("log_level", "INFO")
    
    def get_ssh_timeout(self) -> int:
        return self.get("ssh_timeout", 10)
    
    def get_test_timeout(self) -> int:
        return self.get("test_timeout", 5)
    
    def get_keepalive_interval(self) -> int:
        return self.get("keepalive_interval", 30)
    
    def get_show_colors(self) -> bool:
        return self.get("show_colors", True)
    
    def get_sort_by(self) -> str:
        return self.get("sort_by", "name")
    
    def get_default_group(self) -> Optional[str]:
        return self.get("default_group")
    
    def get_recent_limit(self) -> int:
        return self.get("recent_limit", 5)
