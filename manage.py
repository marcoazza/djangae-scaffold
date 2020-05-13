#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{{ project_name }}.settings.base')
    try:
        from django.core.management import execute_from_command_line
        from djangae import environment, sandbox
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    if environment.is_development_environment():
        try:
            sandbox.start_emulators(persist_data=True)
            execute_from_command_line(sys.argv)
        finally:
            sandbox.stop_emulators()

    else:
        execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()