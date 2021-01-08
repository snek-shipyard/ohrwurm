from wagtail.core import blocks

from esite.bifrost.helpers import register_streamfield_block
from esite.bifrost.models import GraphQLString



@register_streamfield_block
class TagBlock(blocks.StructBlock):
    SIGNIFICANCE_CHOICES = [
        ("success", "Success"),
        ("danger", "Danger"),
        ("warning", "Warning"),
        ("info", "Info"),
        ("light", "Light"),
        ("dark", "Dark"),
    ]
    name = blocks.CharBlock(required=True, max_length=16)
    significance = blocks.ChoiceBlock(
        choices=SIGNIFICANCE_CHOICES, required=True, icon="cup"
    )

    graphql_fields = [
        GraphQLString("name"),
        GraphQLString("significance"),
    ]


@register_streamfield_block
class AttendeeBlock(blocks.StructBlock):
    name = blocks.CharBlock(required=True, max_length=250)

    graphql_fields = [
        GraphQLString("name"),
    ]


# SPDX-License-Identifier: (EUPL-1.2)
# Copyright © 2019-2020 Simon Prast
