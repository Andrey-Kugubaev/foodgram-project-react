from django.urls import path

from recipes import views

urlpatterns = [
    path('', views.index, name='index'),
    path('recipe/<int:recipe_id>/', views.view_recipe, name='view_recipe'),
    path('recipe/new/', views.add_recipe, name='add_recipe'),
    path('recipe/<int:recipe_id>/edit/', views.edit_recipe,
         name='edit_recipe'),
    path('recipe/<int:recipe_id>/delete/', views.del_recipe,
         name='del_recipe'),
    path(
        'recipes/<str:username>/',
        views.authors_recipes,
        name='authors_recipes'
    ),
    path('favorite/', views.favorite, name='favorite'),
    path('favorites/<int:recipe_id>/', views.favorites, name='favorites'),
    path('subscriptions_list/', views.subscriptions_list,
         name='subscriptions_list'),
    path('subscriptions/<int:author_id>/', views.subscriptions,
         name='subscriptions'),
    path('purchases/<int:recipe_id>/', views.purchases, name='purchases'),
    path('shopping_list/', views.shopping_list, name='shopping_list'),
    path('shopping_list/save/', views.shopping_list_save,
         name='shopping_list_save'),
    path('ingredients/', views.ingredients, name='ingredients')
]
