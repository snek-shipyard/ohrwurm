from django.contrib.auth import get_user_model

import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from graphql_jwt.decorators import (
    login_required,
    permission_required,
    staff_member_required,
    superuser_required,
)
from .models import Track


class Query(graphene.ObjectType):
    tracks = graphene.List(graphene.Field(Track))

    @login_required
    def resolve_tracks(self, info, token, **kwargs):
        try:
            user = Track
            return True
        except get_user_model().DoesNotExist:
            return False

    @login_required
    def resolve_me(self, info, **_kwargs):
        user = info.context.user

        return user


# SPDX-License-Identifier: (EUPL-1.2)
# Copyright © 2019-2020 Simon Prast
