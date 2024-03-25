#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
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

    execute_from_command_line(['__main__.py', 'makemigrations'])
    execute_from_command_line(['__main__.py', 'migrate'])
    execute_from_command_line(['__main__.py', 'createsuperuser', '--noinput'])
    execute_from_command_line(['__main__.py', 'collectstatic', '--noinput'])

    with open('entrypoints/setup_initial_periodic_tasks.py') as script:
        script_text = script.read()
    execute_from_command_line(['__main__.py', 'shell', f'--command={script_text}'])

    with open('entrypoints/initialize_dustmaps.py') as script:
        script_text = script.read()
    execute_from_command_line(['__main__.py', 'shell', f'--command={script_text}'])

    execute_from_command_line(['__main__.py', 'loaddata', '/app/host/fixtures/initial/setup_survey_data.yaml'])
    execute_from_command_line(['__main__.py', 'loaddata', '/app/host/fixtures/initial/setup_filter_data.yaml'])
    execute_from_command_line(['__main__.py', 'loaddata', '/app/host/fixtures/initial/setup_catalog_data.yaml'])
    execute_from_command_line(['__main__.py', 'loaddata', '/app/host/fixtures/initial/setup_tasks.yaml'])
    execute_from_command_line(['__main__.py', 'loaddata', '/app/host/fixtures/initial/setup_status.yaml'])
    execute_from_command_line(['__main__.py', 'loaddata', '/app/host/fixtures/initial/setup_acknowledgements.yaml'])
    execute_from_command_line(['__main__.py', 'loaddata', '/app/host/fixtures/example/2010ag.yaml'])
    execute_from_command_line(['__main__.py', 'loaddata', '/app/host/fixtures/example/2010ai.yaml'])
    execute_from_command_line(['__main__.py', 'loaddata', '/app/host/fixtures/example/2010h.yaml'])
    execute_from_command_line(['__main__.py', 'loaddata', '/app/host/fixtures/example/snapshot.yaml'])

if __name__ == "__main__":
    main()
