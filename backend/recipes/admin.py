from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Favorite, Ingredient, Recipe, RecipeIngredient, RecipeTag, ShoppingCart,
    Tag
)


@admin.display(description='Общее число добавлений рецепта в избранное.')
def favorite_count(self, recipe):
    return recipe.favorites.count()


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


class RecipeTagInline(admin.TabularInline):
    model = RecipeTag
    extra = 1


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientInline,)
    list_display = ('name', 'measurement_unit')
    list_display_links = ('name',)
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    inlines = (RecipeTagInline,)
    list_display = ('id', 'name', 'slug')
    list_display_links = ('id', 'name', 'slug')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientInline, RecipeTagInline)
    list_display = ('author', 'name',)
    list_display_links = ('name', 'author')
    search_fields = ('name', 'author__username')
    list_filter = ('tags',)
    list_display_links = ('author', 'name')
    readonly_fields = ('in_favorites',)
    fieldsets = (
        (
            None,
            {
                'fields': (
                    'author',
                    ('name', 'cooking_time', 'in_favorites'),
                    'text',
                    'image',
                )
            },
        ),
    )

    @admin.display(
        description=format_html('<strong>Рецептов в избранных</strong>')
    )
    def in_favorites(self, obj):
        """Количество рецепта в избранном."""
        return Favorite.objects.filter(recipe=obj).count()


@admin.register(Favorite, ShoppingCart)
class AuthorRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', '__str__')
    list_display_links = ('id', '__str__')
