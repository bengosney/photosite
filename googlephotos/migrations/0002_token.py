# Generated by Django 4.2.6 on 2023-10-08 16:33

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("googlephotos", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Token",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("access_token", models.CharField(max_length=255)),
                ("expires_at", models.FloatField()),
                ("expires_in", models.IntegerField()),
                ("token_type", models.CharField(max_length=10)),
            ],
        ),
    ]
