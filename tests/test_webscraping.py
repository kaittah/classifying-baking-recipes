import os
import pytest

from collect_recipes import scrape_brown_eyed_baker_main, scrape_brown_eyed_baker_search_results, \
                                    scrape_food_dot_com, scrape_sallys_baking_addiction

#Test that webscraping results in a list of links
def test_url_scraping_1():
    scraper, base_urls = scrape_brown_eyed_baker_main(test_mode=True)
    for category, url_template, x_path in base_urls:
        scraper.scrape_links_from_webpage(category, url_template, x_path)

def test_url_scraping_2():
    scraper, base_urls = scrape_brown_eyed_baker_search_results(test_mode=True)
    for category, url_template, x_path in base_urls:
        scraper.scrape_links_from_webpage(category, url_template, x_path)

def test_url_scraping_3():
    scraper, base_urls = scrape_sallys_baking_addiction(test_mode=True)
    for category, url_template, x_path in base_urls:
        scraper.scrape_links_from_webpage(category, url_template, x_path)

def test_url_scraping_4():
    scraper, base_urls = scrape_food_dot_com(test_mode=True)
    for category, url_template, x_path in base_urls:
        scraper.scrape_links_from_webpage(category, url_template, x_path)

#Test that recipe ingredients are correctly scraped from the link
def test_recipe_scraping_1():
    '''
    Transforms ingredients on page:
    2 cups all-purpose flour
    ¾ teaspoon baking soda
    ½ teaspoon salt
    3 medium bananas, mashed
    ½ cup creamy peanut butter
    ½ cup granulated sugar
    ½ cup light brown sugar
    ⅓ cup buttermilk
    ¼ cup vegetable oil
    2 eggs
    2 teaspoons vanilla extract
    1 cup semisweet chocolate chips
    '''

    scraper, base_urls = scrape_brown_eyed_baker_main(test_mode=True)
    scraper.scrape_recipe('https://www.browneyedbaker.com/peanut-butter-banana-bread-recipe-chocolate-chips/', 'bread')
    #assert len(scraper.errors) == 0
    assert len(scraper.recipes) == 1
    recipe = scraper.recipes[0]
    assert recipe.title == 'Peanut Butter Banana Bread'
    assert recipe.website == 'BEB'
    expected_ingredients = [[2, 'cup', 'flour'],
                            [0.75, 'tsp', 'baking soda'],
                            [0.5, 'tsp', 'salt'],
                            [3, 'whole', 'mashed banana'],
                            [0.5, 'cup', 'peanut butter'],
                            [0.5, 'cup', 'sugar'],
                            [0.5, 'cup', 'sugar'],
                            [1/3, 'cup', 'buttermilk'],
                            [0.25, 'cup', 'oil'],
                            [2, 'whole', 'egg'],
                            [2, 'tsp', 'vanilla'], 
                            [1, 'cup', 'semisweet chocolate chips']]
    ingredients = recipe.ingredients
    for ingredient in ingredients:
        ingredient_list = [ingredient['amount'], ingredient['unit'], ingredient['name']]
        if ingredient_list in expected_ingredients:
            expected_ingredients.remove(ingredient_list)
        else:
            assert 0

def test_recipe_scraping_2():
    '''
    Transforms ingredients on page:
    3 cups all-purpose flour
    1 teaspoon baking soda
    1 teaspoon salt
    ½ teaspoon baking powder
    2 cups granulated sugar
    1 cup vegetable oil
    3 eggs
    1 tablespoon vanilla extract
    4 ripe bananas, peeled and coarsely mashed
    '''
    scraper, base_urls = scrape_brown_eyed_baker_search_results(test_mode=True)
    scraper.scrape_recipe('https://www.browneyedbaker.com/banana-muffins-2/', 'muffin')
    #assert len(scraper.errors) == 0
    assert len(scraper.recipes) == 1
    recipe = scraper.recipes[0]
    assert recipe.title == 'Banana Muffins'
    assert recipe.website == 'BEB'
    expected_ingredients = [[3, 'cup', 'flour'],
                            [1, 'tsp', 'baking soda'],
                            [1, 'tsp', 'salt'],
                            [0.5, 'tsp', 'baking powder'],
                            [2, 'cup', 'sugar'],
                            [1, 'cup', 'oil'],
                            [3, 'whole', 'egg'],
                            [1, 'tbsp', 'vanilla'], 
                            [4, 'whole', 'mashed banana']]
    ingredients = recipe.ingredients
    for ingredient in ingredients:
        ingredient_list = [ingredient['amount'], ingredient['unit'], ingredient['name']]
        if ingredient_list in expected_ingredients:
            expected_ingredients.remove(ingredient_list)
        else:
            assert 0

def test_recipe_scraping_3():
    '''
    Transforms ingredients on page:
    2 and 2/3 cups (315g) cake flour (spoon & leveled)
    2 teaspoons baking powder
    1/2 teaspoon baking soda
    1 teaspoon salt
    3/4 cup (1.5 sticks; 170g) unsalted butter, softened to room temperature
    5 teaspoons espresso powder
    1 and 3/4 cups (350g) granulated sugar
    4 large egg whites, at room temperature
    1/2 cup (120g) sour cream, at room temperature
    2 teaspoons pure vanilla extract
    2/3 cup (160ml) whole milk, at room temperature
    1/3 cup (80ml) brewed strong black coffee, at room temperature
    1 and 1/4 cups (225g) mini chocolate chips (see note)
    '''
    scraper, base_urls = scrape_sallys_baking_addiction(test_mode=True)
    scraper.scrape_recipe('https://sallysbakingaddiction.com/espresso-chocolate-chip-cake/', 'cake')
    assert len(scraper.errors) == 0
    assert len(scraper.recipes) == 1
    recipe = scraper.recipes[0]
    assert recipe.title == 'Espresso Chocolate Chip Cake'
    assert recipe.website == 'SBA'
    expected_ingredients = [[315, 'g', 'flour'],
                            [2, 'tsp', 'baking powder'],
                            [0.5, 'tsp', 'baking soda'],
                            [1, 'tsp', 'salt'],
                            [170, 'g', 'unsalted butter'],
                            [5, 'tsp', 'instant coffee'],
                            [350, 'g', 'sugar'],
                            [4, 'whole', 'egg'],
                            [120, 'g', 'sour cream'], 
                            [2, 'tsp', 'vanilla'],
                            [160, 'ml', 'milk'],
                            [80, 'ml', 'coffee'],
                            [225, 'g', 'semisweet chocolate chips']]
    ingredients = recipe.ingredients
    for ingredient in ingredients:
        ingredient_list = [ingredient['amount'], ingredient['unit'], ingredient['name']]
        if ingredient_list in expected_ingredients:
            expected_ingredients.remove(ingredient_list)
        else:
            assert 0

def test_recipe_scraping_4():
    '''
    1 cup butter, softened
    1 1⁄2 cups sugar
    2 large eggs
    2 3⁄4 cups flour
    2 teaspoons cream of tartar
    1 teaspoon baking soda
    1⁄4 teaspoon salt
    3 tablespoons sugar
    3 teaspoons cinnamon
    1 teaspoon vanilla extract
    '''
    scraper, base_urls = scrape_food_dot_com(test_mode=True)
    scraper.scrape_recipe('https://www.food.com/recipe/soft-snickerdoodle-cookies-97496', 'cookie')
    assert len(scraper.errors) == 0
    assert len(scraper.recipes) == 1
    recipe = scraper.recipes[0]
    assert recipe.title == 'Soft Snickerdoodle Cookies'
    assert recipe.website == 'F'
    expected_ingredients = [[1, 'cup', 'unsalted butter'],
                            [1.5, 'cup', 'sugar'],
                            [2, 'whole', 'egg'],
                            [2.75, 'cup', 'flour'],
                            [2, 'tsp', 'cream of tartar'],
                            [1, 'tsp', 'baking soda'],
                            [0.25, 'tsp', 'salt'],
                            [3, 'tbsp', 'sugar'],
                            [3, 'tsp', 'cinnamon'],
                            [1, 'tsp', 'vanilla']]
    ingredients = recipe.ingredients
    for ingredient in ingredients:
        ingredient_list = [ingredient['amount'], ingredient['unit'], ingredient['name']]
        if ingredient_list in expected_ingredients:
            expected_ingredients.remove(ingredient_list)
        else:
            assert 0