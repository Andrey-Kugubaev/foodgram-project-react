from django import template

register = template.Library()


@register.filter
def addclass(field, css):
    return field.as_widget(attrs={'class': css})


@register.filter
def favorite_recipe(things, recipe):
    return things.filter(recipe=recipe)


@register.filter
def follow_author(things, author):
    return things.filter(author=author)


@register.filter
def tags_link(request, tag):
    new_request = request.GET.copy()
    tag_id = str(tag.id)
    if tag_id in request.GET.getlist('tags'):
        tags = new_request.getlist('tags')
        tags.remove(tag_id)
        new_request.setlist('tags', tags)
    else:
        new_request.appendlist('tags', tag.id)
    return new_request.urlencode()
