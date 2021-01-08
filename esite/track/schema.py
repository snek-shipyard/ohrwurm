import io
import json

import graphene
from django.conf import settings
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.models import Group
from django.core.files import File
from graphene_django import DjangoObjectType
from graphene_file_upload.scalars import Upload
from graphql import GraphQLError
from graphql_jwt.decorators import (
    login_required,
    permission_required,
    staff_member_required,
    superuser_required,
)
from pydub import AudioSegment

from esite.track.models import ProjectAudioChannel, Track
from esite.user.models import SNEKUser


class PACType(DjangoObjectType):
    class Meta:
        model = ProjectAudioChannel


class TrackType(DjangoObjectType):
    class Meta:
        model = Track
        exclude = ["audio_file"]

    audio_file_url = graphene.String()

    def resolve_audio_file_url(instance, info, **kwargs):
        return (
            "%s%s" % (settings.BASE_URL, instance.audio_file.url)
            if instance.audio_file.name
            else None
        )


class Significance(graphene.Enum):
    SUCCESS = "success"
    DANGER = "danger"
    WARNING = "warning"
    INFO = "info"
    LIGHT = "light"
    DARK = "dark"


class TagType(graphene.InputObjectType):
    name = graphene.String()
    significance = Significance()


class AttendeeType(graphene.InputObjectType):
    name = graphene.String()


class AddPACMember(graphene.Mutation):
    pac = graphene.Field(PACType)

    class Arguments:
        token = graphene.String(required=False)
        pac_id = graphene.ID(required=True)
        username = graphene.String(required=True)

    @login_required
    @permission_required("track.can_assign_project_members")
    def mutate(self, info, pac_id, username, **kwargs):
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
    def mutate(self, info, pac_id, username, **kwargs):
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
        self, info, title, description=None, channel_id=None, members=[], **kwargs
    ):
        User = get_user_model()
        pac = ProjectAudioChannel.objects.create(
            title=title, description=description, channel_id=channel_id
        )

        for member in members:
            try:
                pac.members.add(User.objects.get(username=member))
            except User.DoesNotExist:
                pass

        pac.save()

        return AddPAC(pac=pac)


class DeletePAC(graphene.Mutation):
    success = graphene.String()

    class Arguments:
        token = graphene.String(required=False)
        id = graphene.ID(required=True)

    @login_required
    @permission_required("track.can_delete_projects")
    def mutate(self, info, id, **kwargs):
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
    def mutate(self, info, id, members=None, **kwargs):
        print(kwargs)
        User = get_user_model()
        try:
            pac = ProjectAudioChannel.objects.get(pk=id)
        except ProjectAudioChannel.DoesNotExist:
            raise GraphQLError("PAC does not exist")

        if members:
            new_members = []
            for member in members:
                try:
                    new_members.append(User.objects.get(username=member))
                except User.DoesNotExist:
                    pass

            pac.members.set(new_members)
        pac.save()

        if kwargs.get("token"):
            kwargs.pop("token")
        ProjectAudioChannel.objects.filter(pk=id).update(**kwargs)
        # Refreshing objects from databse
        # Ref: https://docs.djangoproject.com/en/3.1/ref/models/instances/#refreshing-objects-from-database
        pac.refresh_from_db()

        return UpdatePAC(pac=pac)


class AddTrack(graphene.Mutation):
    track = graphene.Field(TrackType)

    class Arguments:
        token = graphene.String(required=False)
        title = graphene.String(required=True)
        description = graphene.String(required=False)
        pac_id = graphene.ID(required=True)
        created_At = graphene.DateTime(required=False)
        tags = graphene.List(TagType, required=False)
        attendees = graphene.List(AttendeeType, required=False)
        audio_file = Upload(required=False)

    @login_required
    @permission_required("track.can_add_tracks")
    def mutate(
        self,
        info,
        title,
        pac_id,
        audio_file=None,
        description=None,
        created_At=None,
        tags=[],
        attendees=[],
        **kwargs,
    ):

        if audio_file.content_type == "audio/x-wav":
            audio_seg = AudioSegment.from_wav(audio_file.file)
            audio_out = io.BytesIO()
            audio_out = audio_seg.export(
                audio_out,
                bitrate="128k",
                format="ogg",
                codec="opus",
                parameters=["-strict", "-2", "-ac", "2", "-vol", "150"],
                tags={
                    "ARTIST": "waveater",
                    "GENRE": "Meeting/Trashtalk",
                    "ALBUM": "waveater",
                    "TITLE": f"{audio_file._name.split('.')[0]}_{created_At.strftime('%m-%d_%H-%M')}",
                    "DATE": f"{created_At.strftime('%Y/%m/%d_%H:%M:%S')}",
                    "COMMENT": f"A wav file converted to telegram voice message.",
                    "CONTACT": "@waveater",
                },
            )
            audio_out.name = f"{audio_file._name.split('.')[0]}_{created_At.strftime('%m-%d_%H-%M')}.ogg"

            audio_file = File(audio_out)

        track = Track(
            title=title, description=description, pac_id=pac_id, audio_file=audio_file
        )
        track.attendees = json.dumps(
            [{"type": "attendee", "value": attendee} for attendee in attendees]
        )
        track.tags = json.dumps([{"type": "tag", "value": tag} for tag in tags])

        track.save()

        if created_At:
            track.created_at = created_At

            track.save()

        return AddTrack(track=track)


class DeleteTrack(graphene.Mutation):
    success = graphene.String()

    class Arguments:
        token = graphene.String(required=False)
        id = graphene.ID(required=True)

    @login_required
    @permission_required("track.can_delete_tracks")
    def mutate(self, info, id, **kwargs):
        try:
            Track.objects.get(pk=id).delete()
        except Track.DoesNotExist:
            raise GraphQLError("Track does not exist")

        return DeleteTrack(success=True)


class UpdateTrack(graphene.Mutation):
    track = graphene.Field(TrackType)

    class Arguments:
        token = graphene.String(required=False)
        id = graphene.ID(required=True)
        title = graphene.String(required=False)
        description = graphene.String(required=False)
        tags = graphene.List(TagType, required=False)
        attendees = graphene.List(AttendeeType, required=False)

    @login_required
    @permission_required("track.can_update_tracks")
    def mutate(self, info, id, tags=None, attendees=None, **kwargs):
        try:
            track = Track.objects.get(pk=id)

            if attendees:
                track.attendees = json.dumps(
                    [{"type": "attendee", "value": attendee} for attendee in attendees]
                )
            if tags:
                track.tags = json.dumps([{"type": "tag", "value": tag} for tag in tags])

            track.save()

            if kwargs.get("token"):
                kwargs.pop("token")

            Track.objects.filter(pk=id).update(**kwargs)
            # Refreshing objects from databse
            # Ref: https://docs.djangoproject.com/en/3.1/ref/models/instances/#refreshing-objects-from-database
            track.refresh_from_db()
        except Track.DoesNotExist:
            raise GraphQLError("Track does not exist")

        return UpdateTrack(track=track)


class Mutation(graphene.ObjectType):
    add_pac_member = AddPACMember.Field()
    delete_pac_member = DeletePACMember.Field()
    add_pac = AddPAC.Field()
    delete_pac = DeletePAC.Field()
    update_pac = UpdatePAC.Field()
    add_track = AddTrack.Field()
    delete_track = DeleteTrack.Field()
    update_track = UpdateTrack.Field()


# SPDX-License-Identifier: (EUPL-1.2)
# Copyright © 2019-2020 Simon Prast
