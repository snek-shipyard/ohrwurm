import json
import uuid

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
class SNEKUser(AbstractUser, ClusterableModel):
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

    # Custom save function
    def save(self, *args, **kwargs):
        if not self.username:
            self.username = str(uuid.uuid4())

        if not self.is_staff:
            if not self.is_active:
                self.is_active = True

                send_mail(
                    "got activated",
                    "You got activated.",
                    "noreply@snek.at",
                    [self.email],
                    fail_silently=False,
                )

        else:
            self.is_active = False

        super(SNEKUser, self).save(*args, **kwargs)

    panels = [
        FieldPanel("username"),
        FieldPanel("first_name"),
        FieldPanel("last_name"),
        FieldPanel("email"),
        FieldPanel("is_staff"),
        FieldPanel("is_active"),
    ]

    graphql_fields = [
        GraphQLString("username"),
        GraphQLString("first_name"),
        GraphQLString("last_name"),
        GraphQLString("email"),
        GraphQLBoolean("is_active"),
    ]

    def __str__(self):
        return self.username


# SPDX-License-Identifier: (EUPL-1.2)
# Copyright © 2019-2020 Simon Prast
