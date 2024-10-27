import json
import sys

filename = 'gymbeam_products_meal.json'

# load json and filter out items that don't have values
with open(r'./src/data/products/' + filename, encoding='utf-8') as f:
    data = json.load(f)

data = [item for item in data if 'GymBeam' in item['title'] and '€' in item['price'] and item['description'] != 'Опис не знайдено']

# save the result
with open(r'./src/data/products/' + filename, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)