from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.viewsets import ModelViewSet

from recipes.models import (
    Ingredient, Tag, Recipe, Favourite, ShoppingCart, IngredientInRecipe
)
from users.serializers import RecipeShortSerializer
from .filters import RecipeFilter
from .pagination import CustomPagination
from .permissions import ReadOnly, IsAuthor
from .serializers import (
    IngredientSerializer, TagSerializer, RecipeSerializer
)


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminUser | ReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminUser | ReadOnly,)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (ReadOnly | IsAuthor,)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        user = request.user
        if request.method == 'POST':
            return self.add_to(Favourite, user, pk)
        elif request.method == 'DELETE':
            return self.delete_from(Favourite, user, pk)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        user = request.user
        if request.method == 'POST':
            return self.add_to(ShoppingCart, user, pk)
        elif request.method == 'DELETE':
            return self.delete_from(ShoppingCart, user, pk)

    def add_to(self, model, user, pk):
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response({'errors': 'Рецепт уже добавлен!'},
                            status=status.HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = RecipeShortSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_from(self, model, user, pk):
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Рецепт уже удален!'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        user = request.user

        if not user.shopping_cart.exists():
            return Response(status=HTTP_400_BAD_REQUEST)

        ingredients = IngredientInRecipe.objects.filter(
            recipe__shopping_cart__user=user).values_list(
            'ingredient__name', 'ingredient__measurement_unit', 'amount'
        )

        shopping_dict = {}

        for item in ingredients:
            name = item[0]
            if name not in shopping_dict:
                shopping_dict[name] = {
                    'measure': item[1],
                    'amount': item[2]
                }
            else:
                shopping_dict[name]['amount'] += item[2]

        filename = f'{user.username}_shopping_list.txt'
        today = datetime.today()

        shopping_list = (
            f'Список покупок для: {user.get_full_name()}\n\n'
            f'Дата: {today:%Y-%m-%d}\n\n'
        )
        for k, v in shopping_dict.items():
            shopping_list += f'- {k} ({v["measure"]}) - {v["amount"]}\n'

        shopping_list += f'\nFoodgram ({today:%Y})'

        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'

        return response
