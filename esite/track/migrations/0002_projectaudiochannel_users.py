# Generated by Django 2.2.13 on 2020-11-24 00:52

from django.conf import settings
from django.db import migrations
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("track", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="projectaudiochannel",
            name="users",
            field=modelcluster.fields.ParentalManyToManyField(
                related_name="tracks", to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
