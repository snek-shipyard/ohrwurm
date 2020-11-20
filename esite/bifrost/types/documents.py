from wagtail.documents import get_document_model
from wagtail.documents.models import Document as WagtailDocument

import graphene
from graphene_django.types import DjangoObjectType

# graphql_jwt
from graphql_jwt.decorators import login_required

from ..registry import registry
from ..utils import resolve_queryset
from .structures import QuerySetList


class DocumentObjectType(DjangoObjectType):
    """
    Base document type used if one isn't generated for the current model.
    All other node types extend this.
    """

    class Meta:
        """Can change over time."""

        model = WagtailDocument
        exclude_fields = ("tags",)

    id = graphene.ID(required=True)
    title = graphene.String(required=True)
    file = graphene.String(required=True)
    created_at = graphene.DateTime(required=True)
    file_size = graphene.Int()
    file_hash = graphene.String()


def DocumentsQuery():
    registry.documents[WagtailDocument] = DocumentObjectType
    mdl = get_document_model()
    model_type = registry.documents[mdl]

    class Mixin:
        documents = QuerySetList(
            graphene.NonNull(model_type),
            token=graphene.String(),
            enable_search=True,
            required=True,
        )

        # Return all pages, ideally specific.
        @login_required
        def resolve_documents(self, info, **kwargs):
            return resolve_queryset(mdl.objects.all(), info, **kwargs)

    return Mixin


def get_document_type():
    registry.documents[WagtailDocument] = DocumentObjectType
    mdl = get_document_model()
    return registry.documents[mdl]
