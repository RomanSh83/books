from pathlib import Path

from dynaconf import Dynaconf



class Config:
    settings = Dynaconf(environments=True, envvar_prefix="", settings_file=["config/settings.yaml"])

    settings.BASE_DIR = Path(__file__).resolve().parents[3]

    _media_root = settings.BASE_DIR / settings.MEDIA_DIR
    _media_root.mkdir(parents=True, exist_ok=True)

    settings.MEDIA_ROOT = _media_root

def get_settings():
    return Config.settings