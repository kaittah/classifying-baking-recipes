import numpy as np

from recipe_database.utils.build_dataset import convert_to_grams, get_nutrients_array, get_ingredients_array

def test_convert_to_grams_1():
    '''
    Given the recipe ingredient, convert the amount into grams
    '''
    ingredient = {'amount': 1, 'unit': 'cup', 'name': 'flour', 'ingredient_info': {
        'grams_in_cup': 125
    }}
    grams = convert_to_grams(ingredient)
    assert grams == 125

def test_convert_to_grams_2():
    '''
    Given the recipe ingredient, convert the amount into grams
    '''
    ingredient = {'amount': 1, 'unit': 'g', 'name': 'flour', 'ingredient_info': {
        'grams_in_cup': 125
    }}
    grams = convert_to_grams(ingredient)
    assert grams == 1

def test_nutrients_breakdown_1():
    '''
    get_nutrients_array returns an array of:
        grams protein
        grams unsaturated fat
        grams saturated fat
        grams sugar
        grams other carbohydrates
        grams water
    in the given amount of the given ingredient
    '''
    ingredient = {'amount': 250, 'unit': 'g', 'name': 'flour', 'ingredient_info': {
          "other_carbohydrates_fraction": 0.6671,
          "protein_fraction": 0.1315,
          "saturated_fat_fraction": 0.0111,
          "sugar_carbohydrates_fraction": 0.0099,
          "unsaturated_fat_fraction": 0.0541,
          "water_fraction": 0.12629999999999997
    }}
    nutrients_array = get_nutrients_array(ingredient)
    assert np.array_equal(nutrients_array,np.array([33, 14, 3, 2, 167, 32]))
