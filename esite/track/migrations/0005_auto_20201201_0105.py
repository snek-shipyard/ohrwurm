# Generated by Django 2.2.13 on 2020-12-01 00:05

from django.db import migrations
import wagtail.core.blocks
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ("track", "0004_auto_20201128_0004"),
    ]

    operations = [
        migrations.AddField(
            model_name="track",
            name="attendees",
            field=wagtail.core.fields.StreamField(
                [
                    (
                        "attendee",
                        wagtail.core.blocks.StructBlock(
                            [
                                (
                                    "name",
                                    wagtail.core.blocks.CharBlock(
                                        max_length=250, required=True
                                    ),
                                )
                            ],
                            icon="user",
                            required=True,
                        ),
                    )
                ],
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="track",
            name="tags",
            field=wagtail.core.fields.StreamField(
                [
                    (
                        "tag",
                        wagtail.core.blocks.StructBlock(
                            [
                                (
                                    "name",
                                    wagtail.core.blocks.CharBlock(
                                        max_length=16, required=True
                                    ),
                                ),
                                (
                                    "significance",
                                    wagtail.core.blocks.ChoiceBlock(
                                        choices=[
                                            ("sucess", "Sucess"),
                                            ("danger", "Danger"),
                                            ("warning", "Warning"),
                                            ("info", "Info"),
                                            ("light", "Light"),
                                            ("dark", "Dark"),
                                        ],
                                        icon="cup",
                                    ),
                                ),
                            ],
                            icon="tag",
                            required=True,
                        ),
                    )
                ],
                blank=True,
            ),
        ),
    ]
