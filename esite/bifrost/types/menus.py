# python
from typing import List

# graphene_django
import graphene
from graphene_django import DjangoObjectType

# graphql
from graphql import ResolveInfo

# wagtailmenus
from wagtailmenus.models import FlatMenu, FlatMenuItem, MainMenu, MainMenuItem


class MenuItem(DjangoObjectType):
    class Meta:
        """Can change over time."""

        model = MainMenuItem


class Menu(DjangoObjectType):
    class Meta:
        """Can change over time."""

        model = MainMenu
        only_fields = ["max_levels", "menu_items"]


class SecondaryMenuItem(DjangoObjectType):
    class Meta:
        """Can change over time."""

        model = FlatMenuItem


class SecondaryMenu(DjangoObjectType):
    class Meta:
        """Can change over time."""

        model = FlatMenu
        only_fields = ["title", "handle", "heading", "max_levels", "menu_items"]


def MenusQueryMixin():
    class Mixin:
        main_menu = graphene.List(Menu)
        secondary_menu = graphene.Field(
            SecondaryMenu, handle=graphene.String(required=True)
        )
        secondary_menus = graphene.List(SecondaryMenu)

        def resolve_main_menu(self, _info: ResolveInfo) -> List[MainMenu]:
            return MainMenu.objects.all()

        def resolve_secondary_menus(self, _info: ResolveInfo) -> List[FlatMenu]:
            return FlatMenu.objects.all()

        def resolve_secondary_menu(self, _info, handle: ResolveInfo) -> FlatMenu:
            return FlatMenu.objects.filter(handle=handle).first()

    return Mixin
