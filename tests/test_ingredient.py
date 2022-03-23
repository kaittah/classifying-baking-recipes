from recipe_database.recipe_components.ingredient import Ingredient

def test_ingredient_1():
    i = Ingredient('1 egg')
    assert i.name == 'egg'
    assert i.unit == 'whole'
    assert i.amount == 1
    assert i.original_name == 'egg'
    assert i.original_unit == 'whole'
    assert i.original_amount == '1'
    assert i.original_text == '1 egg'

def test_ingredient_2():
    i = Ingredient('100 eggs')
    assert i.name == 'egg'
    assert i.unit == 'whole'
    assert i.amount == 100
    assert i.original_name == 'egg'
    assert i.original_unit == 'whole'
    assert i.original_amount == '100'
    assert i.original_text == '100 eggs'

def test_ingredient_3():
    i = Ingredient(' 1 cup flour ')
    assert i.name == 'flour'
    assert i.unit == 'cup'
    assert i.amount == 1
    assert i.original_name == 'flour'
    assert i.original_unit == 'cup'
    assert i.original_amount == ' 1 '
    assert i.original_text == ' 1 cup flour '

def test_ingredient_4():
    i = Ingredient('2 3/4 cup unsalted butter, melted')
    assert i.name == 'unsalted butter'
    assert i.unit == 'cup'
    assert i.amount == 2.75
    assert i.original_name == 'butter'
    assert i.original_unit == 'cup'
    assert i.original_amount == '2 3/4 '
    assert i.original_text == '2 3/4 cup unsalted butter, melted'

def test_ingredient_5():
    i = Ingredient('2-½ teaspoon salt ')
    assert i.name == 'salt'
    assert i.unit == 'tsp'
    assert i.amount == 2.5
    assert i.original_name == 'salt'
    assert i.original_unit == 'teaspoon'
    assert i.original_amount == '2-½ '
    assert i.original_text == '2-½ teaspoon salt '

def test_ingredient_6():
    i = Ingredient('1 1⁄2 cups sugar')
    assert i.name == 'sugar'
    assert i.unit == 'cup'
    assert i.amount == 1.5
    assert i.original_name == 'sugar'
    assert i.original_unit == 'cup'
    assert i.original_amount == '1 1⁄2 '
    assert i.original_text == '1 1⁄2 cups sugar'

def test_ingredient_6():
    i = Ingredient('2½ large zucchinis ')
    assert i.name == 'zucchini'
    assert i.unit == 'whole'
    assert i.amount == 2.5
    assert i.original_name == 'zucchini'
    assert i.original_unit == 'whole'
    assert i.original_amount == '2½ '
    assert i.original_text == '2½ large zucchinis '

def test_standardization_1():
    '''
    Test conversion of fractions to decimal
    '''
    new_name, new_unit, new_amount = Ingredient.standardize('flour', 'cup', '½')
    assert (new_name, new_unit, new_amount) == ('flour', 'cup', 0.5)

def test_standardization_2():
    '''
    Test conversion of long unit to short unit
    '''
    new_name, new_unit, new_amount = Ingredient.standardize('banana', 'tablespoon', '3 ½')
    assert (new_name, new_unit, new_amount) == ('mashed banana', 'tbsp', 3.5)

def test_standardization_3():
    '''
    Test conversion of strange fraction format
    '''
    new_name, new_unit, new_amount = Ingredient.standardize('flour', 'cup', '6 3⁄4')
    assert (new_name, new_unit, new_amount) == ('flour', 'cup', 6.75)

def test_standardization_4():
    '''
    Test conversion of strange fraction format
    '''
    new_name, new_unit, new_amount = Ingredient.standardize('flour', 'cup', '1 1⁄2 cups sugar')
    assert (new_name, new_unit, new_amount) == ('flour', 'cup', 1.5)