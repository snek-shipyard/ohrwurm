# Generated by Django 2.2.13 on 2020-11-27 23:04

from django.db import migrations
import esite.colorfield.blocks
import wagtail.core.blocks
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ("track", "0003_auto_20201124_0257"),
    ]

    operations = [
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
                                    "color",
                                    esite.colorfield.blocks.ColorBlock(required=True),
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
