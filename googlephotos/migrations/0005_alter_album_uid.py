# Generated by Django 4.2.6 on 2023-10-12 19:32

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("googlephotos", "0004_delete_credentials"),
    ]

    operations = [
        migrations.AlterField(
            model_name="album",
            name="uid",
            field=models.CharField(max_length=255, unique=True),
        ),
    ]