from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint

from recipes.validate import user_directory_path, validate_image

User = get_user_model()


class Ingredient(models.Model):
    title = models.CharField(
        max_length=256,
        verbose_name='Ингредиент'
    )
    dimension = models.CharField(
        max_length=128,
        verbose_name='Единица измерения'
    )

    class Meta:
        ordering = ('title',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.title}, {self.dimension}'


class Tag(models.Model):
    ORANGE = 'tags__checkbox_style_orange'
    GREEN = 'tags__checkbox_style_green'
    PURPLE = 'tags__checkbox_style_purple'
    TAG_COLOR = (
        (ORANGE, 'Оранжевый',),
        (GREEN, 'Зеленый'),
        (PURPLE, 'Фиолетовый'),
    )
    title = models.CharField(
        max_length=50,
        null=True,
        verbose_name='Название'
    )
    color = models.CharField(
        max_length=50,
        choices=TAG_COLOR,
        verbose_name='Цвет'
    )

    class Meta:
        ordering = ('title',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.title


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='автор рецепта',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='тег'
    )
    title = models.CharField(
        max_length=256,
        blank=False,
        verbose_name='название рецепта'
    )
    image = models.ImageField(
        upload_to=user_directory_path,
        validators=[validate_image],
        verbose_name='изображение',
        blank=True,
        null=True,
        default='default.jpg',
    )
    description = models.TextField(
        blank=False,
        verbose_name='описание рецепта'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='время приготовления'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        through='IngredientAmount',
        verbose_name='ингредиент',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='дата публикации'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.title


class IngredientAmount(models.Model):
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, verbose_name='ингредиент',
        blank=False,
        related_name='recipes_amounts',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients_amounts',
        blank=False,
        verbose_name='рецепт',
    )
    amount = models.IntegerField(
        blank=False,
        verbose_name='количество',
        validators=[MinValueValidator(1)]
    )

    class Meta:
        ordering = ('-recipe__pub_date',)
        verbose_name = 'Кол-во ингредиента'
        verbose_name_plural = 'Кол-во ингредиентов'

    def __str__(self):
        ingredient = self.ingredient.title
        amount = self.amount
        dimension = self.ingredient.dimension
        recipe = self.recipe
        return (f'{ingredient}: {amount}{dimension} - рецепт #{recipe.id}'
                f' {recipe.title}')


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_recipes',
        verbose_name='пользватель'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='at_favorites',
        verbose_name='рецепт'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='дата добавления'
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_favorite_recipe',
            ),
        ]
        ordering = ('-recipe__pub_date',)
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self):
        user_username = self.user.username
        recipe = self.recipe.title
        return f'{user_username} добавил в избранное {recipe}'


class ShoppingList(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='users_shopping_lists',
        verbose_name='пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='at_shopping_lists',
        verbose_name='рецепт'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='дата добавления'
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_shopping_recipe',
            ),
        ]
        ordering = ('-pub_date',)
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        user_username = self.user.username
        recipe = self.recipe.title
        return f'{user_username} добавил в список покупок {recipe}'


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='пользователь'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='автор'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата добавления'
    )

    class Meta:
        ordering = ('-pub_date',)
        constraints = [
            UniqueConstraint(
                fields=['user', 'author'],
                name='unique_following',
            ),
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        user_username = self.user.username
        author_username = self.author.username
        return f'{user_username} подписался на {author_username}'
