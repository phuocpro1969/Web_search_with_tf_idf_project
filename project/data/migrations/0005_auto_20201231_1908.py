# Generated by Django 3.1.3 on 2020-12-31 12:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0004_auto_20201231_1905'),
    ]

    operations = [
        migrations.AlterField(
            model_name='data',
            name='text',
            field=models.CharField(blank=True, max_length=10000000, null=True),
        ),
    ]
