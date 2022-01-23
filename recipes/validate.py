from django.core.exceptions import ValidationError
from django.utils import timezone


def user_directory_path(instance, filename):
    image_format = filename.split('.')[-1]
    date = timezone.now().strftime('%d-%m-%Y %H.%M.%S')
    return (f'recipe_images/user_{instance.author.username}/'
            f'{date}_recipe_{instance.title}.{image_format}')


def validate_image(image_field_obj):
    filesize = image_field_obj.file.size
    megabyte_limit = 20
    if filesize > megabyte_limit * 1024 * 1024:
        raise ValidationError(
            (f'Файл слишком большой! '
             f'Максимальный размер файла: {megabyte_limit}MB'))
