"""Settings de prueba local: hereda del original pero usa SQLite.

Útil para probar sin levantar PostgreSQL/Docker:
    python manage.py <cmd> --settings=Tienda.settings_sqlite
"""
from .settings import *  # noqa: F401,F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
    }
}

# Permite el cliente de pruebas local y localhost.
ALLOWED_HOSTS = ["*"]
