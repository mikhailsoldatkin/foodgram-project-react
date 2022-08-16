from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import (
    SerializerMethodField, ReadOnlyField, CurrentUserDefault
)

from recipes.models import Ingredient, Tag, Recipe, IngredientInRecipe
from users.serializers import CustomUserSerializer


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = ReadOnlyField(source='ingredient.id')
    name = ReadOnlyField(source='ingredient.name')
    measurement_unit = ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = IngredientInRecipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(read_only=True, many=True)
    author = CustomUserSerializer(read_only=True,
                                  default=CurrentUserDefault())
    ingredients = IngredientInRecipeSerializer(
        source='ingredientinrecipe_set',
        many=True,
        read_only=True,
    )

    image = Base64ImageField()

    is_favorited = SerializerMethodField(read_only=True)
    is_in_shopping_cart = SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.favorites.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.shopping_cart.filter(recipe=obj).exists()

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise ValidationError({
                'ingredients': 'Нужен хотя бы один ингредиент!'
            })
        ingredient_list = []
        for item in ingredients:
            ingredient = get_object_or_404(Ingredient, id=item['id'])
            if ingredient in ingredient_list:
                raise ValidationError({
                    'ingredients': 'Ингридиенты не могут повторяться!'
                })

            if int(item['amount']) <= 0:
                raise ValidationError({
                    'amount': 'Количество ингредиента должно быть больше 0!'
                })

            ingredient_list.append(ingredient)

        tags = self.initial_data.get('tags')
        if not tags:
            raise ValidationError({
                'tags': 'Нужно выбрать хотя бы один тег!'
            })
        tags_list = []
        for tag in tags:
            if tag in tags_list:
                raise ValidationError({
                    'tags': 'Теги должны быть уникальными!'
                })

            tags_list.append(tag)

        data['ingredients'] = ingredients
        data['tags'] = tags

        return data

    def create_ingredients_amounts(self, recipe, ingredients):
        IngredientInRecipe.objects.bulk_create(
            [IngredientInRecipe(
                ingredient=Ingredient.objects.get(id=ingredient.get('id')),
                recipe=recipe,
                amount=ingredient.get('amount')
            ) for ingredient in ingredients]
        )

    def create(self, validated_data):
        author = self.context.get('request').user
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=author,
                                       **validated_data)
        recipe.tags.set(tags)
        self.create_ingredients_amounts(recipe=recipe,
                                        ingredients=ingredients)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        instance = super().update(instance, validated_data)

        instance.tags.clear()
        instance.tags.set(tags)

        instance.ingredients.clear()
        self.create_ingredients_amounts(recipe=instance,
                                        ingredients=ingredients)
        instance.save()
        return instance
