# Generated by Django 5.1.3 on 2024-12-14 01:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='part',
            name='crate_size',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='part',
            name='description',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='part',
            name='image',
            field=models.ImageField(null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='part',
            name='lbs1400',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='part',
            name='length',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='part',
            name='old_sku',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='part',
            name='old_sku_color',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='part',
            name='qty_per_box',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='part',
            name='sku_color',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='part',
            name='weight',
            field=models.IntegerField(null=True),
        ),
    ]
