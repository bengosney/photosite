# Generated by Django 4.2.6 on 2023-10-27 19:04

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0004_homepage_content"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="homepage",
            name="body",
        ),
    ]