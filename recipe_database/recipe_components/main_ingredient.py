import requests
import time

from recipe_database.utils.connect import get_spoonacular_key

class MainIngredient:
    '''
    Ingredients that will be included in the feature set
    '''
    main_ingredient_names = ['almond flour', 'flour', 'water', 'sugar', 'peanut butter', 'unsalted butter', 'oil', 'evaporated milk', 
      'sweetened condensed milk', 'buttermilk', 'milk', 'sour cream', 'heavy cream', 'half-and-half', 'juice', 
      'honey', 'syrup', 'yogurt', 'oats', 'cocoa', 'unsweetened chocolate', 'white chocolate', 'semisweet chocolate chips', 
      'canned pumpkin', 'mashed banana', 'applesauce', 'corn starch', 'corn meal', 'egg', 'molasses', 'shortening', 
      'crisco', 'shredded coconut', 'zucchini', 'carrot', 'apple', 'berries', 'raisins', 'walnut', 'pecans', 
      'pistachio', 'potato', 'cinnamon', 'allspice', 'zest', 'nutmeg', 'ginger', 'cloves', 'spice', 'vanilla', 'yeast', 
      'baking soda', 'baking powder', 'salt', 'cream of tartar', 'vinegar', 'almond extract', 'rhubarb',
      'sprinkles', 'instant coffee', 'coffee']
    api_key = get_spoonacular_key()
    
    @staticmethod
    def get_spoonacular_id(ingredient):
        url = f'https://api.spoonacular.com/food/ingredients/search?query={ingredient}&offset=0&number=1&apiKey={MainIngredient.api_key}'
        response = requests.get(url)
        if response.status_code == 429:
            time.sleep(60)
            response = requests.get(url)
        if response.status_code != 200 or len(response.json()['results'])==0:
            return None
        else:
            return response.json()['results'][0]

    def __init__(self,  name):
        if name not in MainIngredient.main_ingredient_names:
            raise Exception('Not one of the main ingredients')
        self.name = name
        search_results = MainIngredient.get_spoonacular_id(name)
        self.spoonacular_id = search_results['id']
        self.spoonacular_name = search_results['name']
        nutrition_data, consistency, possible_units = self.get_nutrient_info(self.spoonacular_id)
        self.nutrition_data = nutrition_data
        self.consistency = consistency
        self.possible_units = possible_units
        if 'liter' in possible_units or 'fluid ounce' in possible_units:
            self.set_grams_in_ml()
        else:
            self.grams_in_ml = None
        if 'cup' in possible_units:
            self.set_grams_in_cup()
        else:
            self.grams_in_cup = None
        if 'teaspoon' in possible_units or 'tablespoon' in possible_units:
            self.set_grams_in_tsp()
        else:
            self.grams_in_tsp = None
        if 'piece' in possible_units:
            self.set_grams_in_whole()
        else:
            self.grams_in_whole = None

    @staticmethod
    def get_conversion_amount(ingredient, source_unit):
        url = f'https://api.spoonacular.com/recipes/convert?ingredientName={ingredient}&sourceAmount=1&sourceUnit={source_unit}&targetUnit=grams&apiKey={MainIngredient.api_key}'
        response = requests.get(url)
        if response.status_code == 429:
            time.sleep(60)
            response = requests.get(url)
        if response.status_code != 200:
            return None
        else:
            return response.json()['targetAmount']
    
    @staticmethod
    def get_nutrient_info(ingredient_id):
        url = f'https://api.spoonacular.com/food/ingredients/{ingredient_id}/information?amount=1000&unit=grams&apiKey={MainIngredient.api_key}'
        response = requests.get(url)
        if response.status_code == 429:
            time.sleep(60)
            response = requests.get(url)
        if response.status_code != 200:
            return None
        else:
            nutrition_data = response.json()
            consistency = nutrition_data.get('consistency', 'unspecified')
            possible_units = nutrition_data.get('possibleUnits', [])
            return nutrition_data, consistency, possible_units

    def set_grams_in_cup(self):
        self.grams_in_cup = self.get_conversion_amount(self.name, 'cup')

    def set_grams_in_ml(self):
        self.grams_in_ml = self.get_conversion_amount(self.name, 'milliliter')

    def set_grams_in_tsp(self):
        self.grams_in_tsp = self.get_conversion_amount(self.name, 'teaspoon')

    def set_grams_in_whole(self):
        self.grams_in_whole = self.get_conversion_amount(self.name, 'piece')

    def get_possible_units(self):
        return self.possible_units[:]
    
    def get_dictionary(self):
        properties = {  
                        'name': self.name,
                        'spoonacular_id': self.spoonacular_id,
                        'spoonacular_name': self.spoonacular_name,
                        'consistency': self.consistency,
                        'possible_units': self.possible_units,
                        'nutrition_data': self.nutrition_data
                     }
        if self.grams_in_cup:
            properties['grams_in_cup'] = self.grams_in_cup
        if self.grams_in_ml:
            properties['grams_in_ml'] = self.grams_in_ml
        if self.grams_in_tsp:
            properties['grams_in_tsp'] = self.grams_in_tsp
        if self.grams_in_whole:
            properties['grams_in_whole'] = self.grams_in_whole
        return properties
    
    def insert_into_mongo_db(self, db):
        document = self.get_dictionary()
        db.ingredients.replace_one({'name':self.name},document,upsert=True)
