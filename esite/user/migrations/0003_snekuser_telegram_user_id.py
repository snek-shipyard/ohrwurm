# Generated by Django 2.2.13 on 2020-11-24 01:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0002_initial_data"),
    ]

    operations = [
        migrations.AddField(
            model_name="snekuser",
            name="telegram_user_id",
            field=models.CharField(blank=True, max_length=250, null=True, unique=True),
        ),
    ]