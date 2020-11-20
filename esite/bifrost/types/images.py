from django.conf import settings

from wagtail.images import get_image_model
from wagtail.images.models import Image as WagtailImage
from wagtail.images.models import Rendition as WagtailImageRendition

import graphene
from graphene_django import DjangoObjectType

# graphql_jwt
from graphql_jwt.decorators import login_required

from ..registry import registry
from ..utils import resolve_queryset
from .structures import QuerySetList


def get_image_url(cls):
    url = ""
    if hasattr(cls, "url"):
        url = cls.url
    else:
        url = cls.file.url

    if url[0] == "/":
        return settings.BASE_URL + url
    return url


class BaseImageObjectType(graphene.ObjectType):
    width = graphene.Int(required=True)
    height = graphene.Int(required=True)
    src = graphene.String(required=True)
    aspect_ratio = graphene.Float(required=True)
    sizes = graphene.String(required=True)

    def resolve_src(self, info):
        """
        Get url of the original uploaded image.
        """
        return get_image_url(self)

    def resolve_aspect_ratio(self, info, **kwargs):
        """
        Calculate aspect ratio for the image.
        """
        return self.width / self.height

    def resolve_sizes(self, info):
        return "(max-width: {}px) 100vw, {}px".format(self.width, self.width)


class ImageRenditionObjectType(DjangoObjectType, BaseImageObjectType):
    id = graphene.ID(required=True)
    url = graphene.String(required=True)

    class Meta:
        """Can change over time."""

        model = WagtailImageRendition

    @login_required
    def resolve_image(self, info, **kwargs):
        return self.image


def get_rendition_type():
    rendition_mdl = get_image_model().renditions.rel.related_model
    rendition_type = registry.images.get(rendition_mdl, ImageRenditionObjectType)
    return rendition_type


class ImageObjectType(DjangoObjectType, BaseImageObjectType):
    rendition = graphene.Field(
        lambda: get_rendition_type(),
        max=graphene.String(),
        min=graphene.String(),
        width=graphene.Int(),
        height=graphene.Int(),
        fill=graphene.String(),
        format=graphene.String(),
        bgcolor=graphene.String(),
        jpegquality=graphene.Int(),
    )
    src_set = graphene.String(sizes=graphene.List(graphene.Int))

    class Meta:
        """Can change over time."""

        model = WagtailImage
        exclude_fields = ("tags",)

    def resolve_rendition(self, info, **kwargs):
        """
        Render a custom rendition of the current image.
        """
        try:
            filters = "|".join([f"{key}-{val}" for key, val in kwargs.items()])
            img = self.get_rendition(filters)
            rendition_type = get_rendition_type()

            return rendition_type(
                id=img.id,
                url=img.url,
                width=img.width,
                height=img.height,
                file=img.file,
                image=self,
            )
        except:
            return None

    def resolve_src_set(self, info, sizes, **kwargs):
        """
        Generate src set of renditions.
        """
        try:
            if self.file.name is not None:
                rendition_list = [
                    ImageObjectType.resolve_rendition(self, info, width=width)
                    for width in sizes
                ]

                return ", ".join(
                    [f"{get_image_url(img)} {img.width}w" for img in rendition_list]
                )
        except:
            pass

        return ""


def get_image_type():
    mdl = get_image_model()
    return registry.images.get(mdl, ImageObjectType)


def ImagesQuery():
    mdl = get_image_model()
    mdl_type = get_image_type()

    class Mixin:
        images = QuerySetList(
            graphene.NonNull(mdl_type),
            token=graphene.String(),
            enable_search=True,
            required=True,
        )
        image_type = graphene.String(required=True)

        # Return all pages, ideally specific.
        @login_required
        def resolve_images(self, info, **kwargs):
            return resolve_queryset(mdl.objects.all(), info, **kwargs)

        # Give name of the image type, used to generate mixins
        def resolve_image_type(self, info, **kwargs):
            return get_image_type()

    return Mixin
