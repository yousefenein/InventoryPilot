# Generated by Django 5.1.3 on 2025-03-23 02:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0008_merge_20250322_2207'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orders',
            name='pack_complete_timestamp',
        ),
        migrations.RemoveField(
            model_name='orders',
            name='ship_complete_timestamp',
        ),
    ]
