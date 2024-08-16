from django.db import migrations
from django.core import serializers


def load_fixtures(apps, schema_editor):
    for fixture_file in [
        '/app/host/fixtures/initial/setup_survey_data.yaml',
        '/app/host/fixtures/initial/setup_filter_data.yaml',
        '/app/host/fixtures/initial/setup_tasks.yaml',
        '/app/host/fixtures/initial/setup_status.yaml',
        '/app/host/fixtures/initial/setup_acknowledgements.yaml',
        '/app/host/fixtures/initial/setup_catalog_data.yaml',
        '/app/host/fixtures/test/setup_test_transient.yaml',
        '/app/host/fixtures/test/setup_test_task_register.yaml',
        '/app/host/fixtures/example/snapshot.yaml',
        '/app/host/fixtures/example/2010H.yaml',
        '/app/host/fixtures/example/2010ai.yaml',
        '/app/host/fixtures/example/2010ag.yaml',
    ]:
        # print(f'''  Loading fixture "{fixture_file}"...''')
        with open(fixture_file) as fp:
            # Inspired by https://stackoverflow.com/a/25981899
            objects = serializers.deserialize('yaml', fp, ignorenonexistent=True)
            for obj in objects:
                obj.save()


class Migration(migrations.Migration):

    dependencies = [
        ('host', '0023_alter_transient_name'),
    ]

    operations = [
        migrations.RunPython(load_fixtures),
    ]
