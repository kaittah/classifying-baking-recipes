import re
import unicodedata as ud
from fractions import Fraction
import pytest

class Ingredient():
    COMMON_INGREDIENTS = [  
                            'buttermilk', 'almond flour', 'flour', 'water', 'sugar', 'peanut butter', 'butter', 
                            'oil', 'evaporated milk', 'sweetened condensed milk', 'milk', 'sour cream', 'heavy cream', 
                            'half-and-half', 'half and half', 'juice', 'honey', 'syrup', 'yogurt', 'oats', 'cocoa', 
                            'unsweetened chocolate', 'white chocolate', 'chocolate', 'pumpkin', 'banana', 'applesauce',
                             'cornstarch', 'corn starch', 'starch', 'corn meal', 'egg', 'molasses', 'shortening', 
                            'crisco', 'shredded coconut', 'zucchini', 'carrot', 'apple', 'berries', 'raisins', 'nuts', 'pecan', 
                            'pistachio', 'potato', 'cinnamon', 'allspice', 'zest', 'nutmeg', 'ginger', 'cloves', 'spice', 
                            'vanilla', 'yeast', 'baking soda', 'baking powder', 'salt', 'cream of tartar', 'vinegar', 
                            'almond extract', 'rhubarb', 'emulsion', 'extract', 'sprinkles', 'instant coffee', 'coffee', 'espresso powder'
                        ]
    COMMON_INGREDIENTS_PATTERN = r'.+?(' + r'|'.join([ingredient + r'[s]{0,1}\b' for ingredient in COMMON_INGREDIENTS]) + r').*?'
    METRIC_PATTERN = re.compile(r'([0-9.]+)\s*(g|oz|ml|gram|ounce|lb|pound)'+COMMON_INGREDIENTS_PATTERN,flags=re.IGNORECASE)
    CUP_PATTERN = re.compile(r'([0-9\u2150-\u215E\u00BC-\u00BE-\band\b/⁄\s]+)(cup|teaspoon|tbsp|tablespoon|tsp|tbl)' + COMMON_INGREDIENTS_PATTERN, 
                            flags=re.UNICODE|re.IGNORECASE)
    WHOLE_PATTERN = re.compile(r'([0-9\u2150-\u215E\u00BC-\u00BE-\band\b/⁄\s]+).+(egg|banana|apple|rubharb|zucchini|carrot|potato)([s|es]{0,1}\b){0,1}', flags=re.IGNORECASE)
    UNITS_DICTIONARY = {'gram':'g', 'ounce':'oz', 'pound':'lb', 'teaspoon':'tsp', 'tablespoon': 'tbsp', 't.': 'tbsp', 'c.': 'cup', 'tbl': 'tbsp'}
    INGREDIENTS_DICTIONARY = {'butter': 'unsalted butter', 'pumpkin': 'canned pumpkin', 'banana': 'mashed banana', 'cornstarch': 'corn starch', 'starch': 'corn starch', 'half and half': 'half-and-half',
                            'chocolate': 'semisweet chocolate chips', 'nuts': 'walnut', 'espresso powder': 'instant coffee', 'emulsion': 'vanilla', 'extract': 'vanilla'}

    def __init__(self, original_text):
        self.original_text = original_text
        self.parse_amount(original_text)

    def parse_amount(self, ingredient):
        metric_result = re.search(Ingredient.METRIC_PATTERN, ingredient)
        whole_result = re.search(Ingredient.WHOLE_PATTERN, ingredient)
        cup_result = re.search(Ingredient.CUP_PATTERN, ingredient)
        if metric_result:
            amount = metric_result.group(1)
            unit = metric_result.group(2)
            name = metric_result.group(3)
        elif cup_result:
            amount = cup_result.group(1)
            unit = cup_result.group(2)
            name = cup_result.group(3)
        elif whole_result and len(whole_result.groups())>1:
            amount = whole_result.group(1)
            unit = 'whole'
            name = whole_result.group(2)
        else:
            amount = unit = name = ''
        if name:
           name = name.strip().lower()
        new_name, new_unit, new_amount = self.standardize(name, unit, amount)

        self.name = new_name
        self.unit = new_unit
        self.amount = new_amount
        self.original_name = name
        self.original_unit = unit
        self.original_amount = amount

    @staticmethod
    def standardize(name, unit, amount):
        unit = unit.strip().lower()
        new_name = Ingredient.INGREDIENTS_DICTIONARY.get(name, name)
        new_unit = Ingredient.UNITS_DICTIONARY.get(unit, unit)
        cleaned_amount = ud.normalize('NFKD', str(amount).lower().replace('and', '').replace('-', ' '))
        new_amount = 0
        vulgar_fraction_index = cleaned_amount.find('⁄')
        if vulgar_fraction_index > -1:
            new_amount += float(Fraction(*map(int, (cleaned_amount[vulgar_fraction_index-1], cleaned_amount[vulgar_fraction_index+1]))))
            cleaned_amount = cleaned_amount[:vulgar_fraction_index-1]
        try:
            new_amount += float(sum(Fraction(s.strip()) for s in cleaned_amount.split() if len(s.strip())>0))
        except:
            print('Invalid quantity ', amount, name)
        return new_name, new_unit, new_amount    
        
    def get_dictionary(self):
        return {
            'name': self.name,
            'original_text': self.original_text,
            'unit': self.unit,
            'amount': self.amount
        }
    
    def get_labeling(self):
        text = self.original_text.lower().strip()
        name_index, name_length = text.find(self.original_name.strip()), len(self.original_name.strip())
        unit_index, unit_length = text.find(self.original_unit.strip()), len(self.original_unit.strip())
        amount_index, amount_length = text.find(self.original_amount.strip()), len(self.original_amount.strip())
        if min([name_index, unit_index, amount_index]) > -1 and min([name_length, unit_length, amount_length]) > 0:
            return ( text[:amount_index], 
                 (text[amount_index: amount_index + amount_length + 1], "amount"),
                 text[amount_index + amount_length + 1: unit_index], 
                 (text[unit_index: unit_index + unit_length + 1], "unit"),
                 text[unit_index + unit_length + 1: name_index], 
                 (text[name_index: name_index + name_length + 1], "name"),
                 text[name_index + name_length + 1:]
                )
        elif min([name_index, amount_index]) > -1 and min([name_length, amount_length]) > 0: 
            return ( text[:amount_index], 
                 (text[amount_index: amount_index + amount_length + 1], "amount"),
                 text[amount_index + amount_length + 1: name_index], 
                 (text[name_index: name_index + name_length + 1], "name"),
                 text[name_index + name_length + 1:]
                ) 
        else:
            return (text)