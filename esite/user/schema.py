import hashlib

import graphene
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.models import Group
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from graphql_jwt.decorators import (
    login_required,
    permission_required,
    staff_member_required,
    superuser_required,
)

from esite.bifrost.registry import registry
from esite.track.models import ProjectAudioChannel
from esite.user.models import SNEKUser


class OhrwurmMemberType(DjangoObjectType):
    class Meta:
        model = SNEKUser
        exclude_fields = ["password"]

    is_ohrwurm_supervisor = graphene.Boolean()

    def resolve_is_ohrwurm_supervisor(instance, info, **kwargs):
        return instance.is_ohrwurm_supervisor(info)


class AddOhrwurmMember(graphene.Mutation):
    member = graphene.Field(OhrwurmMemberType)
    generated_password = graphene.String()

    class Arguments:
        token = graphene.String(required=False)
        username = graphene.String(required=True)
        pacs = graphene.List(graphene.ID, required=False)
        is_ohrwurm_supervisor = graphene.Boolean(required=False)

    @login_required
    @permission_required("user.can_add_members")
    def mutate(self, info, username, pacs=[], is_ohrwurm_supervisor=False, **kwargs):
        password = SNEKUser.objects.make_random_password()

        try:
            member = SNEKUser.objects.get(username=username)
        except SNEKUser.DoesNotExist:
            member = SNEKUser.objects.create(username=username, is_active=True)
            member.set_password(hashlib.sha256(str.encode(password)).hexdigest())

            if is_ohrwurm_supervisor:
                member.groups.add(Group.objects.get(name="ohrwurm-supervisor"))

            member.groups.add(Group.objects.get(name="ohrwurm-member"))

            member.pacs.add(*pacs)

            member.save()
        else:
            raise GraphQLError("User already exists")

        return AddOhrwurmMember(member=member, generated_password=password)


class DeleteOhrwurmMember(graphene.Mutation):
    success = graphene.String()

    class Arguments:
        token = graphene.String(required=False)
        username = graphene.String(required=True)

    @login_required
    @permission_required("user.can_delete_members")
    def mutate(self, info, username, **kwargs):
        try:
            user = SNEKUser.objects.get(username=username)
            user.is_active = False
            user.save()
        except SNEKUser.DoesNotExist:
            raise GraphQLError("User does not exist")

        return DeleteOhrwurmMember(success=True)


class UpdateOhrwurmMember(graphene.Mutation):
    member = graphene.Field(OhrwurmMemberType)

    class Arguments:
        token = graphene.String(required=False)
        username = graphene.String(required=True)
        pacs = graphene.List(graphene.ID, required=False)
        is_ohrwurm_supervisor = graphene.Boolean(required=False)

    @login_required
    @permission_required("user.can_update_members")
    def mutate(self, info, username, pacs=None, is_ohrwurm_supervisor=False, **kwargs):
        try:
            member = SNEKUser.objects.get(username=username)
            supervisor_group = Group.objects.get(name="ohrwurm-supervisor")

            if is_ohrwurm_supervisor:
                member.groups.add(supervisor_group)
            else:
                member.groups.remove(supervisor_group)

            if pacs:
                member.pacs.set(pacs)

        except SNEKUser.DoesNotExist:
            raise GraphQLError("User does not exist")

        return UpdateOhrwurmMember(member=member)


class ChangePassword(graphene.Mutation):
    success = graphene.Boolean()

    class Arguments:
        token = graphene.String(required=False)
        new_password = graphene.String(required=True)

    @login_required
    def mutate(self, info, new_password, **kwargs):
        try:
            username = info.context.user.username
            user = SNEKUser.objects.get(username=username)

            if user.check_password(new_password):
                raise GraphQLError("The new password must not match the old one")

            user.set_password(new_password)
            user.password_changed = True
            # Session invalidation on password change
            # Ref: https://docs.djangoproject.com/en/3.1/topics/auth/default/#session-invalidation-on-password-change
            update_session_auth_hash(info.context, user)
            user.save()
        except SNEKUser.DoesNotExist:
            raise GraphQLError("User does not exist")

        return DeleteOhrwurmMember(success=True)


class Mutation(graphene.ObjectType):
    add_ohrwurm_member = AddOhrwurmMember.Field()
    delete_ohrwurm_member = DeleteOhrwurmMember.Field()
    update_ohrwurm_member = UpdateOhrwurmMember.Field()
    change_password = ChangePassword.Field()


class Query(graphene.ObjectType):
    me = graphene.Field(
        registry.models[get_user_model()], token=graphene.String(required=False)
    )
    ohrwurm_members = graphene.List(
        OhrwurmMemberType, token=graphene.String(required=False)
    )

    @login_required
    def resolve_me(self, info, **_kwargs):
        user = info.context.user

        return user

    @login_required
    @permission_required("user.can_view_members")
    def resolve_ohrwurm_members(self, info, **kwargs):
        members = SNEKUser.objects.filter(groups__name="ohrwurm-member", is_active=True)
        return members


# SPDX-License-Identifier: (EUPL-1.2)
# Copyright © 2019-2020 Simon Prast
