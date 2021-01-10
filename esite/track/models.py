import graphene
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from graphql_jwt.decorators import (
    login_required,
    permission_required,
    staff_member_required,
    superuser_required,
)
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.models import ClusterableModel
from wagtail.admin.edit_handlers import (
    FieldPanel,
    FieldRowPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    StreamFieldPanel,
    TabbedInterface,
)
from wagtail.core.fields import StreamField
from wagtail.search import index

from esite.bifrost.helpers import register_paginated_query_field
from esite.bifrost.models import (
    GraphQLCollection,
    GraphQLForeignKey,
    GraphQLImage,
    GraphQLStreamfield,
    GraphQLString,
    GraphqlDatetime,
)
from esite.utils.edit_handlers import ReadOnlyPanel
from esite.utils.models import TimeStampMixin

from .blocks import AttendeeBlock, TagBlock
from .validators import validate_audio_file


@register_paginated_query_field(
    "project_audio_channel",
    query_params={
        "token": graphene.String(),
    },
)
class ProjectAudioChannel(index.Indexed, ClusterableModel):
    title = models.CharField(null=True, blank=False, max_length=250)
    description = models.TextField(null=True, blank=True)
    channel_id = models.CharField(null=True, blank=True, max_length=250)
    avatar_image = models.ForeignKey(
        settings.WAGTAILIMAGES_IMAGE_MODEL,
        null=True,
        blank=True,
        related_name="+",
        on_delete=models.SET_NULL,
    )
    members = ParentalManyToManyField(
        get_user_model(), related_name="pacs", null=True, blank=True
    )

    search_fields = [
        index.SearchField("title"),
        index.SearchField("created_at"),
        index.SearchField("description"),
        index.FilterField("snekuser_id"),
    ]

    graphql_fields = [
        GraphQLString("title", required=True),
        GraphQLString("description"),
        GraphQLString("channel_id"),
        GraphQLImage("avatar_image"),
        GraphQLCollection(GraphQLForeignKey, "members", get_user_model()),
    ]

    def __str__(self):
        return f"{self.title}"

    @classmethod
    @login_required
    def bifrost_queryset(cls, info, **kwargs):
        return cls.objects.filter(members=info.context.user)


@register_paginated_query_field(
    "track",
    query_params={
        "token": graphene.String(),
        "id": graphene.Int(),
        "pac": graphene.ID(),
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
    attendees = StreamField(
        [("attendee", AttendeeBlock(required=True, icon="user"))], blank=True
    )
    transcript = models.TextField(null=True, blank=True)
    pac = ParentalKey(
        "ProjectAudioChannel", related_name="tracks", on_delete=models.CASCADE
    )

    graphql_fields = [
        GraphQLString("title", required=True),
        GraphqlDatetime("created_at", required=True),
        GraphQLString("audio_file_url"),
        GraphQLString("audio_channel"),
        GraphQLString("audio_format"),
        GraphQLString("audio_codec"),
        GraphQLString("audio_bitrate"),
        GraphQLString("description"),
        GraphQLStreamfield("tags"),
        GraphQLStreamfield("attendees"),
        GraphQLString("transcript"),
        GraphQLForeignKey("pac", "track.ProjectAudioChannel"),
    ]

    search_fields = [
        index.SearchField("title"),
        index.SearchField("created_at"),
        index.SearchField("description"),
        index.SearchField("tags"),
        index.SearchField("attendees"),
        index.SearchField("transcript"),
        index.FilterField("pac"),
        index.FilterField("snekuser_id"),
    ]

    panels = [
        FieldPanel("title"),
        ReadOnlyPanel("created_at"),
        FieldPanel("audio_file"),
        FieldPanel("audio_channel"),
        FieldPanel("audio_format"),
        FieldPanel("audio_codec"),
        FieldPanel("audio_bitrate"),
        FieldPanel("description"),
        StreamFieldPanel("tags"),
        StreamFieldPanel("attendees"),
        FieldPanel("transcript"),
        FieldPanel("pac"),
    ]

    def audio_file_url(self, info, **kwargs):
        return (
            "%s%s" % (settings.BASE_URL, self.audio_file.url)
            if self.audio_file.name
            else None
        )

    def __str__(self):
        return f"{self.title}"

    @classmethod
    @login_required
    def bifrost_queryset(cls, info, **kwargs):
        return cls.objects.filter(pac__members=info.context.user)


# SPDX-License-Identifier: (EUPL-1.2)
# Copyright © 2019-2020 Simon Prast
