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

from esite.bifrost.registry import registry


class Query(graphene.ObjectType):
    me = graphene.Field(
        registry.models[get_user_model()], token=graphene.String(required=False)
    )

    @login_required
    def resolve_me(self, info, **_kwargs):
        user = info.context.user

        return user


# SPDX-License-Identifier: (EUPL-1.2)
# Copyright © 2019-2020 Simon Prast
