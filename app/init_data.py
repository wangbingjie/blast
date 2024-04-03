#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings_slim")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    # To reset the database prior to initialization uncomment the line below:
    # execute_from_command_line(['__main__.py', 'flush', '--noinput'])

    with open("entrypoints/initialize_dustmaps.py") as script:
        script_text = script.read()
    execute_from_command_line(["__main__.py", "shell", f"--command={script_text}"])


if __name__ == "__main__":
    main()
