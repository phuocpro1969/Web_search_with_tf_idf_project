# Generated by Django 3.1.3 on 2020-12-29 07:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0002_auto_20201229_1356'),
    ]

    operations = [
        migrations.AlterField(
            model_name='data',
            name='text',
            field=models.CharField(max_length=10000000),
        ),
    ]
