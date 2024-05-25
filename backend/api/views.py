from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse

from .filters import IngredientFilter, RecipeFilter
from .pagination import CustomPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    AvatarSerializer, CustomUserSerializer, FavoriteSerializer,
    IngredientSerializer, LinkSerializers, RecipeReadSerializer,
    RecipeWriteSerializer, ShoppingCartSerializer, SubscribeReadSerializer,
    SubscribeWriteSerializer, TagSerializer
)
from recipes.models import (
    Favorite, Ingredient, Recipe, RecipeIngredient, ShoppingCart, Subscribe,
    Tag
)


User = get_user_model()


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAny]
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action == 'me':
            return CustomUserSerializer
        return super().get_serializer_class()

    @action(
        methods=['get'],
        detail=False,
        permission_classes=[IsAuthenticated],
        url_name='me',
    )
    def me(self, request, *args, **kwargs):
        """Метод для данных о себе."""
        return super().me(request, *args, **kwargs)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, **kwargs):
        """Метод для подписки на автора и отписки от него."""
        author_id = self.kwargs.get('id')
        author = get_object_or_404(User, id=author_id)
        serializer = SubscribeWriteSerializer(
            data={'author': author.id, 'user': request.user.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, **kwargs):
        deleted_subscriptions_count, _ = Subscribe.objects.filter(
            user=request.user, author=self.get_object()
        ).delete()
        if not deleted_subscriptions_count:
            return Response(
                {"errors": "Вы не были подписаны на этого пользователя"},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        """Метод для просмотра своих подписок."""
        user = request.user
        queryset = User.objects.filter(subscribing__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeReadSerializer(
            pages, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(
        detail=False,
        methods=['put'],
        permission_classes=[IsAuthenticated],
        url_path='me/avatar'
    )
    def avatar(self, request, **kwargs):
        """Метод для удаления и изменения аватара пользователя."""
        user = self.request.user
        serializer = AvatarSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data, status=status.HTTP_200_OK)

    @avatar.mapping.delete
    def delete_avatar(self, request, **kwargs):
        User.objects.filter(id=self.request.user.id).update(avatar=None)
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthorOrReadOnly, AllowAny]
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        elif self.action == 'favorite':
            return FavoriteSerializer
        elif self.action == 'shopping_cart':
            return ShoppingCartSerializer
        return RecipeWriteSerializer

    def add_to(self, model, user, pk):
        """Метод для добавления рецепта в избранное или в список покупок."""
        serializer = self.get_serializer(data={'recipe': pk})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_from(self, model, user, pk, error_message=''):
        """Метод для удаления рецепта из избранного или из списка покупок."""
        recipe = get_object_or_404(Recipe, id=pk)
        deleted_model_count, _ = model.objects.filter(
            user=user, recipe=recipe
        ).delete()
        if not deleted_model_count:
            return Response(
                {
                    'errors': (
                        f'Данного рецепта нет в списке {error_message}!'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, **kwargs):
        """Метод для добавления рецепта в избранное и удаления из него."""
        return self.add_to(
            model=Favorite, user=request.user, pk=self.kwargs.get('pk'))

    @favorite.mapping.delete
    def delete_favorite(self, request, **kwargs):
        return self.delete_from(
            model=Favorite,
            user=request.user,
            pk=self.kwargs.get('pk'),
            error_message='избранных рецептов')

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, **kwargs):
        """Метод для добавления рецепта в список покупок и удаления из него."""
        return self.add_to(
            model=ShoppingCart, user=request.user, pk=self.kwargs.get('pk'))

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, **kwargs):
        return self.delete_from(
            model=ShoppingCart,
            user=request.user,
            pk=self.kwargs.get('pk'),
            error_message='покупок')

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        """Метод для скачивания списка покупок."""
        user = request.user
        if not user.shopping_cart.exists():
            return Response(
                {'errors': 'Список покупок пуст'},
                status=status.HTTP_400_BAD_REQUEST
            )
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        shopping_list = []
        for ingredient in ingredients:
            shopping_list.append(
                (
                    f'- {ingredient["ingredient__name"]} '
                    f'({ingredient["ingredient__measurement_unit"]}) '
                    f'- {ingredient["amount"]}'
                )
            )
        response = HttpResponse(
            '\n'.join(shopping_list), content_type='text.txt'
        )
        response['Content-Disposition'] = (
            'attachment; filename=shopping_list.txt')
        return response

    @action(
        detail=True,
        methods=['get'],
        permission_classes=[AllowAny],
        url_path='get-link',
        url_name='get-link'
    )
    def get_link(self, request, **kwargs):
        """Метод для получения короткой ссылки на рецепт."""
        full_url = request.META.get('HTTP_REFERER')
        recipe_id = kwargs.get('pk')
        if full_url is None:
            url = reverse('api:recipe-detail', kwargs={'pk': recipe_id})
            full_url = request.build_absolute_uri(url)
        serializer = LinkSerializers(
            data={'full_url': full_url}, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
