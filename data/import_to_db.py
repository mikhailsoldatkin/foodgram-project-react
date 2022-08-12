import json
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "foodgram.settings")

import django

django.setup()
from recipes.models import Ingredient

path = '.'
os.chdir(path)

with open('ingredients.json', encoding='utf8') as f:
    data = json.load(f)
    for element in data:
        instance = Ingredient(
            name=element['name'],
            measurement_unit=element['measurement_unit']
        )
        instance.save()
