from recipe_database.utils.connect import get_mongo_client
from recipe_database.recipe_components.main_ingredient import MainIngredient

def collect_ingredients(ingredient, db):
    '''
    Find ingredient properties using Spoonacular API and save into MongoDB's ingredients collection
    '''
    spoonacular_ingredient = MainIngredient(ingredient)
    spoonacular_ingredient.insert_into_mongo_db(db)

def summarize_properties(db):
    '''
    Use information from the ingredients collection to summarize the ingredient properties by their:
        protein_fraction: grams protein per gram of ingredient
        saturated_fat_fraction: grams saturated fat per gram of ingredient
        unsaturated_fat_fraction: grams unsaturated fat per gram of ingredient
        sugar_fraction: grams sugar per gram of ingredient
        carbohydrates_fraction: grams carbohydrates excluding sugar per gram of ingredient
        water_fraction: grams water per gram of ingredient, equal to 1 - sum of all nutrient fractions
    Saves as documents in the mongoDB ingredient_features collection
    '''
    db.ingredients.aggregate([
            {
                '$unwind': {
                'path': "$nutrition_data.nutrition.nutrients"
                }
            },
            {
                '$match': {
                "nutrition_data.nutrition.nutrients.name": {
                    '$in': [
                    "Protein",
                    "Saturated Fat",
                    "Fat",
                    "Carbohydrates",
                    "Sugar"
                    ]
                }
                }
            },
            {
                '$match': {
                "nutrition_data.nutrition.nutrients.unit": "g"
                }
            },
            {
                '$group': {
                '_id': "$name",
                'consistency': {'$first': "$consistency"},
                'grams_in_cup': {'$first': "$grams_in_cup"},
                'grams_in_tsp': {'$first': "$grams_in_tsp"},
                'grams_in_ml': {'$first': "$grams_in_ml"},
                'grams_in_whole': {'$first': "$grams_in_whole"},
                'name': {'$first': "$name"},
                'protein_content': {
                    '$max': {
                    '$switch': {
                        'branches': [
                        {
                            'case': {
                            '$eq': [
                                "$nutrition_data.nutrition.nutrients.name",
                                "Protein"
                            ]
                            },
                            'then': "$nutrition_data.nutrition.nutrients.amount"
                        }
                        ],
                        'default': 0
                    }
                    }
                },
                'saturated_fat_content': {
                    '$max': {
                    '$switch': {
                        'branches': [
                        {
                            'case': {
                            '$eq': [
                                "$nutrition_data.nutrition.nutrients.name",
                                "Saturated Fat"
                            ]
                            },
                            'then': "$nutrition_data.nutrition.nutrients.amount"
                        }
                        ],
                        'default': 0
                    }
                    }
                },
                'fat_content': {
                    '$max': {
                    '$switch': {
                        'branches': [
                        {
                            'case': {
                            '$eq': [
                                "$nutrition_data.nutrition.nutrients.name",
                                "Fat"
                            ]
                            },
                            'then': "$nutrition_data.nutrition.nutrients.amount"
                        }
                        ],
                        'default': 0
                    }
                    }
                },
                'carbohydrates_content': {
                    '$max': {
                    '$switch': {
                        'branches': [
                        {
                            'case': {
                            '$eq': [
                                "$nutrition_data.nutrition.nutrients.name",
                                "Carbohydrates"
                            ]
                            },
                            'then': "$nutrition_data.nutrition.nutrients.amount"
                        }
                        ],
                        'default': 0
                    }
                    }
                },
                'sugar_content': {
                    '$max': {
                    '$switch': {
                        'branches': [
                        {
                            'case': {
                            '$eq': [
                                "$nutrition_data.nutrition.nutrients.name",
                                "Sugar"
                            ]
                            },
                            'then': "$nutrition_data.nutrition.nutrients.amount"
                        }
                        ],
                        'default': 0
                    }
                    }
                }
                }
            },
            {
                '$group': {
                '_id': "$_id",
                'consistency': {'$first': "$consistency"},
                'grams_in_cup': {'$first': "$grams_in_cup"},
                'grams_in_ml': {'$first': "$grams_in_ml"},
                'grams_in_whole': {'$first': "$grams_in_whole"},
                'grams_in_tsp': {'$first': "$grams_in_tsp"},
                'name': {'$first': "$name"},
                'protein_fraction': {
                    '$max': {
                    '$divide': [
                        "$protein_content",
                        1000
                    ]
                    }
                },
                'saturated_fat_fraction': {
                    '$max': {
                    '$divide': [
                        "$saturated_fat_content",
                        1000
                    ]
                    }
                },
                'unsaturated_fat_fraction': {
                    '$max': {
                            '$switch': {
                                        'branches': [
                                                {
                                                    'case': {
                                                    '$gt': [
                                                        "$fat_content",
                                                        "$saturated_fat_content"
                                                    ]
                                                    },
                                                    'then': {'$divide': [
                                                        {"$subtract": ["$fat_content", "$saturated_fat_content"]},
                                                        1000]
                                                }
                                                }
                                                ]
                                                ,
                                        'default': 0
                                        }                
                    }
                },
                'other_carbohydrates_fraction': {
                    '$max': {
                            '$switch': {
                                        'branches': [
                                                {
                                                    'case': {
                                                    '$gt': [
                                                        "$carbohydrates_content",
                                                        "$sugar_content"
                                                    ]
                                                    },
                                                    'then': {'$divide': [
                                                        {"$subtract": ["$carbohydrates_content", "$sugar_content"]},
                                                        1000]
                                                }
                                                }
                                                ]
                                                ,
                                        'default': 0
                                        }                
                    }
                },
                'sugar_carbohydrates_fraction': {
                    '$max': {
                    '$divide': [
                        "$sugar_content",
                        1000
                    ]
                    }
                },
                'water_fraction': {
                    '$max': {
                    '$divide': [
                        {
                        '$subtract': [
                            1000,
                            {
                            '$add': [
                                "$protein_content",
                                "$fat_content",
                                "$carbohydrates_content"
                            ]
                            }
                        ]
                        },
                        1000
                    ]
                    }
                }
                }
            },
            { '$merge': {
                'into': "ingredient_features",
                'on': "_id"
            } }
            ])
    
    db.ingredient_features.update_many({'grams_in_cup': None}, {'$unset' : { 'grams_in_cup' : 1 }})
    db.ingredient_features.update_many({'grams_in_ml': None}, {'$unset' : { 'grams_in_ml' : 1 }})
    db.ingredient_features.update_many({'grams_in_whole': None}, {'$unset' : { 'grams_in_whole' : 1 }})
    db.ingredient_features.update_many({'grams_in_tsp': None}, {'$unset' : { 'grams_in_tsp' : 1 }})

if __name__ == '__main__':
    client = get_mongo_client(streamlit = False)
    db = client.recipe_analysis
    
    # for ingredient in [ 'almond flour', 'flour', 'water', 'sugar', 'peanut butter', 'unsalted butter', 'oil', 'evaporated milk', 
    #                     'sweetened condensed milk', 
    #                     'buttermilk', 'milk', 'sour cream', 'heavy cream', 'half-and-half', 'juice', 
    #                     'honey', 'syrup', 'yogurt', 'oats', 'cocoa', 'unsweetened chocolate', 'white chocolate', 
    #                     'semisweet chocolate chips', 
    #                     'canned pumpkin', 'mashed banana', 'applesauce', 'corn starch', 'corn meal', 'egg', 
    #                     'molasses', 'shortening', 
    #                     'crisco', 'shredded coconut', 'zucchini', 'carrot', 'apple', 'berries', 'raisins', 
    #                     'walnut', 'pecans', 
    #                     'pistachio', 'potato', 'cinnamon', 'allspice', 'zest', 'nutmeg', 
    #                     'ginger', 'cloves', 'spice', 'vanilla', 'yeast', 
    #                     'baking soda', 'baking powder', 'salt', 'cream of tartar', 'vinegar', 
    #                     'almond extract', 'rhubarb',
    #                     'sprinkles', 'instant coffee', 'coffee']:
    #     collect_ingredients(ingredient, db)
    summarize_properties(db)