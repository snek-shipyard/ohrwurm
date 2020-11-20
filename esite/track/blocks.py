from wagtail.core import blocks


class TagBlock(blocks.StructBlock):
    name = blocks.CharBlock(required=True, max_length=16)


# SPDX-License-Identifier: (EUPL-1.2)
# Copyright © 2019-2020 Simon Prast
