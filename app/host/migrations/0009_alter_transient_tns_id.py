# Generated by Django 3.2.9 on 2022-11-08 19:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('host', '0008_auto_20220822_2335'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transient',
            name='tns_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
