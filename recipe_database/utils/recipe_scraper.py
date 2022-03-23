from recipe_scrapers import scrape_me
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
import time

from recipe_database.recipe_components.ingredient import Ingredient
from recipe_database.recipe_components.recipe import Recipe

class RecipeScraper():

    PATH = r"C:\Program Files (x86)\chromedriver.exe"

    def __init__(self, website_name, max_pages, links_per_page, add_page_to_count, wild_mode):
        '''
        website_name : abbreviated name for source
        max_pages: pages to iterate through to look for recipe links
        links_per_page: number of recipes to get from each page
        add_page_to_count: True if the link index will only ever increase (not reset to 1 in the x_path)
        wild_mode: True if not one of the established websites in scrape_me
        '''
        self.website_name = website_name
        self.max_pages = max_pages
        self.links_per_page = links_per_page
        self.add_page_to_count = add_page_to_count
        self.wild_mode = wild_mode
        self.errors = []
        self.recipes = []
        self.urls = []
    
    @staticmethod
    def get_chrome_driver(url):
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        driver = webdriver.Chrome(chrome_options=options, executable_path=RecipeScraper.PATH)
        try:
            driver.get(url)
            time.sleep(5)
        except TimeoutException:
            driver.get(url)
            time.sleep(5)
        return driver

    def scrape_recipe(self, recipe_link, category):
        '''
        Creates a Recipe object using ingredients scraped from the webpage specified by the recipe link
        '''
        try:
            scraper = scrape_me(recipe_link, wild_mode=self.wild_mode)
        except Exception as e:
            self.errors.append([str(e), recipe_link])
            return
        if scraper:
            try:
                title = scraper.title()
                ingredients = scraper.ingredients()
                butter_count = 0
                link_ingredients = []
                for ingredient in ingredients:
                    cleaned_ingredient = Ingredient(ingredient)
                    if cleaned_ingredient.name == 'unsalted butter':
                        #Remove ingredients used for cake frosting
                        if butter_count > 0:
                            previous_ingredient = link_ingredients[-1]
                            if previous_ingredient['name'] in ['cream cheese', 'sugar']:
                                link_ingredients.pop()
                            break
                        else:
                            butter_count += 1
                    link_ingredients.append(cleaned_ingredient.get_dictionary())
                recipe = Recipe(recipe_link, title, link_ingredients, category, self.website_name)
                self.recipes.append(recipe)
            except Exception as e:
                self.errors.append(str(e))

    def scrape_links_from_webpage(self, category, url_template, x_path):
        '''
        Pages through the website to find links of recipes
        Category is passed in to label the recipes, and is based on the section of the website the recipes come from
        '''
        if self.add_page_to_count:
            last_element = 1
            url = url_template.substitute(Number=1)
            webpage = RecipeScraper.get_chrome_driver(url)
            for page in range(1, self.max_pages + 1):
                counter = 0
                while counter < self.links_per_page:
                    webpage.execute_script("window.scrollTo(0,document.body.scrollHeight)")
                    time.sleep(3)
                    try:
                        recipe = webpage.find_element_by_xpath(
                                x_path.substitute(i=last_element+counter))
                        last_element += counter
                        recipe_link = recipe.get_attribute("href")
                        self.urls.append([recipe_link, category])
                    except Exception as e:
                        self.errors.append(str(e))
                    counter +=1

        else:
            for page in range(1, self.max_pages + 1):
                for i in range(1, self.links_per_page + 1):
                    url = url_template.substitute(Number=page)
                    webpage = RecipeScraper.get_chrome_driver(url)
                    try:
                        recipe = webpage.find_element_by_xpath(
                                x_path.substitute(i=i))
                    except Exception as e:
                        self.errors.append(str(e))
                        continue
                    recipe_link = recipe.get_attribute("href")
                    self.urls.append([recipe_link, category])