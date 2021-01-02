from esite.track.models import ProjectAudioChannel
from django.contrib.auth.models import Group
from esite.user.models import SNEKUser
from django.contrib.auth import get_user_model, update_session_auth_hash

import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from graphql_jwt.decorators import (
    login_required,
    permission_required,
    staff_member_required,
    superuser_required,
)

class PACType(DjangoObjectType):
    class Meta:
        model = ProjectAudioChannel

class AddPACMember(graphene.Mutation):
    pac = graphene.Field(PACType)
    
    class Arguments:
        token = graphene.String(required=False)
        pac_id = graphene.ID(required=True)
        username = graphene.String(required=True)
        
    @login_required
    @permission_required("track.can_assign_members")
    def mutate(
        self,
        info,
        pac_id,
        username,
        **kwargs
    ):
        try:
            user = SNEKUser.objects.get(username=username)
            pac = ProjectAudioChannel.objects.get(id=pac_id)
        except SNEKUser.DoesNotExist:
            raise GraphQLError("User does not exist")
        except ProjectAudioChannel.DoesNotExist:
          raise GraphQLError("PAC does not exist")
        
        pac.members.add(user)
        pac.save()
        
        return AddPACMember(pac=pac)
      
class DeletePACMember(graphene.Mutation):
    pac = graphene.Field(PACType)
    
    class Arguments:
        token = graphene.String(required=False)
        pac_id = graphene.ID(required=True)
        username = graphene.String(required=True)
        
    @login_required
    @permission_required("track.can_assign_members")
    def mutate(
        self,
        info,
        pac_id,
        username,
        **kwargs
    ):
        try:
            user = SNEKUser.objects.get(username=username)
            pac = ProjectAudioChannel.objects.get(id=pac_id)
        except SNEKUser.DoesNotExist:
            raise GraphQLError("User does not exist")
        except ProjectAudioChannel.DoesNotExist:
          raise GraphQLError("PAC does not exist")
        
        pac.members.remove(user)
        pac.save()
        
        return DeletePACMember(pac=pac)
    
class Mutation(graphene.ObjectType):
    add_pac_member = AddPACMember.Field()
    delete_pac_member = DeletePACMember.Field()

# SPDX-License-Identifier: (EUPL-1.2)
# Copyright © 2019-2020 Simon Prast
