from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.reverse import reverse

from link_shortner.models import Link
from recipes.models import (
    Favorite, Ingredient, Recipe, RecipeIngredient, ShoppingCart, Subscribe,
    Tag
)


User = get_user_model()


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для аватара пользователя."""

    avatar = Base64ImageField(allow_null=True)

    class Meta:
        model = User
        fields = ('avatar',)


class CustomUserSerializer(UserSerializer):
    """Сериализатор для пользователя."""

    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'avatar'
        )

    def get_is_subscribed(self, author):
        user = self.context.get('request').user
        return (
            self.context.get('request')
            and user.is_authenticated
            and Subscribe.objects.filter(user=user, author=author).exists()
        )


class SubscribeReadSerializer(CustomUserSerializer):
    """Сериализатор для отображения подписок пользователя."""

    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + (
            'recipes_count', 'recipes'
        )

    def get_recipes(self, author):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = author.recipes.all()
        if limit:
            try:
                recipes = recipes[:int(limit)]
            except TypeError:
                pass
        serializer = RecipeShortSerializer(recipes, many=True, read_only=True)
        return serializer.data

    def get_recipes_count(self, author):
        return author.recipes.count()


class SubscribeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для сохранения подписок пользователя."""

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    author = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
    )

    class Meta:
        model = Subscribe
        fields = ('user', 'author')

    def validate(self, data):
        author = data.get('author')
        user = self.context.get('request').user
        if Subscribe.objects.filter(author=author, user=user).exists():
            raise ValidationError(
                detail='Вы уже подписаны на этого пользователя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        if user == author:
            raise ValidationError(
                detail='Нельзя подписаться на самого себя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        return data

    def to_representation(self, instance):
        return SubscribeReadSerializer(
            instance.author, context=self.context).data


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тэгов."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для записи ингредиентов в рецепте."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source='ingredient')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения ингредиентов в рецепте."""

    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit')
    id = serializers.IntegerField(source='ingredient.id')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для записи рецептов."""

    ingredients = RecipeIngredientWriteSerializer(
        many=True, allow_empty=False)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(), allow_empty=False)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'name', 'image', 'text', 'cooking_time'
        )
        read_only_fields = ('author',)

    def validate_image(self, image):
        if image is None:
            raise serializers.ValidationError(
                {'error': 'Добавьте изображение рецепта!'}
            )
        return image

    def validate(self, attrs):
        tags = attrs.get('tags', [])
        if len(tags) == 0:
            raise ValidationError(
                {'tags': 'Нужно выбрать хотя бы один тэг'}
            )
        if len(set(tags)) != len(tags):
            raise ValidationError(
                {'tags': 'Теги не должны повторяться!'}
            )
        ingredients = attrs.get('ingredients', [])
        if len(ingredients) == 0:
            raise ValidationError(
                {'ingredients': 'Добавьте хотя бы один ингредиент'}
            )
        ingredients_set = {
            ingredient['ingredient'] for ingredient in ingredients
        }
        if len(ingredients) != len(ingredients_set):
            raise ValidationError(
                {'ingredients': 'Ингридиенты не должны повторяться!'}
            )
        return attrs

    @staticmethod
    def create_ingredients(recipe, ingredients):
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount'],
            )
            for ingredient in ingredients
        )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=self.context.get('request').user,
            **validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe=recipe, ingredients=ingredients)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        instance.ingredients.clear()
        self.create_ingredients(recipe=instance, ingredients=ingredients)
        tags = validated_data.pop('tags')
        instance.tags.clear()
        instance.tags.set(tags)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецептов."""

    ingredients = RecipeIngredientReadSerializer(
        many=True, source='recipeingredient_set')
    tags = TagSerializer(read_only=True, many=True)
    author = CustomUserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',
        )

    def get_is_favorited(self, recipe):
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and user.favorite.filter(recipe=recipe).exists()
        )

    def get_is_in_shopping_cart(self, recipe):
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and user.shopping_cart.filter(recipe=recipe).exists()
        )


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения короткой записи рецептов."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class LinkSerializers(serializers.ModelSerializer):
    """Сериализатор для короткой ссылки."""

    class Meta:
        model = Link
        fields = ('full_url',)
        write_only_fiels = ('full_url',)

    def create(self, validated_data):
        instance, _ = Link.objects.get_or_create(**validated_data)
        return instance

    def get_short_url(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(
            reverse('link_shortner:redirection', args=[obj.short_url])
        )

    def to_representation(self, instance):
        return {'short-link': self.get_short_url(instance)}


class UserRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для наследования избранных рецептов и списка покупок."""

    error_message = None

    class Meta:
        model = None
        fields = ('user', 'recipe')
        read_only_fields = ('user',)

    def validate(self, attrs):
        recipe = attrs['recipe']
        user = self.context.get('request').user
        if self.Meta.model.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                {'error': f'Рецепт уже добавлен в {self.error_message}!'}
            )
        return attrs

    def to_representation(self, instance):
        return RecipeShortSerializer(
            instance.recipe, context=self.context
        ).data


class FavoriteSerializer(UserRecipeSerializer):
    """Сериализатор для избранных рецептов."""

    error_message = 'избранное'

    class Meta(UserRecipeSerializer.Meta):
        model = Favorite


class ShoppingCartSerializer(UserRecipeSerializer):
    """Сериализатор для списка покупок."""

    error_message = 'список покупок'

    class Meta(UserRecipeSerializer.Meta):
        model = ShoppingCart
