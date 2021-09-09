from django import forms

from recipes.models import Recipe


class RecipeForm(forms.ModelForm):

    class Meta:
        model = Recipe
        fields = ('title', 'cooking_time', 'description', 'image', 'tags',)
        widgets = {
            'tags': forms.CheckboxSelectMultiple(),
            'description': forms.Textarea(attrs={'class': 'form__textarea'}),
        }
