from django.shortcuts import get_object_or_404

from recipes.models import Ingredient, IngredientAmount, Tag


def get_ingredients(request):
    ingredients = {}
    for key in request.POST:
        if key.startswith('nameIngredient'):
            ingredient_id = key.split('_')[-1]
            ingredient_name = request.POST[key]
            ingredient_value = int(
                request.POST['valueIngredient_' + ingredient_id]
            )
            if ingredient_value < 1:
                continue
            ingredients[ingredient_name] = (
                    ingredients.get(ingredient_name, 0) + ingredient_value
            )
    return ingredients


def add_ingredients_to_recipe(ingredients, recipe):
    ingredient_amount = []
    for title, amount in ingredients.items():
        ingredient = get_object_or_404(Ingredient, title=title)
        ingredient_amount.append(
            IngredientAmount(
                recipe=recipe,
                ingredient=ingredient,
                amount=amount
            )
        )
    IngredientAmount.objects.bulk_create(ingredient_amount)
    return True


def save_recipe(request, form):
    tags = form.cleaned_data['tags']
    recipe = form.save(commit=False)
    recipe.author = request.user
    recipe.save()
    recipe.tags.set(tags)
    ingredients = get_ingredients(request)
    add_ingredients_to_recipe(ingredients, recipe)
    return recipe


def get_tags_for_filter(request):
    tags = Tag.objects.all()
    tags_id = tags.values_list('id', flat=True)
    request_tag_id = [int(tag_id) for tag_id in request.GET.getlist('tags')]
    tags_for_filter = request_tag_id or tags_id
    return tags, tags_for_filter,


def ingredients_for_shopping_list(ingredients):
    ingredient_txt = [
        '************************\n'
        '*  Список игредиентов  *\n',
        '************************\n',
        '\n',
    ]
    count = 1
    if (not ingredients
            or ingredients.count() <= 1
            and ingredients[0].get('title') is None):
        ingredient_txt.append('   ---   ПУСТО   ---\n')
        return ingredient_txt
    for item in ingredients:
        title = item.get('title')
        if title is None:
            continue
        ingredient_txt.append(
            (f"{count}. {title.capitalize()} "
             f"\u2014 {item['amount']} {item['dimension']}.\n")
        )
        count += 1
    return ingredient_txt
