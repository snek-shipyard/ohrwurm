import inspect

from django.conf import settings

import wagtail
import wagtail.documents.blocks
import wagtail.embeds.blocks
import wagtail.images.blocks
import wagtail.snippets.blocks
from wagtail.core import blocks
from wagtail.core.fields import StreamField

import graphene
from graphene.types import Scalar
from graphene_django.converter import convert_django_field

from ..registry import registry


class GenericStreamFieldInterface(Scalar):
    @staticmethod
    def serialize(stream_value):
        return stream_value.stream_data


@convert_django_field.register(StreamField)
def convert_stream_field(field, registry=None):
    return GenericStreamFieldInterface(
        description=field.help_text, required=not field.null
    )


class StreamFieldInterface(graphene.Interface):
    id = graphene.String()
    block_type = graphene.String(required=True)
    field = graphene.String(required=True)
    raw_value = graphene.String(required=True)

    @classmethod
    def resolve_type(cls, instance, info):
        """
        If block has a custom Graphene Node type in registry then use it,
        otherwise use generic block type.
        """
        if hasattr(instance, "block"):
            mdl = type(instance.block)
            if mdl in registry.streamfield_blocks:
                return registry.streamfield_blocks[mdl]

            for block_class in inspect.getmro(mdl):
                if block_class in registry.streamfield_blocks:
                    return registry.streamfield_blocks[block_class]

        return registry.streamfield_blocks["generic-block"]

    def resolve_id(self, info, **kwargs):
        return self.id

    def resolve_block_type(self, info, **kwargs):
        return type(self.block).__name__

    def resolve_field(self, info, **kwargs):
        return self.block.name

    def resolve_raw_value(self, info, **kwargs):
        import json

        if isinstance(self, dict):
            return json.dumps(serialize_struct_obj(self), sort_keys=True)

        if isinstance(self.value, dict):
            return json.dumps(serialize_struct_obj(self.value), sort_keys=True)

        return json.dumps(self.value, sort_keys=True)


def generate_streamfield_union(graphql_types):
    class StreamfieldUnion(graphene.Union):
        class Meta:
            """Can change over time."""

            types = graphql_types

        @classmethod
        def resolve_type(cls, instance, info):
            """
            If block has a custom Graphene Node type in registry then use it,
            otherwise use generic block type.
            """
            mdl = type(instance.block)
            if mdl in registry.streamfield_blocks:
                return registry.streamfield_blocks[mdl]

            return registry.streamfield_blocks["generic-block"]

    return StreamfieldUnion


class StructBlockItem:
    id = None
    block = None
    value = None

    def __init__(self, id, block, value=""):
        """
        Initialise StructBlock from a Streamfield.
        """
        self.id = id
        self.block = block
        self.value = value


def serialize_struct_obj(obj):
    rtn_obj = {}

    if hasattr(obj, "stream_data"):
        rtn_obj = []
        for field in obj.stream_data:
            rtn_obj.append(serialize_struct_obj(field["value"]))
    elif isinstance(obj, dict):
        for field in obj:
            value = obj[field]
            if hasattr(value, "stream_data"):
                rtn_obj[field] = list(
                    map(
                        lambda data: serialize_struct_obj(data["value"]),
                        value.stream_data,
                    )
                )
            elif hasattr(value, "value"):
                rtn_obj[field] = value.value
            elif hasattr(value, "src"):
                rtn_obj[field] = value.src
            elif hasattr(value, "file"):
                rtn_obj[field] = value.file.url
            elif isinstance(value, blocks.StructValue):
                rtn_obj[field] = dict(value)
            elif isinstance(value, list):
                rtn_obj[field] = [serialize_struct_obj(e) for e in value]
            else:
                rtn_obj[field] = value
    else:
        rtn_obj = obj

    return rtn_obj


class StructBlock(graphene.ObjectType):
    class Meta:
        """Can change over time."""

        interfaces = (StreamFieldInterface,)

    blocks = graphene.List(graphene.NonNull(StreamFieldInterface), required=True)

    def resolve_blocks(self, info, **kwargs):
        stream_blocks = []
        for name, value in self.value.items():
            block = self.block.child_blocks[name]
            if issubclass(type(block), wagtail.core.blocks.ChooserBlock) and hasattr(
                value, "id"
            ):
                value = block.to_python(value.id)
            elif not issubclass(type(block), blocks.StreamBlock):
                value = block.to_python(value)

            stream_blocks.append(StructBlockItem(name, block, value))
        return stream_blocks


class StreamBlock(StructBlock):
    class Meta:
        """Can change over time."""

        interfaces = (StreamFieldInterface,)

    def resolve_blocks(self, info, **kwargs):
        stream_blocks = []

        if issubclass(type(self.value), wagtail.core.blocks.stream_block.StreamValue):
            # self: StreamChild, block: StreamBlock, value: StreamValue
            stream_data = self.value.stream_data
            child_blocks = self.value.stream_block.child_blocks
        else:
            # This occurs when StreamBlock is child of StructBlock
            # self: StructBlockItem, block: StreamBlock, value: list
            stream_data = self.value
            child_blocks = self.block.child_blocks

        for field in stream_data:
            block = child_blocks[field["type"]]
            value = field["value"]
            if issubclass(
                type(block), wagtail.core.blocks.ChooserBlock
            ) or not issubclass(type(block), blocks.StructBlock):
                value = block.to_python(value)

            stream_blocks.append(StructBlockItem(field["type"], block, value))

        return stream_blocks


class StreamFieldBlock(graphene.ObjectType):
    value = graphene.String(required=True)

    class Meta:
        """Can change over time."""

        interfaces = (StreamFieldInterface,)


class CharBlock(graphene.ObjectType):
    value = graphene.String(required=True)

    class Meta:
        """Can change over time."""

        interfaces = (StreamFieldInterface,)


class TextBlock(graphene.ObjectType):
    value = graphene.String(required=True)

    class Meta:
        """Can change over time."""

        interfaces = (StreamFieldInterface,)


class EmailBlock(graphene.ObjectType):
    value = graphene.String(required=True)

    class Meta:
        """Can change over time."""

        interfaces = (StreamFieldInterface,)


class IntegerBlock(graphene.ObjectType):
    value = graphene.Int(required=True)

    class Meta:
        """Can change over time."""

        interfaces = (StreamFieldInterface,)


class FloatBlock(graphene.ObjectType):
    value = graphene.Float(required=True)

    class Meta:
        """Can change over time."""

        interfaces = (StreamFieldInterface,)


class DecimalBlock(graphene.ObjectType):
    value = graphene.Float(required=True)

    class Meta:
        """Can change over time."""

        interfaces = (StreamFieldInterface,)


class RegexBlock(graphene.ObjectType):
    value = graphene.String(required=True)

    class Meta:
        """Can change over time."""

        interfaces = (StreamFieldInterface,)


class URLBlock(graphene.ObjectType):
    value = graphene.String(required=True)

    class Meta:
        """Can change over time."""

        interfaces = (StreamFieldInterface,)


class BooleanBlock(graphene.ObjectType):
    value = graphene.Boolean(required=True)

    class Meta:
        """Can change over time."""

        interfaces = (StreamFieldInterface,)


class DateBlock(graphene.ObjectType):
    value = graphene.String(format=graphene.String(), required=True)

    class Meta:
        """Can change over time."""

        interfaces = (StreamFieldInterface,)

    def resolve_value(self, info, **kwargs):
        format = kwargs.get("format")
        if format:
            return self.value.strftime(format)
        return self.value


class DateTimeBlock(DateBlock):
    class Meta:
        """Can change over time."""

        interfaces = (StreamFieldInterface,)


class TimeBlock(DateBlock):
    class Meta:
        """Can change over time."""

        interfaces = (StreamFieldInterface,)


class RichTextBlock(graphene.ObjectType):
    value = graphene.String(required=True)

    class Meta:
        """Can change over time."""

        interfaces = (StreamFieldInterface,)


class RawHTMLBlock(graphene.ObjectType):
    value = graphene.String(required=True)

    class Meta:
        """Can change over time."""

        interfaces = (StreamFieldInterface,)


class BlockQuoteBlock(graphene.ObjectType):
    value = graphene.String(required=True)

    class Meta:
        """Can change over time."""

        interfaces = (StreamFieldInterface,)


class ChoiceOption(graphene.ObjectType):
    key = graphene.String(required=True)
    value = graphene.String(required=True)


class ChoiceBlock(graphene.ObjectType):
    value = graphene.String(required=True)
    choices = graphene.List(graphene.NonNull(ChoiceOption), required=True)

    class Meta:
        """Can change over time."""

        interfaces = (StreamFieldInterface,)

    def resolve_choices(self, info, **kwargs):
        choices = []
        for key, value in self.block._constructor_kwargs["choices"]:
            choice = ChoiceOption(key, value)
            choices.append(choice)
        return choices


def get_media_url(url):
    if url[0] == "/":
        return settings.BASE_URL + url
    return url


class EmbedBlock(graphene.ObjectType):
    value = graphene.String(required=True)
    url = graphene.String(required=True)

    class Meta:
        """Can change over time."""

        interfaces = (StreamFieldInterface,)

    def resolve_url(self, info, **kwargs):
        if hasattr(self, "value"):
            return get_media_url(self.value.url)
        return get_media_url(self.url)


class StaticBlock(graphene.ObjectType):
    value = graphene.String(required=True)

    class Meta:
        """Can change over time."""

        interfaces = (StreamFieldInterface,)


class ListBlock(graphene.ObjectType):
    items = graphene.List(graphene.NonNull(StreamFieldInterface), required=True)

    class Meta:
        """Can change over time."""

        interfaces = (StreamFieldInterface,)

    def resolve_items(self, info, **kwargs):
        # Get the nested StreamBlock type
        block_type = self.block.child_block
        # Return a list of GraphQL types from the list of valuess
        return [StructBlockItem(self.id, block_type, item) for item in self.value]


registry.streamfield_blocks.update(
    {
        "generic-block": StreamFieldBlock,
        blocks.CharBlock: CharBlock,
        blocks.TextBlock: TextBlock,
        blocks.EmailBlock: EmailBlock,
        blocks.IntegerBlock: IntegerBlock,
        blocks.FloatBlock: FloatBlock,
        blocks.DecimalBlock: DecimalBlock,
        blocks.RegexBlock: RegexBlock,
        blocks.URLBlock: URLBlock,
        blocks.BooleanBlock: BooleanBlock,
        blocks.DateBlock: DateBlock,
        blocks.TimeBlock: TimeBlock,
        blocks.DateTimeBlock: DateTimeBlock,
        blocks.RichTextBlock: RichTextBlock,
        blocks.RawHTMLBlock: RawHTMLBlock,
        blocks.BlockQuoteBlock: BlockQuoteBlock,
        blocks.ChoiceBlock: ChoiceBlock,
        blocks.StreamBlock: StreamBlock,
        blocks.StructBlock: StructBlock,
        blocks.StaticBlock: StaticBlock,
        blocks.ListBlock: ListBlock,
        wagtail.embeds.blocks.EmbedBlock: EmbedBlock,
    }
)


def register_streamfield_blocks():
    from .pages import PageInterface
    from .documents import get_document_type
    from .images import get_image_type

    class PageChooserBlock(graphene.ObjectType):
        page = graphene.Field(PageInterface, required=True)

        class Meta:
            """Can change over time."""

            interfaces = (StreamFieldInterface,)

        def resolve_page(self, info, **kwargs):
            return self.value

    class DocumentChooserBlock(graphene.ObjectType):
        document = graphene.Field(get_document_type(), required=True)

        class Meta:
            """Can change over time."""

            interfaces = (StreamFieldInterface,)

        def resolve_document(self, info, **kwargs):
            return self.value

    class ImageChooserBlock(graphene.ObjectType):
        image = graphene.Field(get_image_type(), required=True)

        class Meta:
            """Can change over time."""

            interfaces = (StreamFieldInterface,)

        def resolve_image(self, info, **kwargs):
            return self.value

    class SnippetChooserBlock(graphene.ObjectType):
        snippet = graphene.String(required=True)

        class Meta:
            """Can change over time."""

            interfaces = (StreamFieldInterface,)

        def resolve_snippet(self, info, **kwargs):
            return self.value

    registry.streamfield_blocks.update(
        {
            blocks.PageChooserBlock: PageChooserBlock,
            wagtail.documents.blocks.DocumentChooserBlock: DocumentChooserBlock,
            wagtail.images.blocks.ImageChooserBlock: ImageChooserBlock,
            wagtail.snippets.blocks.SnippetChooserBlock: SnippetChooserBlock,
        }
    )
