# Generated by Django 5.1.3 on 2024-12-17 23:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('manufacturingLists', '0002_manufacturiglistitem_sku_color'),
        ('parts', '0003_remove_part_old_sku_color_remove_part_sku_color'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ManufacturigListItem',
            new_name='ManufacturingListItem',
        ),
    ]
