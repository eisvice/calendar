# Generated by Django 5.0.4 on 2024-05-06 06:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mnts', '0002_alter_theme_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='duration',
            field=models.DecimalField(decimal_places=2, default=1.0, max_digits=5),
        ),
    ]