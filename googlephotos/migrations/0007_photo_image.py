# Generated by Django 4.2.6 on 2023-10-13 07:39

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("googlephotos", "0006_photo_album"),
    ]

    operations = [
        migrations.AddField(
            model_name="photo",
            name="image",
            field=models.ImageField(null=True, upload_to="googlephotos"),
        ),
    ]
