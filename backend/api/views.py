from rest_framework.viewsets import ModelViewSet
from users.models import User

from .serializers import (
    IngredientSerializer, TagSerializer, RecipeSerializer, FavouriteSerializer,
    ShoppingCartSerializer
)
from recipes.models import (
    Ingredient, Tag, Recipe, ShoppingCart, IngredientInRecipe, Favourite
)


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer


class FavouriteViewSet(ModelViewSet):
    queryset = Favourite.objects.all()
    serializer_class = FavouriteSerializer


class ShoppingCartViewSet(ModelViewSet):
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer
