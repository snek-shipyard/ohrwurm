from django.db import models
from wagtail.search import index
from django.conf import settings
from django.db import models
from wagtail.core.fields import StreamField
from esite.utils.models import TimeStampMixin
from .blocks import TagBlock
from modelcluster.models import ClusterableModel
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from esite.bifrost.helpers import register_paginated_query_field
from esite.bifrost.models import (
    GraphQLCollection,
    GraphQLForeignKey,
    GraphQLImage,
    GraphQLStreamfield,
    GraphQLString,
)
from wagtail.admin.edit_handlers import (
    FieldPanel,
    FieldRowPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    StreamFieldPanel,
    TabbedInterface,
)
import graphene
from graphql_jwt.decorators import (
    login_required,
    permission_required,
    staff_member_required,
    superuser_required,
)
from .validators import validate_audio_file

from django.contrib.auth import get_user_model


@register_paginated_query_field("project_audio_channel")
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
    users = ParentalManyToManyField(
        get_user_model(), related_name="tracks", null=True, blank=True
    )

    graphql_fields = [
        GraphQLString("title"),
        GraphQLString("description"),
        GraphQLString("channel_id"),
        GraphQLImage("avatar_image"),
        GraphQLCollection(GraphQLForeignKey, "users", get_user_model()),
    ]

    def __str__(self):
        return f"{self.title}"

    @classmethod
    @login_required
    def bifrost_queryset(cls, info, **kwargs):
        return cls.objects.filter(users=info.context.user)


@register_paginated_query_field(
    "track",
    query_params={
        "id": graphene.Int(),
        "pac": graphene.Int(),
    },
)
class Track(index.Indexed, TimeStampMixin):
    title = models.CharField(null=True, blank=False, max_length=250)
    audio_file = models.FileField(
        upload_to="tracks/", blank=True, validators=[validate_audio_file]
    )
    audio_channel = models.CharField(null=True, blank=True, max_length=250)
    audio_format = models.CharField(null=True, blank=True, max_length=250)
    audio_codec = models.CharField(null=True, blank=True, max_length=250)
    audio_bitrate = models.CharField(null=True, blank=True, max_length=250)
    description = models.TextField(null=True, blank=True)
    tags = StreamField([("tag", TagBlock(required=True, icon="tag"))], blank=True)
    transcript = models.TextField(null=True, blank=True)
    pac = ParentalKey(
        "ProjectAudioChannel", related_name="tracks", on_delete=models.CASCADE
    )

    graphql_fields = [
        GraphQLString("title"),
        GraphQLString("audio_file_url"),
        GraphQLString("audio_channel"),
        GraphQLString("audio_format"),
        GraphQLString("audio_codec"),
        GraphQLString("audio_bitrate"),
        GraphQLString("description"),
        GraphQLStreamfield("tags"),
        GraphQLString("transcript"),
        GraphQLForeignKey("pac", "track.ProjectAudioChannel"),
    ]

    search_fields = [
        index.SearchField("title"),
        index.SearchField("description"),
        index.SearchField("tags"),
        index.SearchField("transcript"),
        index.FilterField("pac"),
    ]

    panels = [
        FieldPanel("title"),
        FieldPanel("audio_file"),
        FieldPanel("audio_channel"),
        FieldPanel("audio_format"),
        FieldPanel("audio_codec"),
        FieldPanel("audio_bitrate"),
        FieldPanel("description"),
        StreamFieldPanel("tags"),
        FieldPanel("transcript"),
        FieldPanel("pac"),
    ]

    def audio_file_url(self, info, **kwargs):
        return "%s%s" % (settings.BASE_URL, self.audio_file.url)

    def __str__(self):
        return f"{self.title}"

    @classmethod
    @login_required
    def bifrost_queryset(cls, info, **kwargs):
        return cls.objects.filter(pac__users=info.context.user)


# SPDX-License-Identifier: (EUPL-1.2)
# Copyright © 2019-2020 Simon Prast
