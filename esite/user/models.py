import django.contrib.auth.validators
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
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
from wagtail.search import index
from wagtail.core.fields import RichTextField, StreamField
from wagtail.snippets.edit_handlers import SnippetChooserPanel

from esite.bifrost.helpers import register_streamfield_block
from esite.bifrost.models import (
    GraphQLBoolean,
    GraphQLCollection,
    GraphQLEmbed,
    GraphQLField,
    GraphQLForeignKey,
    GraphQLImage,
    GraphQLSnippet,
    GraphQLStreamfield,
    GraphQLString,
)

# from esite.utils.models import BasePage


# Extend AbstractUser Model from django.contrib.auth.models
class SNEKUser(AbstractUser, index.Indexed, ClusterableModel):
    username = models.CharField(
        "username",
        null=True,
        blank=False,
        error_messages={"unique": "A user with that username already exists."},
        help_text="Required. 36 characters or fewer. Letters, digits and @/./+/-/_ only.",
        max_length=36,
        unique=True,
        validators=[django.contrib.auth.validators.UnicodeUsernameValidator()],
    )
    password_changed = models.BooleanField(default=False)
    telegram_user_id = models.CharField(null=True, blank=True, max_length=250)

    def is_ohrwurm_supervisor(self, info, **kwargs):
        return self.groups.filter(name="ohrwurm-supervisor").exists()

    # Custom save function
    def save(self, *args, **kwargs):
        super(SNEKUser, self).save(*args, **kwargs)

    panels = [
        FieldPanel("username"),
        MultiFieldPanel(
            [
                FieldPanel("is_active"),
                FieldPanel("password_changed"),
            ],
            "Settings",
        ),
        MultiFieldPanel(
            [
                FieldPanel("telegram_user_id"),
            ],
            "Telegram",
        ),
    ]

    graphql_fields = [
        GraphQLString("username"),
        GraphQLBoolean("is_active"),
        GraphQLBoolean("is_ohrwurm_supervisor"),
        GraphQLBoolean("password_changed"),
        GraphQLCollection(GraphQLForeignKey, "pacs", "track.ProjectAudioChannel"),
    ]

    def __str__(self):
        return self.username


# SPDX-License-Identifier: (EUPL-1.2)
# Copyright © 2019-2020 Simon Prast
