from matplotlib.pyplot import get
import numpy as np

from recipe_database.utils.connect import get_mongo_client

def convert_to_grams(ingredient):
    og_amount = ingredient['amount']
    og_unit = ingredient['unit']
    if og_unit == 'g':
        amount = og_amount
    elif og_unit == 'tsp':
        amount = og_amount*ingredient['ingredient_info'].get('grams_in_tsp',0)
    elif og_unit == 'tbsp':
        if ingredient['ingredient_info'].get('grams_in_tsp'):
            amount = og_amount*ingredient['ingredient_info']['grams_in_tsp']*3
        else:
            amount = og_amount*ingredient['ingredient_info'].get('grams_in_cup',0)/16
    elif og_unit == 'cup':
        amount = og_amount*ingredient['ingredient_info'].get('grams_in_cup',0)
    elif og_unit == 'ml':
        if ingredient['ingredient_info'].get('grams_in_ml',1):
            amount = og_amount*ingredient['ingredient_info'].get('grams_in_ml',1)
        else:
            amount = og_amount
    elif og_unit == 'oz':
        amount = og_amount*28.3495
    elif og_unit == 'whole':
        amount = og_amount*ingredient['ingredient_info'].get('grams_in_whole',0)
    else:
        amount = 0 
    return round(amount)

def get_nutrients_array(ingredient):
    gram_amount = convert_to_grams(ingredient)
    nutrients_list = ['protein_fraction', 'unsaturated_fat_fraction', 'saturated_fat_fraction', 'sugar_carbohydrates_fraction',
                      'other_carbohydrates_fraction', 'water_fraction']
    return np.array([round(gram_amount*ingredient['ingredient_info'][nutrient_fraction]) for nutrient_fraction in nutrients_list], dtype = float)

def get_ingredients_array(ingredient):
    gram_amount = convert_to_grams(ingredient)
    ingredients_list = [ 'almond flour', 'flour', 'water', 'sugar', 'peanut butter', 'unsalted butter', 'oil', 'evaporated milk', 
      'sweetened condensed milk', 'buttermilk', 'milk', 'sour cream', 'heavy cream', 'half-and-half', 'juice', 
      'honey', 'syrup', 'yogurt', 'oats', 'cocoa', 'unsweetened chocolate', 'white chocolate', 'semisweet chocolate chips', 
      'canned pumpkin', 'mashed banana', 'applesauce', 'corn starch', 'corn meal', 'egg', 'molasses', 'shortening', 
      'crisco', 'shredded coconut', 'zucchini', 'carrot', 'apple', 'berries', 'raisins', 'walnut', 'pecans', 
      'pistachio', 'potato', 'cinnamon', 'allspice', 'zest', 'nutmeg', 'ginger', 'cloves', 'spice', 'vanilla', 'yeast', 
      'baking soda', 'baking powder', 'salt', 'cream of tartar', 'vinegar', 'almond extract', 'rhubarb',
      'sprinkles', 'instant coffee', 'coffee']
    return np.array([gram_amount*(1 if ingredient['name'] == ingredient_name else 0) for ingredient_name in ingredients_list], dtype = float)

def get_dataset(db = None, recipe_id = None):
    nutition_by_ingredient_func = np.vectorize(get_nutrients_array, otypes=[np.ndarray])
    amount_by_ingredient_func = np.vectorize(get_ingredients_array, otypes=[np.ndarray])
    if db == None:
        client = get_mongo_client()
        db = client.recipe_analysis
    aggregation_pipeline = [{ "$unwind": "$ingredients" },
        {
            '$lookup': {
                'from': "ingredient_features",
                'localField': "ingredients.name",   
                'foreignField': "name",  
                'as': "ingredients.ingredient_info"
            }
        },
        { "$unwind": "$ingredients.ingredient_info" },
        { "$group": {
            "_id": "$_id",
            "title": {"$first": "$title"},
            "website": {"$first": "$website"},
            "category": {"$first": "$category"},
            "url": {"$first":"$url"},
            "ingredients": { "$push": "$ingredients" }
        }}
            ]
    if recipe_id:
        aggregation_pipeline.insert(0, {'$match': {'_id': recipe_id}})
    else:
        aggregation_pipeline.insert(0, {'$match': {'category': {'$ne': None}}})
    r = db.recipes.aggregate(aggregation_pipeline)

    X = None
    categories = []
    recipe_strings = []
    titles = []
    urls = []
    ids = []
    for document in r:
        category = document['category']
        title = document['title']
        url = document['url']
        id = document['_id']
        ingredients = np.array([i for i in document['ingredients'] if i['amount'] and i['amount'] > 0 and i.get('ingredient_info')], dtype=object)
        ingredients_string = '\n\n'.join([i['original_text'] for i in ingredients])
        nutition_by_ingredient = np.stack(nutition_by_ingredient_func(ingredients)).sum(axis=0)
        amount_by_ingredient = np.stack(amount_by_ingredient_func(ingredients)).sum(axis=0)
        nutrition_fractions = nutition_by_ingredient/nutition_by_ingredient.sum()
        ingredient_fractions = amount_by_ingredient/amount_by_ingredient.sum()
        combined = np.concatenate((nutrition_fractions[:-1],ingredient_fractions[:-1]))
        if isinstance(X, np.ndarray):
            X = np.concatenate((X, combined.flatten().reshape(1,-1)), axis=0)
        else:
            X = combined.flatten().reshape(1,-1)
        categories.append(category)
        titles.append(title)
        urls.append(url)
        ids.append(id)
        recipe_strings.append(ingredients_string)

    np.nan_to_num(X, copy=False)
    return X, categories, recipe_strings, titles, urls, ids

if __name__ == '__main__':
    X, y = get_dataset()

    print('hi')