#!/usr/bin/env python
import os
import sys

def main():
    # 1) Apunta al módulo de settings del proyecto "core"
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Django no está instalado o el entorno virtual no está activo."
        ) from exc
    # 2) Ejecuta el comando (runserver, migrate, etc.)
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
