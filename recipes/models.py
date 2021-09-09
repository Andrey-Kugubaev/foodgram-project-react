from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint

from recipes.validate import user_directory_path, validate_image

User = get_user_model()


class Ingredient(models.Model):
    title = models.CharField(max_length=256)
    dimension = models.CharField(max_length=128)

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
    title = models.CharField('Название', max_length=50, null=True)
    color = models.CharField('Цвет', max_length=50, choices=TAG_COLOR)

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
    tags = models.ManyToManyField(Tag, related_name='recipes')
    title = models.CharField('название рецепта', max_length=256, blank=False)
    image = models.ImageField(
        upload_to=user_directory_path,
        validators=[validate_image],
        verbose_name='изображение',
        blank=True,
        null=True,
        default='default.jpg',
    )
    description = models.TextField('описание рецепта', blank=False)
    cooking_time = models.PositiveSmallIntegerField('время приготовления')
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        through='IngredientAmount',
        verbose_name='ингредиент',
    )
    pub_date = models.DateTimeField(
        'дата публикации', auto_now_add=True, db_index=True
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
        related_name='recipes_amount',
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='ingredients_amount',
        blank=False,
        verbose_name='рецепт',
    )
    amount = models.IntegerField(
        'количество',
        blank=False,
        validators=[
            MinValueValidator(1)
        ]
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
        related_name='favorite_recipes'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='at_favorites'
    )
    pub_date = models.DateTimeField(
        'дата добавления', auto_now_add=True, db_index=True
    )

    class Meta:
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
        related_name='users_shopping_lists'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='at_shopping_lists'
    )
    pub_date = models.DateTimeField(
        'дата добавления', auto_now_add=True, db_index=True
    )

    class Meta:
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
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )
    pub_date = models.DateTimeField('дата добавления', auto_now_add=True)

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
