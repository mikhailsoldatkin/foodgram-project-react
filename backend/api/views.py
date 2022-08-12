from rest_framework import viewsets

from users.models import User
from .serializers import (
    IngredientSerializer, TagSerializer, RecipeSerializer, FavouriteSerializer,
    ShoppingCartSerializer
)
from recipes.models import (
    Ingredient, Tag, Recipe, ShoppingCart, IngredientInRecipe, Favourite
)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer


class FavouriteViewSet(viewsets.ModelViewSet):
    queryset = Favourite.objects.all()
    serializer_class = FavouriteSerializer


class ShoppingCartViewSet(viewsets.ModelViewSet):
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer
