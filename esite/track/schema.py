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
    @permission_required("track.can_assign_project_members")
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
    @permission_required("track.can_assign_project_members")
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

class AddPAC(graphene.Mutation):
    pac = graphene.Field(PACType)
    
    class Arguments:
        token = graphene.String(required=False)
        title = graphene.String(required=True)
        description = graphene.String(required=False)
        channel_id = graphene.String(required=False)
        members = graphene.List(graphene.String)
        
    @login_required
    @permission_required("track.can_add_projects")
    def mutate(
        self,
        info,
        title,
        description=None,
        channel_id=None,
        members=[],
        **kwargs
    ):
      User = get_user_model()
      pac = ProjectAudioChannel.objects.create(title=title, description=description, channel_id=channel_id)

      for member in members:
        try:
          pac.members.add(User.objects.get(username=member))
        except User.DoesNotExist:
          pass

      return AddPAC(pac=pac)

class DeletePAC(graphene.Mutation):
    success = graphene.String()

    class Arguments:
        token = graphene.String(required=False)
        id = graphene.ID(required=True)

    @login_required
    @permission_required("user.can_delete_projects")
    def mutate(
        self,
        info,
        id,
        **kwargs
    ):
        try:
            ProjectAudioChannel.objects.get(pk=id).delete()
        except ProjectAudioChannel.DoesNotExist:
            raise GraphQLError("PAC does not exist")
        
        return DeletePAC(success=True)

class UpdatePAC(graphene.Mutation):
    pac = graphene.Field(PACType)
    
    class Arguments:
        token = graphene.String(required=False)
        id = graphene.ID(required=True)
        title = graphene.String(required=False)
        description = graphene.String(required=False)
        channel_id = graphene.String(required=False)
        members = graphene.List(graphene.String)
        
    @login_required
    @permission_required("track.can_update_projects")
    def mutate(
        self,
        info,
        id,
        members=[],
        **kwargs
    ):
      print(kwargs)
      User = get_user_model()
      try:
        pac = ProjectAudioChannel.objects.get(pk=id)
      except ProjectAudioChannel.DoesNotExist:
        raise GraphQLError("PAC does not exist")

      new_members = []
      for member in members:
        try:
          new_members.append(User.objects.get(username=member))
        except User.DoesNotExist:
          pass
        
      pac.members.set(new_members)
      pac.save()
      
      ProjectAudioChannel.objects.filter(pk=id).update(**kwargs)
      # Refreshing objects from databse
      # Ref: https://docs.djangoproject.com/en/3.1/ref/models/instances/#refreshing-objects-from-database
      pac.refresh_from_db()

      return UpdatePAC(pac=pac)

class AddTrack(graphene.Mutation):
  pass

class DeleteTrack(graphene.Mutation):
  pass

class UpdateTrack(graphene.Mutation):
  pass

class Mutation(graphene.ObjectType):
    add_pac_member = AddPACMember.Field()
    delete_pac_member = DeletePACMember.Field()
    add_pac = AddPAC.Field()
    delete_pac = DeletePAC.Field()
    update_pac = UpdatePAC.Field()

# SPDX-License-Identifier: (EUPL-1.2)
# Copyright © 2019-2020 Simon Prast
