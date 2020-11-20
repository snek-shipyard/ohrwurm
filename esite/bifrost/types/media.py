from django.conf import settings

from graphene_django import DjangoObjectType

# graphql_jwt
from graphql_jwt.decorators import login_required
from wagtailmedia.models import Media


class MediaObjectType(DjangoObjectType):
    class Meta:
        """Can change over time."""

        model = Media
        exclude_fields = ("tags",)

    @login_required
    def resolve_file(self, info, **kwargs):
        if self.file.url[0] == "/":
            return settings.BASE_URL + self.file.url
        return self.file.url
