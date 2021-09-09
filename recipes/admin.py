from django.contrib import admin

from recipes.models import (FavoriteRecipe, Follow, Ingredient,
                            IngredientAmount, Recipe, ShoppingList, Tag)


class IngredientAmountInline(admin.TabularInline):
    model = IngredientAmount
    extra = 3


class RecipeAdmin(admin.ModelAdmin):
    inlines = (IngredientAmountInline,)
    list_display = ('title', 'author', 'count_favorites',)
    list_filter = ('title', 'author', 'tags',)

    def count_favorites(self, obj):
        result = FavoriteRecipe.objects.filter(recipe=obj).count()
        return result

    count_favorites.short_description = 'В избранном'


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('title', 'dimension',)
    list_filter = ('title',)


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(IngredientAmount)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag)
admin.site.register(FavoriteRecipe)
admin.site.register(Follow)
admin.site.register(ShoppingList)
