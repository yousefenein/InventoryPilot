# Generated by Django 5.1.3 on 2025-04-03 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0015_inventorypicklistitem_manually_picked'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventorypicklistitem',
            name='repick',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='inventorypicklistitem',
            name='repick_reason',
            field=models.TextField(blank=True, null=True),
        ),
    ]
