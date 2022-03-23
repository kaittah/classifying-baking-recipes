from string import Template

from recipe_database.utils.connect import get_mongo_client
from recipe_database.utils.recipe_scraper import RecipeScraper

def scrape_sallys_baking_addiction(test_mode = False):
    if test_mode:
        sallys_baking_addition_scraper = RecipeScraper('SBA', 1, 1, False, False)
    else:
        sallys_baking_addition_scraper = RecipeScraper('SBA', 12, 12, False, False)

    sba_x_path_1 = Template('//*[@id="primary"]/div[4]/div/div[$i]/div[2]/a')
    sba_x_path_2 = Template('//*[@id="primary"]/div[3]/div/div[$i]/div[2]/a')
    sba_urls = [
                 ('bread', Template('https://sallysbakingaddiction.com/category/bread/page/$Number/#recipe-list-page'), sba_x_path_1),
                 ('cake', Template('https://sallysbakingaddiction.com/category/desserts/cakes/page/$Number/#recipe-list-page'), sba_x_path_1),
                 ('cookie', Template('https://sallysbakingaddiction.com/category/desserts/cookies/page/$Number/#recipe-list-page'), sba_x_path_1),
                 ('muffin', Template('https://sallysbakingaddiction.com/category/breakfast-treats/muffins/page/$Number/#recipe-list-page'), sba_x_path_2),
                 ('cupcake', Template('https://sallysbakingaddiction.com/category/desserts/cupcakes/page/$Number/#recipe-list-page'), sba_x_path_2)
                ]
    return sallys_baking_addition_scraper, sba_urls

def scrape_brown_eyed_baker_main(test_mode = False):
    if test_mode:
        brown_eyed_baker_scraper_1 = RecipeScraper('BEB', 1, 1, False, True)
    else:
        brown_eyed_baker_scraper_1 = RecipeScraper('BEB', 6, 24, False, True)
    beb_x_path_1 = Template('//*[@id="content2"]/div[1]/div[$i]/a')
    beb_urls_1 = [
        ('bread', Template('https://www.browneyedbaker.com/recipes/bread-recipes-2/page/$Number/'), beb_x_path_1),
        ('cake', Template('https://www.browneyedbaker.com/recipes/desserts/cake-recipes/page/$Number'), beb_x_path_1),
        ('cookie', Template('https://www.browneyedbaker.com/recipes/desserts/cookie-recipes/page/$Number'), beb_x_path_1),
        ('cupcake', Template('https://www.browneyedbaker.com/recipes/desserts/cupcake-recipes/page/$Number'), beb_x_path_1)
    ]
    return brown_eyed_baker_scraper_1, beb_urls_1

def scrape_brown_eyed_baker_search_results(test_mode = False):
    if test_mode:
        brown_eyed_baker_scraper_2 = RecipeScraper('BEB', 1, 1, False, True)
    else:
        brown_eyed_baker_scraper_2 = RecipeScraper('BEB', 1, 10, False, True)
    beb_x_path_2 = Template('//*[@id="content"]/div/article[$i]/a')
    beb_urls_2 = [('muffin', Template('https://www.browneyedbaker.com/?s=muffins'), beb_x_path_2)]
    return brown_eyed_baker_scraper_2, beb_urls_2

def scrape_food_dot_com(test_mode = False):
    if test_mode:
        food_scraper = RecipeScraper('F', 2, 5, True, False)
    else:
        food_scraper = RecipeScraper('F', 5, 24, True, False)
    food_x_path = Template('//*[@id="gk-menu-search"]/div[1]/div[2]/div/div/div[$i]/div/div[2]/div/h2/a')
    food_urls = [
        ('bread', Template('https://www.food.com/search/bread?pn=$Number'), food_x_path),
        ('cake', Template('https://www.food.com/search/cake?pn=$Number'), food_x_path),
        ('cookie', Template('https://www.food.com/search/cookies?pn=$Number'), food_x_path),
        ('cupcake', Template('https://www.food.com/search/cupcakes?pn=$Number'), food_x_path),
        ('muffin', Template('https://www.food.com/search/muffins?pn=$Number'), food_x_path),
        ('pancake', Template('https://www.food.com/search/pancakes?pn=$Number'), food_x_path)
    ]
    return food_scraper, food_urls
                                 
if __name__ == '__main__':
    for function in [scrape_food_dot_com]:
        scraper, base_urls = function()
        for category, url_template, x_path in base_urls:
            scraper.scrape_links_from_webpage(category, url_template, x_path)
        with open('app/recipe_database/utils/links.csv', 'a') as f:
            for link, category in scraper.urls:
                f.write(link + ',' + category + '\n')
        for link, category in scraper.urls:
            scraper.scrape_recipe(link, category)
        print('Errors', len(scraper.errors), 'Successes', len(scraper.recipes))
        client = get_mongo_client(streamlit=False)
        db = client.recipe_analysis
        for recipe in scraper.recipes:
            try:
                status, inserted_id, error = recipe.insert_into_mongo_db(db)
                print(status, error)
            except:
                print(recipe.title, recipe.url, 'Not Inserted into MongoDB')