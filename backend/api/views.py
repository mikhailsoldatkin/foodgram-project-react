from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ModelViewSet

from recipes.models import (
    Ingredient, Tag, Recipe
)
from .filters import RecipeFilter
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

    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
