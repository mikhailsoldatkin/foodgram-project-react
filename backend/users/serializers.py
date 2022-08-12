from djoser.serializers import UserSerializer, UserCreateSerializer
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField

from .models import Subscribe, User


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
            'username',
            'password'
        )
        # extra_kwargs = {
        #     'email': {'required': True},
        #     'username': {'required': True},
        #     'password': {'required': True},
        #     'first_name': {'required': True},
        #     'last_name': {'required': True},
        # }


class CustomUserSerializer(UserSerializer):
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscribe.objects.filter(user=user, author=obj).exists()


class SubscribeSerializer(CustomUserSerializer):
    # recipes_count = SerializerMethodField()
    # recipes = RecipeSerializer(many=True)

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields
        read_only_fields = ('email', 'username')

    def validate(self, data):
        author = self.instance  # seconduser
        user = self.context.get('request').user  # admin

        if Subscribe.objects.filter(author=author, user=user).exists():
            raise ValidationError(
                detail='Вы уже подписаны на этого пользователя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        if user == author:
            raise ValidationError(
                detail='Вы не можете подписаться на самого себя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        return data

    # def get_recipes_count(self, obj):
    #     print(self)
    #     return obj.recipes.count()

    # def get_recipes(self, obj):
    #     request = self.context.get('request')
    #     limit = request.GET.get('recipes_limit')
    #     recipes = Recipe.objects.filter(author=obj.author)
    #     if limit:
    #         recipes = recipes[:int(limit)]
    #     return RecipeSerializer(recipes, many=True).data
