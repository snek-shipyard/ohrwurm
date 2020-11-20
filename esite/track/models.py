from django.db import models
from wagtail.search import index
from django.conf import settings
from django.db import models
from wagtail.core.fields import StreamField

from esite.utils.models import TimeStampMixin
from .blocks import TagBlock
from modelcluster.models import ClusterableModel
from modelcluster.fields import ParentalKey
from esite.bifrost.helpers import register_paginated_query_field


class ProjectAudioChannel(ClusterableModel):
    title = models.CharField(null=True, blank=False, max_length=250)
    description = models.TextField(null=True, blank=True)
    channel_id = models.CharField(null=True, blank=False, max_length=250)
    avatar_image = models.ForeignKey(
        settings.WAGTAILIMAGES_IMAGE_MODEL,
        null=True,
        blank=True,
        related_name="+",
        on_delete=models.SET_NULL,
    )


@register_paginated_query_field("track")
class Track(index.Indexed, TimeStampMixin):
    title = models.CharField(null=True, blank=False, max_length=250)
    audio_file = models.FileField(
        upload_to="tracks/",
        blank=True,
    )
    audio_channel = models.CharField(null=True, blank=True, max_length=250)
    audio_format = models.CharField(null=True, blank=True, max_length=250)
    audio_codec = models.CharField(null=True, blank=True, max_length=250)
    audio_bitrate = models.CharField(null=True, blank=True, max_length=250)
    description = models.TextField(null=True, blank=True)
    tags = StreamField([("label", TagBlock(required=True, icon="tag"))])
    transcript = models.TextField(null=True, blank=True)
    pac = ParentalKey(
        "ProjectAudioChannel", related_name="tracks", on_delete=models.CASCADE
    )

    search_fields = [
        index.SearchField("title"),
        index.SearchField("description"),
        index.SearchField("tags"),
        index.SearchField("transcript"),
    ]


# SPDX-License-Identifier: (EUPL-1.2)
# Copyright © 2019-2020 Simon Prast
