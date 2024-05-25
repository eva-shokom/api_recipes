from django.contrib import admin

from .models import (
    Favorite, Ingredient, Recipe, RecipeIngredient, ShoppingCart, Tag
)
from foodgram.constants import MIN_AMOUNT


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    min_num = MIN_AMOUNT


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_display_links = ('name',)
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    list_display_links = ('id', 'name', 'slug')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientInline,)
    list_display = ('author', 'name',)
    list_display_links = ('name', 'author')
    search_fields = ('name', 'author__username')
    filter_horizontal = ('tags',)
    list_filter = ('tags',)
    list_display_links = ('author', 'name')
    readonly_fields = ('favorite_count',)
    fieldsets = (
        (
            None,
            {
                'fields': (
                    'author',
                    ('name', 'cooking_time', 'favorite_count'),
                    'text',
                    'image',
                    'tags',
                )
            },
        ),
    )

    @admin.display(description='Общее число добавлений рецепта в избранное.')
    def favorite_count(self, recipe):
        """Количество рецепта в избранном."""
        return recipe.favorites.count()


@admin.register(Favorite, ShoppingCart)
class AuthorRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', '__str__')
    list_display_links = ('id', '__str__')
