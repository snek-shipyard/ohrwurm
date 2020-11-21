from wagtail.core import blocks
from esite.bifrost.helpers import register_streamfield_block
from esite.bifrost.models import (
    GraphQLString,
)


@register_streamfield_block
class TagBlock(blocks.StructBlock):
    name = blocks.CharBlock(required=True, max_length=16)

    graphql_fields = [
        GraphQLString("name"),
    ]


# SPDX-License-Identifier: (EUPL-1.2)
# Copyright © 2019-2020 Simon Prast
