from django.contrib.auth.models import Group
from esite.user.models import SNEKUser
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

class OhrwurmMemberType(DjangoObjectType):
    class Meta:
        model = SNEKUser
        exclude_fields = ["password"]

class AddOhrwurmMember(graphene.Mutation):
    member = graphene.Field(OhrwurmMemberType)
    generated_password = graphene.String()

    class Arguments:
        token = graphene.String(required=False)
        username = graphene.String(required=True)
        is_supervisor = graphene.Boolean(required=False)

    @login_required
    @permission_required("user.can_add_members")
    def mutate(
        self,
        info,
        username,
        is_supervisor=False,
        **kwargs
    ):
        password = SNEKUser.objects.make_random_password()
        
        try:
            member = SNEKUser.objects.get(username=username)
        except SNEKUser.DoesNotExist:
            member = SNEKUser.objects.create(username=username)
            member.set_password(password)
            
            if is_supervisor:
                member.groups.add(Group.objects.get(name="ohrwurm-supervisor"))
            else:
                member.groups.add(Group.objects.get(name="ohrwurm-member"))

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
    def mutate(
        self,
        info,
        username,
        **kwargs
    ):
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
        is_supervisor = graphene.Boolean(required=True)

    @login_required
    @permission_required("user.can_update_members")
    def mutate(
        self,
        info,
        username,
        is_supervisor=False,
        **kwargs
    ):
        try:
            member = SNEKUser.objects.get(username=username)
            supervisor_group = Group.objects.get(name="ohrwurm-supervisor")
            
            if is_supervisor:
                member.groups.add(supervisor_group)
            else:
                member.groups.remove(supervisor_group)
        except SNEKUser.DoesNotExist:
            raise GraphQLError("User does not exist")
        
        return UpdateOhrwurmMember(member=member)

class Mutation(graphene.ObjectType):
    add_ohrwurm_member = AddOhrwurmMember.Field()
    delete_ohrwurm_member = DeleteOhrwurmMember.Field()
    update_ohrwurm_member = UpdateOhrwurmMember.Field()


class Query(graphene.ObjectType):
    me = graphene.Field(
        registry.models[get_user_model()], token=graphene.String(required=False)
    )
    ohrwurm_members = graphene.List(OhrwurmMemberType, token=graphene.String(required=False))

    @login_required
    def resolve_me(self, info, **_kwargs):
        user = info.context.user

        return user

    @login_required
    @permission_required('user.can_view_members')
    def resolve_ohrwurm_members(self, info, **kwargs):
        members = SNEKUser.objects.filter(groups__name='ohrwurm-member', is_active=True)
        return members


# SPDX-License-Identifier: (EUPL-1.2)
# Copyright © 2019-2020 Simon Prast
