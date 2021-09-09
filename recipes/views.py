from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import F, Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from foodgram import settings
from recipes.forms import RecipeForm
from recipes.models import (FavoriteRecipe, Follow, Ingredient, Recipe,
                            ShoppingList)
from recipes.utils import (add_ingredients_to_recipe, get_ingredients,
                           get_tags_for_filter, ingredients_for_shopping_list,
                           save_recipe)

User = get_user_model()

OBJECT_PER_PAGE = settings.OBJECT_PER_PAGE


@require_http_methods(['GET'])
def ingredients(request):
    query = (request.GET['query']).lower()
    ingredients_list = (
        Ingredient.objects.values(
            'title',
            'dimension',
        ).filter(title__icontains=query)
    )
    context = list(ingredients_list)
    return JsonResponse(context, safe=False)


def index(request):
    tags, tags_for_filter = get_tags_for_filter(request)
    recipes = Recipe.objects.filter(tags__in=tags_for_filter).distinct()
    paginator = Paginator(recipes, OBJECT_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page,
        'paginator': paginator,
        'tags': tags,
        'tags_for_filter': tags_for_filter,
    }
    return render(request, 'index.html', context)


def authors_recipes(request, username):
    author = get_object_or_404(User, username=username)
    tags, tags_for_filter = get_tags_for_filter(request)
    recipe_list = Recipe.objects.filter(author=author,
                                        tags__in=tags_for_filter).distinct()
    paginator = Paginator(recipe_list, OBJECT_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page,
        'paginator': paginator,
        'author': author,
        'tags': tags,
        'tags_for_filter': tags_for_filter,
    }
    if request.user.is_authenticated:
        my_user = request.user
        follow = Follow.objects.filter(user=my_user, author=author)
        follow_or_author = follow or my_user == author
        context['follow_or_author'] = follow_or_author
    return render(request, 'authors_recipes.html', context)


def view_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    context = {
        'recipe': recipe,
    }
    return render(request, 'recipe_view.html', context)


@login_required
def add_recipe(request):
    form = RecipeForm(request.POST or None, files=request.FILES or None, )
    if form.is_valid():
        recipe = save_recipe(request, form)
        return redirect(to=view_recipe, recipe_id=recipe.id)
    context = {
        'form': form,
    }
    return render(request, 'recipe_form.html', context)


@login_required
def edit_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if request.user != recipe.author and not request.user.is_staff:
        return redirect(to=view_recipe, recipe_id=recipe_id)
    form = RecipeForm(
        request.POST or None,
        files=request.FILES or None,
        instance=recipe
    )
    if form.is_valid():
        recipe.ingredients.clear()
        form.save()
        ingredients = get_ingredients(request)
        add_ingredients_to_recipe(ingredients, recipe)
        return redirect(to=view_recipe, recipe_id=recipe_id)
    context = {
        'form': form,
        'recipe': recipe,
    }
    return render(request, 'recipe_form.html', context)


@login_required
def del_recipe(request, recipe_id):
    my_user = request.user
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if my_user != recipe.author and not my_user.is_staff:
        return redirect(to=view_recipe, recipe_id=recipe_id)
    recipe.delete()
    return redirect(to=index)


@login_required
def favorite(request):
    tags, tags_for_filter = get_tags_for_filter(request)
    my_user = request.user
    recipes_list = my_user.favorite_recipes.filter(
        recipe__tags__in=tags_for_filter).distinct()
    paginator = Paginator(recipes_list, OBJECT_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page,
        'paginator': paginator,
        'tags': tags,
        'tags_for_filter': tags_for_filter,
    }
    return render(request, 'favorite.html', context)


@login_required
def subscriptions_list(request):
    my_user = request.user
    following_authors = User.objects.filter(following__user=my_user)
    paginator = Paginator(following_authors, 3)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page,
        'paginator': paginator
    }
    return render(request, 'subscriptions.html', context)


@login_required
@require_http_methods(['POST', 'DELETE'])
def favorites(request, recipe_id):
    my_user = request.user
    recipe = get_object_or_404(Recipe, id=recipe_id)
    context = {'success': True}
    if request.method == 'POST':
        _, created = FavoriteRecipe.objects.get_or_create(user=my_user,
                                                          recipe=recipe)
        return JsonResponse(context)
    favorite_recipe = get_object_or_404(FavoriteRecipe, user=my_user,
                                        recipe__id=recipe_id)
    favorite_recipe.delete()
    return JsonResponse(context)


@login_required
@require_http_methods(['POST', 'DELETE'])
def subscriptions(request, author_id):
    my_user = request.user
    author = get_object_or_404(User, id=author_id)
    context = {'success': True}
    if request.method == 'POST':
        _, created = Follow.objects.get_or_create(user=my_user, author=author)
        return JsonResponse(context)
    subscription = Follow.objects.filter(user=my_user, author=author)
    if subscription.exists():
        subscription.delete()
    return JsonResponse(context)


@login_required
@require_http_methods(['POST', 'DELETE'])
def purchases(request, recipe_id):
    my_user = request.user
    recipe = get_object_or_404(Recipe, id=recipe_id)
    context = {'success': True}
    if request.method == 'POST':
        _, created = ShoppingList.objects.get_or_create(user=my_user,
                                                        recipe=recipe)
        return JsonResponse(context)
    favorite_recipe = get_object_or_404(ShoppingList, user=my_user,
                                        recipe=recipe)
    favorite_recipe.delete()
    return JsonResponse(context)


@login_required
def shopping_list(request):
    my_user = request.user
    shopping_list = my_user.users_shopping_lists.all()
    context = {
        'shopping_list': shopping_list,
    }
    return render(request, 'shopping_list.html', context)


@login_required
def shopping_list_save(request):
    my_user = request.user
    ingredient_list = Recipe.objects.prefetch_related(
        'ingredients', 'ingredients_amount'
    ).filter(
        at_shopping_lists__user=my_user
    ).order_by(
        'ingredients__title'
    ).values(
        'ingredients__title', 'ingredients__dimension'
    ).annotate(
        title=F('ingredients__title'),
        amount=Sum('ingredients_amount__amount'),
        dimension=F('ingredients__dimension')
    )
    ingredient_txt = ingredients_for_shopping_list(ingredient_list)
    filename = 'shoppinglist.txt'
    response = HttpResponse(ingredient_txt, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename={filename}'
    return response
